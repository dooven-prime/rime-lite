"""Paper-local source and implementation separation lint, not theorem validation."""

import ast
from pathlib import Path
import re
import sys

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from audit_scope import ARTIFACTS
from contract import require


def check_reader_surfaces(paper):
    require("## Computational Artifacts" in paper and "## Claim Status and Boundary" in paper,
            "reader artifact/claim entry missing")
    artifacts = paper.split("## Computational Artifacts", 1)[1].split("## Claim Status and Boundary", 1)[0]
    for token in ("bounded three-model replay", "partial Lean spine", "LOCAL_CLOSURE_VERIFICATION",
                  "not independent validation", "Neither the bounded replay nor the partial Lean spine is a machine proof",
                  "The development manifest alone is not a release identity"):
        require(token in " ".join(artifacts.split()), f"evidence boundary missing: {token}")
    require(not re.search(r"https://github\.com/dooven-prime/rime-lite/(?:blob|tree)/main(?:/|\b)", paper),
            "nonexistent main-branch source link")
    appendix = paper.split("## Appendix B:", 1)[1]
    require("`experiments/paper39/notes/`" in appendix,
            "supplement directory locator missing")
    for filename in ("ABSORPTION_CONSUMER_SPEC.md", "ABSORPTION_CONSUMER_ADEQUACY.md", "UFE_CORRESPONDENCE.md"):
        require(f"`{filename}`" in appendix and (ROOT / "experiments/paper39/notes" / filename).is_file(),
                f"supplement locator missing: {filename}")


def main():
    for _, relative in ARTIFACTS:
        path = ROOT / relative
        data = path.read_bytes()
        text = data.decode("utf-8")
        require(not any(ord(char) < 32 and char not in "\n\t" for char in text),
                f"control characters: {relative}")
        if path.suffix == ".py":
            syntax = ast.parse(text, filename=relative)
            require(not any(isinstance(node, ast.Assert) for node in ast.walk(syntax)),
                    f"optimization-sensitive assert: {relative}")
            modules = [node.module or "" for node in ast.walk(syntax) if isinstance(node, ast.ImportFrom)]
            modules += [alias.name for node in ast.walk(syntax) if isinstance(node, ast.Import)
                        for alias in node.names]
            require(not any("exploratory" in module or "synchronizing_automata" in module
                            for module in modules),
                    f"undeclared historical code dependency: {relative}")
    for filename, allowed in (
        ("log_consumer.py", {"dataclasses", "contract"}),
        ("forest.py", {"dataclasses", "contract"}),
        ("placed_ufe.py", {"dataclasses", "contract", "forest"}),
    ):
        syntax = ast.parse((PACKAGE / filename).read_text(encoding="utf-8"))
        imports = {node.module for node in ast.walk(syntax) if isinstance(node, ast.ImportFrom)}
        require(imports <= allowed and not any(isinstance(node, ast.Import) for node in ast.walk(syntax)),
                f"implementation separation drift: {filename}")
    paper = (ROOT / "papers/paper39/Paper XXXIX.md").read_text(encoding="utf-8")
    check_reader_surfaces(paper)
    require(paper.count("$$") % 2 == 0, "unbalanced display math")
    require(all(token in paper for token in ("Theorem 4.1", "Proposition 5.1", "Carry", "Absorb")),
            "owning theorem surface changed")
    require(not re.search(r"(?<![\\\w])(qquad|quad|left\(|right\))", paper), "bare TeX escape fragment")
    bibliography = (ROOT / "papers/paper39/references-v1.bib").read_text(encoding="utf-8")
    keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", bibliography))
    citations = set(re.findall(r"(?<![\w/])@([A-Za-z][A-Za-z0-9_:-]*)", paper))
    require(citations <= keys, f"missing bibliography keys: {sorted(citations - keys)}")
    print("PASS: local source lint and implementation separation; no proof certification")


if __name__ == "__main__":
    main()
