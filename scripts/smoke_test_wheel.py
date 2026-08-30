#!/usr/bin/env python3
"""
Prove an installed aicertify wheel produces real verdicts before it is published.

Run with the interpreter of a clean virtualenv that has the wheel installed and
nothing else from this repository:

    python -m venv /tmp/smoke
    /tmp/smoke/bin/pip install dist/aicertify-*.whl
    /tmp/smoke/bin/python scripts/smoke_test_wheel.py

Why this is not covered by the unit tests. The unit tests run against a source
checkout, where the .rego files and coverage.json are on disk whether or not
packaging includes them. A wheel that ships no policies passes every one of
them. It also passes at the CLI: `aicertify evaluate` prints "OPA Evaluation:
Successful" and exits 0 whether the run produced 29 verdicts or none, so no
exit code distinguishes a working release from an empty one.

Before v0.8.0, an EU AI Act evaluation reported 4 verdicts out of 29 and UK,
NIST, BFS, legal, healthcare and education evaluations reported none at all,
while the process exited successfully. This script asserts on the number of
verdicts, which is the only signal that separates those two outcomes.
"""

from __future__ import annotations

import json
import logging
import sys
from importlib import resources
from pathlib import Path

# The library logs at INFO through evaluation; the report below is the output.
logging.disable(logging.WARNING)

# Floors, not exact counts. See tests/test_framework_golden.py for the same
# table and the reasoning behind floors: the policy library is a submodule that
# is bumped deliberately, and a bump that adds a policy must not fail a release.
# A bump that removes verdicts must.
MINIMUM_VERDICTS = {
    "eu_ai_act": 25,
    "uk": 6,
    "nist": 5,
    "bfs": 4,
    "legal": 3,
    "global": 4,
    "healthcare": 2,
    "education": 4,
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    try:
        import aicertify
        from aicertify.opa_core.decision_index import load_index
        from aicertify.opa_core.evaluator import OpaEvaluator
        from aicertify.opa_core.extraction import (
            _package_values_from,
            extract_results_from_packages,
        )
    except Exception as exc:  # noqa: BLE001 - any import failure is a failed release
        fail(f"cannot import the installed package: {exc!r}")

    installed = Path(aicertify.__file__).resolve().parent
    print(f"aicertify {aicertify.__version__} from {installed}")

    # Importing from a source checkout would defeat the purpose: the files
    # under test would be the repository's, not the wheel's.
    if (installed.parent / "pyproject.toml").exists():
        fail(
            f"aicertify was imported from a source checkout at {installed.parent}, "
            "not from an installed wheel. Run this with a clean virtualenv."
        )

    with resources.as_file(
        resources.files("aicertify") / "_demo" / "sample_contract.json"
    ) as p:
        if not p.exists():
            fail("the wheel does not carry aicertify/_demo/sample_contract.json")
        contract = json.loads(p.read_text())

    evaluator = OpaEvaluator()
    evaluator.load_policies()
    policy_dir = evaluator.policy_loader.get_policy_dir()
    print(f"policy library: {policy_dir}")

    rego = list(Path(policy_dir).rglob("*.rego"))
    if len(rego) < 50:
        fail(f"only {len(rego)} .rego files in the installed policy directory")
    print(f"{len(rego)} .rego files present\n")

    index = load_index(policy_dir)

    print(f"{'framework':<12}{'declared':>9}{'delivered':>10}{'floor':>7}   result")
    failures = []
    for framework, floor in MINIMUM_VERDICTS.items():
        folders = evaluator.find_matching_policy_folders(framework)
        if not folders:
            failures.append(f"{framework}: no policy folder matches this name")
            print(f"{framework:<12}{'-':>9}{'-':>10}{floor:>7}   NO FOLDER")
            continue
        prefix = folders[0].split("opa_policies/")[-1].replace("/", ".")

        try:
            raw = evaluator.evaluate_by_folder_name(framework, contract)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{framework}: evaluation raised {exc!r}")
            print(f"{framework:<12}{'-':>9}{'-':>10}{floor:>7}   ERROR {exc!r}")
            continue

        if isinstance(raw, dict) and "error" in raw:
            failures.append(f"{framework}: {raw['error']}")
            print(f"{framework:<12}{'-':>9}{'-':>10}{floor:>7}   ERROR {raw['error']}")
            continue

        # What the library says should arrive, read from coverage.json rather
        # than from the packages that came back. A package that fails to
        # evaluate is absent from the results, so counting only what returned
        # compares a number with itself and always agrees.
        declared = {
            pkg
            for pkg, d in index.items()
            if pkg.startswith(prefix + ".") and d.reports_a_verdict
        }
        packages, _ = _package_values_from(raw)
        verdicts = extract_results_from_packages(packages, policy_dir)

        problems = []
        if len(declared) < floor:
            problems.append(
                f"only {len(declared)} policies declare a verdict, floor is {floor}"
            )
        if len(verdicts) != len(declared):
            silent = sorted(
                declared - {p for p in packages if p.startswith(prefix + ".")}
            )
            problems.append(
                f"{len(declared)} declared, {len(verdicts)} delivered; "
                f"silent packages: {silent or 'none'}"
            )
        for problem in problems:
            failures.append(f"{framework}: {problem}")
        status = "ok" if not problems else "FAIL"
        print(
            f"{framework:<12}{len(declared):>9}{len(verdicts):>10}{floor:>7}   {status}"
        )

    print()
    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        print(
            f"\n{len(failures)} framework(s) did not deliver verdicts from the installed wheel. "
            "Do not publish this build.",
            file=sys.stderr,
        )
        return 1

    print(
        f"All {len(MINIMUM_VERDICTS)} frameworks delivered every verdict they declare, "
        f"and each is above its floor."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
