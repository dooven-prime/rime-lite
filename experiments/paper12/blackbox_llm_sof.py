"""Paper XII diagnostic: black-box LLM observable-family audit.

Claim status:
    - Behavioral SOF diagnostic for API-only language models.
    - Uses prompt protocols and task classes as probe sectors.
    - Does not claim a strict projector-based SOF realization, access to model
      internals, or a universal hallucination detector.

The observable family is split into three registered classes:

    Structural: output presence, JSON/XML validity, schema consistency,
                valid tool-call emission
    Behavioral: task completion, instruction following, task-scoped
                groundedness, consistency, and appropriate tool use
    Failure:    refusal, grounded-answer failure, format collapse, and
                prompt-injection status when a corresponding probe exists

Schema, few-shot, and tool repair are report transitions, not a fourth
observable family.

The default fixture mode is deterministic and offline. API mode targets an
OpenAI-compatible ``/chat/completions`` endpoint and reads credentials only
from environment variables.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODELS = ["fixture-strict", "fixture-chatty", "fixture-fragile"]
MIN_API_SUCCESS_RATE = 80.0


@dataclass(frozen=True)
class Task:
    name: str
    query: str
    expected: str
    task_class: str
    context: str = ""
    requires_tool: bool = False


@dataclass(frozen=True)
class Protocol:
    name: str
    system: str = ""
    output_format: str = "text"
    few_shot: bool = False
    tools_enabled: bool = False


@dataclass
class Response:
    text: str = ""
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    latency_ms: float = 0.0
    error: str = ""


@dataclass
class Record:
    model: str
    task: Task
    protocol: Protocol
    response: Response
    observables: dict[str, dict[str, bool | None]]


TASKS = [
    Task(
        name="arithmetic",
        query="What is 2 + 2?",
        expected="4",
        task_class="closed_answer",
    ),
    Task(
        name="grounded_deadline",
        query="According to the context, what is the Project Atlas deadline?",
        context="Project Atlas has one stated deadline: Tuesday.",
        expected="tuesday",
        task_class="grounded_qa",
    ),
    Task(
        name="weather_tool",
        query="Use the weather tool to obtain the weather in Paris.",
        expected="get_weather",
        task_class="tool_use",
        requires_tool=True,
    ),
]


PROTOCOLS = [
    Protocol(name="bare"),
    Protocol(
        name="concise",
        system="Answer correctly and concisely. Do not add unsupported claims.",
    ),
    Protocol(
        name="json_schema",
        system='Return only JSON matching {"result": <string>}.',
        output_format="json",
    ),
    Protocol(
        name="xml_schema",
        system="Return only XML of the form <response><result>...</result></response>.",
        output_format="xml",
    ),
    Protocol(
        name="few_shot",
        system="Follow the demonstrated answer pattern exactly.",
        few_shot=True,
    ),
    Protocol(
        name="tool_enabled",
        system="Use the supplied tool when the task requests external data.",
        tools_enabled=True,
    ),
]


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Return weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
                "additionalProperties": False,
            },
        },
    }
]


def messages_for(task: Task, protocol: Protocol) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    if protocol.system:
        messages.append({"role": "system", "content": protocol.system})
    if protocol.few_shot:
        messages.extend(
            [
                {"role": "user", "content": "What is 1 + 1?"},
                {"role": "assistant", "content": "2"},
            ]
        )
    content = task.query
    if task.context:
        content = f"Context: {task.context}\n\nQuestion: {task.query}"
    messages.append({"role": "user", "content": content})
    return messages


def fixture_response(model: str, task: Task, protocol: Protocol) -> Response:
    """Deterministic synthetic controls for offline report verification."""
    start = time.perf_counter()
    strict = model == "fixture-strict"
    chatty = model == "fixture-chatty"
    fragile = model == "fixture-fragile"

    if task.requires_tool and protocol.tools_enabled:
        result = Response(
            text="",
            tool_calls=[{"name": "get_weather", "arguments": {"city": "Paris"}}],
        )
    elif task.name == "arithmetic":
        answer = "5" if fragile and protocol.name == "bare" else "4"
        if protocol.output_format == "json":
            result = Response(text=json.dumps({"result": answer}))
        elif protocol.output_format == "xml":
            result = Response(text=f"<response><result>{answer}</result></response>")
        elif chatty and protocol.name == "bare":
            result = Response(text=f"The answer is {answer}, because addition combines the values.")
        else:
            result = Response(text=answer)
    elif task.name == "grounded_deadline":
        answer = "Wednesday" if fragile and protocol.name == "bare" else "Tuesday"
        if protocol.output_format == "json":
            result = Response(text=json.dumps({"result": answer}))
        elif protocol.output_format == "xml":
            result = Response(text=f"<response><result>{answer}</result></response>")
        elif chatty and protocol.name == "bare":
            result = Response(text=f"The deadline is {answer}. No other date is stated.")
        else:
            result = Response(text=answer)
    elif task.requires_tool:
        result = Response(text="I cannot access live weather data." if strict else "The weather is sunny.")
    else:  # pragma: no cover - TASKS is fixed above
        result = Response(error="unknown fixture task")

    result.latency_ms = (time.perf_counter() - start) * 1000.0
    return result


def api_response(
    model: str,
    task: Task,
    protocol: Protocol,
    endpoint: str,
    api_key: str,
    timeout: float,
) -> Response:
    body: dict[str, Any] = {
        "model": model,
        "messages": messages_for(task, protocol),
        "temperature": 0,
        "max_tokens": 160,
    }
    if protocol.tools_enabled:
        body["tools"] = TOOLS
        body["tool_choice"] = "auto"

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        message = payload["choices"][0]["message"]
        tool_calls = []
        for call in message.get("tool_calls") or []:
            function = call.get("function", {})
            arguments = function.get("arguments", "{}")
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                pass
            tool_calls.append({"name": function.get("name", ""), "arguments": arguments})
        return Response(
            text=(message.get("content") or "").strip(),
            tool_calls=tool_calls,
            latency_ms=(time.perf_counter() - start) * 1000.0,
        )
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError) as exc:
        return Response(
            latency_ms=(time.perf_counter() - start) * 1000.0,
            error=f"{type(exc).__name__}: {exc}",
        )


def parsed_json(text: str) -> Any | None:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def parsed_xml(text: str) -> ET.Element | None:
    try:
        return ET.fromstring(text)
    except (ET.ParseError, TypeError):
        return None


def normalized_answer(response: Response) -> str:
    if response.tool_calls:
        return response.tool_calls[0].get("name", "").lower()
    obj = parsed_json(response.text)
    if isinstance(obj, dict) and "result" in obj:
        return str(obj["result"]).strip().lower()
    root = parsed_xml(response.text)
    if root is not None:
        result = root.find("result")
        if result is not None and result.text:
            return result.text.strip().lower()
    return re.sub(r"\s+", " ", response.text.strip().lower())


def contains_expected(task: Task, response: Response) -> bool:
    answer = normalized_answer(response)
    if task.requires_tool:
        return answer == task.expected.lower()
    if task.name == "arithmetic":
        return bool(re.search(r"(?<!\d)4(?!\d)", answer))
    return task.expected.lower() in answer


def grounded(task: Task, response: Response) -> bool | None:
    if task.task_class != "grounded_qa":
        return None
    answer = normalized_answer(response)
    weekdays = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
    mentioned = {day for day in weekdays if day in answer}
    return task.expected.lower() in answer and mentioned <= {task.expected.lower()}


def valid_weather_tool_call(response: Response, expected_city: str = "") -> bool:
    for call in response.tool_calls:
        if call.get("name") != "get_weather":
            continue
        arguments = call.get("arguments")
        if not isinstance(arguments, dict):
            continue
        city = str(arguments.get("city", "")).strip()
        if city and (not expected_city or city.casefold() == expected_city.casefold()):
            return True
    return False


def instruction_following(task: Task, protocol: Protocol, response: Response) -> bool:
    if response.error:
        return False
    if protocol.output_format == "json":
        obj = parsed_json(response.text)
        return isinstance(obj, dict) and set(obj) == {"result"}
    if protocol.output_format == "xml":
        root = parsed_xml(response.text)
        return root is not None and root.tag == "response" and root.find("result") is not None
    if protocol.tools_enabled:
        if task.requires_tool:
            return valid_weather_tool_call(response, "Paris")
        if response.tool_calls:
            return False
    return bool(response.text.strip()) or bool(response.tool_calls)


def evaluate(
    task: Task,
    protocol: Protocol,
    response: Response,
) -> dict[str, dict[str, bool | None]]:
    obj = parsed_json(response.text)
    root = parsed_xml(response.text)
    tool_call = valid_weather_tool_call(response, "Paris") if task.requires_tool else False
    any_tool_call = bool(response.tool_calls)
    answer_correct = contains_expected(task, response)
    follows = instruction_following(task, protocol, response)
    appropriate_tool = tool_call if task.requires_tool else not any_tool_call
    lower_text = response.text.lower()
    refusal = any(
        marker in lower_text
        for marker in (
            "cannot",
            "can't",
            "unable to",
            "don't have direct access",
            "do not have direct access",
            "don't have the capability",
            "not aware of any specific",
        )
    )
    grounded_value = grounded(task, response)
    format_collapse = None
    if protocol.output_format in {"json", "xml"}:
        format_collapse = not follows

    return {
        "structural": {
            "nonempty": bool(response.text.strip()) or bool(response.tool_calls),
            "json_valid": obj is not None if protocol.output_format == "json" else None,
            "xml_valid": root is not None if protocol.output_format == "xml" else None,
            "schema_consistent": (
                follows if protocol.output_format in {"json", "xml"} else None
            ),
            "tool_call_valid": tool_call if task.requires_tool else None,
        },
        "behavioral": {
            "task_completion": answer_correct,
            "instruction_following": follows,
            "task_scoped_groundedness": grounded_value,
            "cross_protocol_consistency": True,
            "api_success": not response.error,
            "concise": len(response.text) <= 240,
            "latency_recorded": response.latency_ms >= 0.0,
            "appropriate_tool_use": appropriate_tool,
        },
        "failure": {
            "refusal": refusal,
            "grounded_answer_failure": None if grounded_value is None else not grounded_value,
            "format_collapse": format_collapse,
            "prompt_injection_failure": None,
        },
    }


def run_audit(
    models: list[str],
    mode: str,
    endpoint: str,
    api_key: str,
    timeout: float,
) -> list[Record]:
    records: list[Record] = []
    for model in models:
        for task in TASKS:
            for protocol in PROTOCOLS:
                if mode == "fixture":
                    response = fixture_response(model, task, protocol)
                else:
                    response = api_response(model, task, protocol, endpoint, api_key, timeout)
                records.append(
                    Record(
                        model=model,
                        task=task,
                        protocol=protocol,
                        response=response,
                        observables=evaluate(task, protocol, response),
                    )
                )
    for model in models:
        for task in TASKS:
            group = [
                record
                for record in records
                if record.model == model and record.task.name == task.name
            ]
            answers = [normalized_answer(record.response) for record in group]
            nonempty = [answer for answer in answers if answer]
            majority = max(set(nonempty), key=nonempty.count) if nonempty else ""
            for record, answer in zip(group, answers):
                record.observables["behavioral"]["cross_protocol_consistency"] = (
                    bool(answer) and answer == majority
                )
    return records


def observable_rate(
    records: list[Record], family: str, observable: str
) -> float | None:
    values = [
        record.observables[family][observable]
        for record in records
        if record.observables[family][observable] is not None
    ]
    return 100.0 * sum(values) / len(values) if values else None


def pass_rate(records: list[Record], family: str, observable: str) -> float:
    rate = observable_rate(records, family, observable)
    return rate if rate is not None else 0.0


def records_for(records: list[Record], model: str, protocol: str) -> list[Record]:
    return [record for record in records if record.model == model and record.protocol.name == protocol]


def repair_summary(records: list[Record], model: str) -> dict[str, int]:
    by_key = {(record.task.name, record.protocol.name): record for record in records if record.model == model}

    def repaired(task_name: str, before: str, after: str, family: str, observable: str) -> bool:
        left = by_key[(task_name, before)].observables[family][observable]
        right = by_key[(task_name, after)].observables[family][observable]
        return not left and right

    return {
        "schema_repair": sum(
            repaired(task.name, "bare", "json_schema", "structural", "schema_consistent")
            for task in TASKS
        ),
        "few_shot_repair": sum(
            repaired(task.name, "bare", "few_shot", "behavioral", "task_completion")
            for task in TASKS
        ),
        "tool_repair": int(
            repaired("weather_tool", "bare", "tool_enabled", "structural", "tool_call_valid")
        ),
    }


def model_claim_status(records: list[Record], model: str, mode: str) -> dict[str, str]:
    if mode == "fixture":
        return {
            "status": "negative_control",
            "note": "deterministic synthetic control",
        }
    subset = [record for record in records if record.model == model]
    success_rate = observable_rate(subset, "behavioral", "api_success")
    if success_rate is None or success_rate < MIN_API_SUCCESS_RATE:
        return {
            "status": "failure",
            "note": "provider infrastructure failures dominate the API audit",
        }
    return {
        "status": "diagnostic",
        "note": "real API behavioral diagnostic",
    }


def report_dict(
    records: list[Record],
    mode: str,
    provider: str = "",
    endpoint: str = "",
) -> dict[str, Any]:
    models = sorted({record.model for record in records})
    observable_families = {
        family: list(next(iter(records)).observables[family])
        for family in ("structural", "behavioral", "failure")
    }
    support_matrix = {
        model: {
            protocol.name: {
                f"{family}.{name}": observable_rate(
                    records_for(records, model, protocol.name), family, name
                )
                for family in ("structural", "behavioral", "failure")
                for name in observable_families[family]
            }
            for protocol in PROTOCOLS
        }
        for model in models
    }
    repair_matrix = {model: repair_summary(records, model) for model in models}
    model_statuses = {
        model: model_claim_status(records, model, mode) for model in models
    }
    infrastructure_limited = any(
        status["status"] == "failure" for status in model_statuses.values()
    )
    provider_name = provider or ("fixture" if mode == "fixture" else "unspecified")
    system_name = f"{provider_name} behavioral API audit: {', '.join(models)}"
    return {
        "report_type": "api_level_sof_report",
        "diagnostic_regime": "behavioral_black_box",
        "sofrs_version": "1.0",
        "report_id": "api_llm_" + "_".join(
            model.replace("/", "_").replace(".", "_") for model in models
        ),
        "system": system_name,
        "mode": mode,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider": provider_name,
        "endpoint": endpoint if mode == "api" else "offline_fixture",
        "model_ids": models,
        "claim_status": (
            "failure"
            if infrastructure_limited
            else ("negative_control" if mode == "fixture" else "diagnostic")
        ),
        "claim_note": (
            "provider infrastructure failures dominate the API audit"
            if infrastructure_limited
            else (
                "deterministic synthetic control"
                if mode == "fixture"
                else "real API behavioral diagnostic"
            )
        ),
        "strict_sof_realization": False,
        "provenance": {
            "source_identity": {
                "provider": provider_name,
                "endpoint": endpoint if mode == "api" else "offline_fixture",
                "model_ids": models,
            },
            "evaluator": "experiments/paper12/blackbox_llm_sof.py",
            "evaluator_protocol": {
                "tasks": [task.name for task in TASKS],
                "protocols": [protocol.name for protocol in PROTOCOLS],
                "observable_classes": ["structural", "behavioral", "failure"],
            },
            "evaluator_scope": (
                "deterministic task-scoped rules over three registered tasks and six prompt protocols"
            ),
        },
        "sectorization": {
            "type": "probe sectors",
            "protocols": [protocol.name for protocol in PROTOCOLS],
            "task_classes": sorted({task.task_class for task in TASKS}),
        },
        "observable_family": observable_families,
        "support_matrix": support_matrix,
        "bridge_matrix": {
            "status": "behavioral_analogue",
            "claim_note": "protocol transitions, not algebraic or commutator bridges",
            "transitions": {
                "schema_bridge": {
                    "from": "bare",
                    "to": "json_schema",
                    "observable": "structural.schema_consistent",
                },
                "few_shot_bridge": {
                    "from": "bare",
                    "to": "few_shot",
                    "observable": "behavioral.task_completion",
                },
                "tool_bridge": {
                    "from": "bare",
                    "to": "tool_enabled",
                    "observable": "structural.tool_call_valid",
                },
            },
        },
        "repair_matrix": repair_matrix,
        "wall_record": {
            "status": "not_computed",
            "reason": "behavioral walls require an explicit parameterized probe path",
            "trajectory_summary": {
                "status": "discrete_protocol_comparison",
                "protocols": [protocol.name for protocol in PROTOCOLS],
            },
        },
        "failure_modes": [
            "probe sectors are not projector-valued sectors",
            "no access to weights, activations, or hidden mechanisms",
            "behavioral and failure observables are evaluator- and task-scoped",
            "API model versions and backend behavior may drift",
            "provider rate limits or routing failures can make the audit inconclusive",
            "protocol repair is not Lie-depth D-repair",
        ],
        "models": {
            model: {
                family: {
                    name: observable_rate(
                        [record for record in records if record.model == model],
                        family,
                        name,
                    )
                    for name in observable_families[family]
                }
                for family in ("structural", "behavioral", "failure")
            }
            | {
                "repair_matrix": repair_matrix[model],
                "claim_status": model_statuses[model]["status"],
                "claim_note": model_statuses[model]["note"],
                "strict_sof_realization": False,
            }
            for model in models
        },
        "records": [
            {
                "model": record.model,
                "task": record.task.name,
                "task_class": record.task.task_class,
                "protocol": record.protocol.name,
                "text": record.response.text,
                "tool_calls": record.response.tool_calls,
                "latency_ms": round(record.response.latency_ms, 3),
                "error": record.response.error,
                "observables": record.observables,
            }
            for record in records
        ],
    }


def records_from_report(path: Path) -> tuple[dict[str, Any], list[Record]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    tasks = {task.name: task for task in TASKS}
    protocols = {protocol.name: protocol for protocol in PROTOCOLS}
    records = []
    for item in payload.get("records", []):
        task = tasks[item["task"]]
        protocol = protocols[item["protocol"]]
        response = Response(
            text=item.get("text", ""),
            tool_calls=item.get("tool_calls", []),
            latency_ms=float(item.get("latency_ms", 0.0)),
            error=item.get("error", ""),
        )
        records.append(
            Record(
                model=item["model"],
                task=task,
                protocol=protocol,
                response=response,
                observables=evaluate(task, protocol, response),
            )
        )

    # Cross-protocol consistency depends on the full task/protocol group.
    for model in sorted({record.model for record in records}):
        for task in TASKS:
            group = [
                record
                for record in records
                if record.model == model and record.task.name == task.name
            ]
            answers = [normalized_answer(record.response) for record in group]
            nonempty = [answer for answer in answers if answer]
            majority = max(set(nonempty), key=nonempty.count) if nonempty else ""
            for record, answer in zip(group, answers):
                record.observables["behavioral"]["cross_protocol_consistency"] = (
                    bool(answer) and answer == majority
                )
    return payload, records


def print_report(records: list[Record], mode: str, provider: str = "") -> None:
    models = sorted({record.model for record in records})
    print("=" * 96)
    print("  Paper XII: API-Only LLM / API-Level SOF Report")
    print("=" * 96)
    print(f"  Mode: {mode}")
    print(f"  Provider: {provider or ('fixture' if mode == 'fixture' else 'unspecified')}")
    print("  Sectorization proposal: prompt protocols x task classes (probe sectors)")
    print("  Strict SOF realization: no - black-box behavioral comparison only")
    print()
    print("  Observable Family")
    print("    Structural: JSON/XML validity, schema consistency, valid tool-call emission")
    print("    Behavioral: task completion, instruction following, groundedness, consistency")
    print("    Failure: refusal, grounded-answer failure, format collapse, prompt injection")
    print("    Repair Matrix: schema repair, few-shot repair, tool repair")

    for model in models:
        subset = [record for record in records if record.model == model]
        repair = repair_summary(records, model)
        print()
        print(f"  --- {model} ---")
        for family in ("structural", "behavioral", "failure"):
            names = list(subset[0].observables[family])
            values = []
            for name in names:
                rate = observable_rate(subset, family, name)
                value = "not measured" if rate is None else f"{rate:.1f}%"
                values.append(f"{name}={value}")
            print(f"    {family:<10s} {', '.join(values)}")
        print(
            "    repair   "
            f"schema={repair['schema_repair']}, "
            f"few_shot={repair['few_shot_repair']}, "
            f"tool={repair['tool_repair']}"
        )
        print("    protocol matrix (% passing over tasks):")
        print(
            f"      {'protocol':<15s} {'json':>6s} {'xml':>6s} {'schema':>8s} "
            f"{'correct':>8s} {'follow':>8s} {'ground':>8s} {'tool':>6s}"
        )
        for protocol in PROTOCOLS:
            rows = records_for(records, model, protocol.name)
            print(
                f"      {protocol.name:<15s} "
                f"{pass_rate(rows, 'structural', 'json_valid'):>5.1f}% "
                f"{pass_rate(rows, 'structural', 'xml_valid'):>5.1f}% "
                f"{pass_rate(rows, 'structural', 'schema_consistent'):>7.1f}% "
                f"{pass_rate(rows, 'behavioral', 'task_completion'):>7.1f}% "
                f"{pass_rate(rows, 'behavioral', 'instruction_following'):>7.1f}% "
                f"{pass_rate(rows, 'behavioral', 'task_scoped_groundedness'):>7.1f}% "
                f"{pass_rate(rows, 'structural', 'tool_call_valid'):>5.1f}%"
            )

    print()
    print("  Claim Status")
    if mode == "fixture":
        print("    deterministic synthetic control; validates the report contract")
    else:
        for model in models:
            status = model_claim_status(records, model, mode)
            print(f"    {model}: {status['status']} - {status['note']}")
        print("    no claim about internal mechanisms")
    print("    groundedness is task-scoped, not a universal hallucination detector")
    print("    repair transitions are protocol-level, not Lie-depth D-repair")


def validate_fixture(records: list[Record]) -> None:
    by_model = {model: repair_summary(records, model) for model in DEFAULT_MODELS}
    assert by_model["fixture-fragile"]["few_shot_repair"] >= 1
    assert all(summary["schema_repair"] >= 1 for summary in by_model.values())
    assert all(summary["tool_repair"] == 1 for summary in by_model.values())
    assert not any(record.response.error for record in records)
    report = report_dict(records, "fixture")
    required = {
        "sofrs_version",
        "sectorization",
        "observable_family",
        "support_matrix",
        "bridge_matrix",
        "repair_matrix",
        "wall_record",
        "claim_status",
        "failure_modes",
    }
    assert required <= report.keys()
    assert report["sofrs_version"] == "1.0"
    assert report["claim_status"] == "negative_control"
    assert report["strict_sof_realization"] is False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("fixture", "api"), default="fixture")
    parser.add_argument(
        "--models",
        default="",
        help=(
            "Comma-separated model identifiers. Fixture mode uses built-in controls; "
            "API mode can also read BLACKBOX_LLM_MODELS."
        ),
    )
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("BLACKBOX_LLM_API_URL", DEFAULT_ENDPOINT),
        help="OpenAI-compatible chat-completions endpoint.",
    )
    parser.add_argument(
        "--api-key-env",
        default="BLACKBOX_LLM_API_KEY",
        help="Environment variable containing the API key.",
    )
    parser.add_argument("--timeout", type=float, default=45.0)
    parser.add_argument(
        "--provider",
        default=os.environ.get("BLACKBOX_LLM_PROVIDER", ""),
        help="Provider label stored in API-level report provenance.",
    )
    parser.add_argument("--output", type=Path, help="Optional .sofreport output path.")
    parser.add_argument(
        "--reevaluate",
        type=Path,
        help="Recompute observables from a saved report without making API calls.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.reevaluate:
        source, records = records_from_report(args.reevaluate)
        mode = source.get("mode", "api")
        provider = source.get("provider", args.provider)
        endpoint = source.get("endpoint", args.endpoint)
        print_report(records, mode, provider)
        output = args.output or args.reevaluate
        report = report_dict(records, mode, provider, endpoint)
        report["responses_generated_at_utc"] = source.get(
            "responses_generated_at_utc", source.get("generated_at_utc", "")
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n  Re-evaluated report: {output}")
        return

    model_text = args.models
    if not model_text:
        model_text = (
            ",".join(DEFAULT_MODELS)
            if args.mode == "fixture"
            else os.environ.get("BLACKBOX_LLM_MODELS", "")
        )
    models = [model.strip() for model in model_text.split(",") if model.strip()]
    if not models:
        raise SystemExit(
            "At least one model is required via --models or BLACKBOX_LLM_MODELS."
        )

    api_key = os.environ.get(args.api_key_env, "")
    if args.mode == "api" and not api_key:
        raise SystemExit(f"API mode requires environment variable {args.api_key_env}.")

    records = run_audit(models, args.mode, args.endpoint, api_key, args.timeout)
    if args.mode == "fixture" and models == DEFAULT_MODELS:
        validate_fixture(records)
    print_report(records, args.mode, args.provider)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(
                report_dict(records, args.mode, args.provider, args.endpoint),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        print(f"\n  JSON report: {args.output}")


if __name__ == "__main__":
    main()
