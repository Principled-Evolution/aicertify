#!/usr/bin/env python
"""Evaluate a contract in CI and turn the verdict into an exit code.

Copy this next to the workflow in your own repository. It is a script rather
than an inline ``run:`` block so you can run exactly what CI runs before you
push.

    python gate.py --contract contract.json --policy eu_ai_act --fail-on any

Exit codes, kept distinct on purpose:

    0  every policy passed, or --fail-on none
    1  at least one policy denied and --fail-on any
    2  the evaluation could not be carried out

The 2 matters. A run that failed to produce verdicts has told you nothing, and
folding it into "not a failure" is how a compliance pipeline reports green while
checking nothing. Producing no policy results at all is treated the same way,
because an empty result list is indistinguishable from a silent extraction
failure.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any, Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, help="Path to the contract JSON")
    parser.add_argument(
        "--policy",
        required=True,
        help="Framework to evaluate against, e.g. eu_ai_act, uk, bfs",
    )
    parser.add_argument(
        "--fail-on",
        choices=("any", "none"),
        default="any",
        help=(
            "any: exit 1 if a policy denies (use this once your contract is "
            "populated). none: report only, always exit 0 unless the run itself "
            "failed. Start on none, switch to any when the report is clean."
        ),
    )
    parser.add_argument(
        "--report-format",
        default="markdown",
        help="Report format to generate (default: markdown)",
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Where to write the report (default: reports)",
    )
    parser.add_argument(
        "--summary-json",
        default="compliance-summary.json",
        help="Machine-readable verdict summary to write (default: compliance-summary.json)",
    )
    return parser.parse_args()


def annotate(level: str, message: str) -> None:
    """Emit a GitHub Actions annotation, or a plain line when run locally."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::{level}::{message}")
    else:
        print(f"{level.upper()}: {message}")


def write_step_summary(lines: List[str]) -> None:
    """Append to the job summary so the verdict is visible without the log."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
    except OSError:
        pass  # A missing summary file must never fail the gate.


async def run(args: argparse.Namespace) -> Dict[str, Any]:
    from aicertify.api import aicertify_app_for_policy, load_contract

    contract = load_contract(args.contract)
    os.makedirs(args.output_dir, exist_ok=True)
    return await aicertify_app_for_policy(
        contract=contract,
        policy_folder=args.policy,
        output_dir=args.output_dir,
        report_format=args.report_format,
    )


def main() -> int:
    args = parse_args()

    if not os.path.isfile(args.contract):
        annotate("error", f"Contract not found: {args.contract}")
        return 2

    try:
        results = asyncio.run(run(args))
    except Exception as exc:  # noqa: BLE001 - any failure here means "no verdict"
        annotate("error", f"Evaluation did not complete: {exc}")
        return 2

    opa_results = results.get("opa_results") or {}
    if isinstance(opa_results, dict) and "error" in opa_results:
        annotate("error", f"OPA evaluation failed: {opa_results['error']}")
        return 2

    from aicertify.opa_core.extraction import extract_all_policy_results

    policy_results = extract_all_policy_results(opa_results)

    if not policy_results:
        annotate(
            "error",
            "The evaluation produced no policy verdicts. This is treated as a "
            "failure rather than a pass, because an empty result set is "
            "indistinguishable from an extraction failure. Run "
            f"`aicertify explain {args.policy}` to check the contract carries "
            "the fields these policies read.",
        )
        return 2

    passed = [p for p in policy_results if p.result]
    failed = [p for p in policy_results if not p.result]

    print(f"\n{len(policy_results)} policies evaluated against {args.policy}")
    print(f"  passed: {len(passed)}")
    print(f"  failed: {len(failed)}\n")
    for policy in sorted(policy_results, key=lambda p: (p.result, p.name)):
        print(f"  {'PASS' if policy.result else 'FAIL'}  {policy.name}")

    summary = {
        "framework": args.policy,
        "contract": args.contract,
        "total": len(policy_results),
        "passed": len(passed),
        "failed": len(failed),
        "policies": [
            {"name": p.name, "passed": bool(p.result)} for p in policy_results
        ],
        "report_path": results.get("report_path"),
    }
    try:
        with open(args.summary_json, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)
        print(f"\nWrote {args.summary_json}")
    except OSError as exc:
        annotate("warning", f"Could not write {args.summary_json}: {exc}")

    md = [
        f"### AI compliance: {args.policy}",
        "",
        f"**{len(passed)} of {len(policy_results)} policies passed.**",
        "",
        "| Policy | Verdict |",
        "| --- | --- |",
    ]
    md += [
        f"| {p.name} | {'pass' if p.result else 'fail'} |"
        for p in sorted(policy_results, key=lambda p: (p.result, p.name))
    ]
    write_step_summary(md)

    if failed and args.fail_on == "any":
        for policy in failed:
            annotate("error", f"Policy denied: {policy.name}")
        annotate(
            "error",
            f"{len(failed)} of {len(policy_results)} policies denied. "
            "See the uploaded report for the reasons and recommendations.",
        )
        return 1

    if failed:
        annotate(
            "warning",
            f"{len(failed)} of {len(policy_results)} policies denied, but "
            "--fail-on none was set, so the build is not being failed.",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
