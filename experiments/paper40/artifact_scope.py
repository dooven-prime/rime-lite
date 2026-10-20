"""Fixed source inventory and bounded replay scope for Paper XL."""

SOURCE_COMMIT = "b032b47ec47f28c8b2f65844abbe30dc3b38fef8"
RUNTIME_COMMIT = "a4b3e48bd119908494c6d4de8619bffc01c1ecb9"
UPSTREAM = {
    "contract.py": "001ce3824a4cde7c2e1e37ba1cebabbdeed49e1e3b57d5664dcdf609d3e909a1",
    "log_consumer.py": "f0c6786ecdfbd54209487db725340469c4816cae574e55b966d7323955dd2640",
    "forest.py": "ab2d6913f29bb4008f80d9f6d48db7e5b246fe75382ef0b2df2b2f2639d66336",
}
RUNTIME_FILES = {
    "README.md": "SNAPSHOT_README.md", "APPLICATION_README.md": "README.md",
    "Q2_LANGUAGE.md": "Q2_LANGUAGE.md", "q2_cli.py": "q2_cli.py",
    "q2_examples.py": "q2_examples.py", "fixed_controls.py": "fixed_controls.py",
    "test_fixed_controls.py": "test_fixed_controls.py", "test_q2.py": "test_q2.py",
    "run_evidence.py": "run_evidence.py",
    "examples/origin_read_failure.json": "examples/origin_read_failure.json",
    **{f"q2/{name}.py": f"q2/{name}.py" for name in
       ("__init__", "common", "engine", "model", "replay", "request", "syntax", "values")},
}
SNAPSHOT_FILES = frozenset({*RUNTIME_FILES, "LICENSE", "frozen/paper39/LICENSE",
                           *("frozen/paper39/" + name for name in UPSTREAM)})
EXPECTED_CONTROLS = {
    "gamma_n2": "PASS_EXACT", "gamma_n3": "PASS_EXACT", "gamma_n4": "PASS_EXACT",
    "forget_ports": "FAIL_READ", "forget_origin": "FAIL_READ",
    "forget_partition": "FAIL_GUARD", "parity_only": "FAIL_SUCCESSOR",
    "packet_only": "PASS_EXACT", "count_state": "PASS_EXACT",
}
EXPECTED_DOMAINS = {2: (6, 4), 3: (39, 18), 4: (292, 72)}

ARTIFACTS = (
    "papers/paper40/Paper XL.md",
    "papers/paper40/references-v1.bib", "experiments/paper40/README.md",
    "experiments/paper40/artifact_scope.py", "experiments/paper40/build_snapshot.py",
    "experiments/paper40/freeze_closure.py", "experiments/paper40/validation/validate_package.py",
    "experiments/paper40/validation/test_package.py", "experiments/paper40/source/q2-source-v1.zip",
    "experiments/paper40/source/snapshot.v1.json", "experiments/paper40/results/q2-controls.v1.json",
    "experiments/paper40/environment.v1.json",
)

RELEASE_FILES = frozenset({
    "papers/paper40/paper40_arxiv.pdf",
    "experiments/paper40/release-environment.json",
    "experiments/paper40/release-manifest.json",
    "experiments/paper40/validation/validate_release.py",
    "experiments/paper40/results/paper40_public_package_v1.validation-receipt.json",
})


def require(condition, message):
    if not condition:
        raise ValueError(message)
