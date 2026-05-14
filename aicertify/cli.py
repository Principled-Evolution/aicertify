#!/usr/bin/env python
"""AICertify command-line interface.

Two subcommands:

* ``aicertify demo`` — loads a bundled sample contract, runs an OPA evaluation
  against the EU AI Act policy set, and writes a Markdown report to the
  current directory. No contract file or API keys required.

* ``aicertify evaluate`` — evaluates a user-provided contract JSON against a
  user-provided policy folder. Equivalent to the legacy flat invocation.

For backwards compatibility, ``aicertify --contract X --policy Y`` (no
subcommand) is treated as ``aicertify evaluate --contract X --policy Y``.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, Optional

logger = logging.getLogger("aicertify.cli")


async def _run_evaluate(
    contract_path: str,
    policy_folder: str,
    output_dir: Optional[str] = None,
    report_format: str = "pdf",
    evaluators: Optional[list] = None,
    custom_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run a contract evaluation using the existing API."""
    from aicertify.api import aicertify_app_for_policy, load_contract

    logger.info(f"Loading contract from {contract_path}")
    contract = load_contract(contract_path)
    logger.info(
        f"Loaded contract for application: {contract.application_name} "
        f"({len(contract.interactions)} interactions)"
    )

    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "reports")
    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"Running evaluation with policy folder: {policy_folder}")
    return await aicertify_app_for_policy(
        contract=contract,
        policy_folder=policy_folder,
        output_dir=output_dir,
        report_format=report_format,
        custom_params=custom_params,
    )


def _cmd_evaluate(args: argparse.Namespace) -> int:
    """Handle the ``evaluate`` subcommand."""
    custom_params = None
    if args.params:
        try:
            if os.path.isfile(args.params):
                with open(args.params, "r") as f:
                    custom_params = json.load(f)
            else:
                custom_params = json.loads(args.params)
        except Exception as exc:
            logger.error(f"Error parsing --params: {exc}")
            return 2

    try:
        results = asyncio.run(
            _run_evaluate(
                contract_path=args.contract,
                policy_folder=args.policy,
                output_dir=args.output_dir,
                report_format=args.report_format,
                evaluators=args.evaluators,
                custom_params=custom_params,
            )
        )
    except Exception as exc:
        logger.error(f"Error during evaluation: {exc}")
        return 1

    print("\nEvaluation Summary:")
    print(f"Contract ID: {results.get('contract_id', 'Unknown')}")
    print(f"Application: {results.get('application_name', 'Unknown')}")
    if results.get("report_path"):
        print(f"Report: {results['report_path']}")
    opa_results = results.get("opa_results", {})
    if "error" in opa_results:
        print(f"OPA Evaluation Error: {opa_results['error']}")
    else:
        print("OPA Evaluation: Successful")
    return 0


def _cmd_demo(args: argparse.Namespace) -> int:
    """Handle the ``demo`` subcommand."""
    from aicertify._demo.runner import run_demo

    try:
        return asyncio.run(
            run_demo(
                output=args.output,
                report_format=args.format,
                policy=args.policy,
            )
        )
    except Exception as exc:
        logger.error(f"Error running demo: {exc}")
        return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aicertify",
        description=(
            "AICertify — compliance-as-code for AI systems. "
            "Run `aicertify demo` for a 10-second self-contained demo."
        ),
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # demo
    demo = subparsers.add_parser(
        "demo",
        help="Run a self-contained demo against the EU AI Act policies",
        description=(
            "Loads a bundled sample contract, evaluates it against the EU AI "
            "Act policy set via OPA, and writes a Markdown report to the "
            "current directory. Requires the `opa` binary on PATH; if "
            "missing, prints install instructions."
        ),
    )
    demo.add_argument(
        "--output",
        default="aicertify_demo_report.md",
        help="Report output filename (default: aicertify_demo_report.md)",
    )
    demo.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Report format (default: markdown)",
    )
    demo.add_argument(
        "--policy",
        default="eu_ai_act",
        help=(
            "Bundled policy framework name (default: eu_ai_act). "
            "Try also: nist, global"
        ),
    )
    demo.set_defaults(func=_cmd_demo)

    # evaluate
    ev = subparsers.add_parser(
        "evaluate",
        help="Evaluate a user-provided contract against a policy folder",
        description=(
            "Loads a contract JSON, evaluates it against the named OPA policy "
            "folder, and writes a report to --output-dir (default ./reports)."
        ),
    )
    ev.add_argument("--contract", required=True, help="Path to the contract JSON file")
    ev.add_argument(
        "--policy", required=True, help="Path or name of the OPA policy folder"
    )
    ev.add_argument(
        "--output-dir", help="Directory to save the report (default: ./reports)"
    )
    ev.add_argument(
        "--report-format",
        choices=["json", "markdown", "pdf", "html"],
        default="pdf",
        help="Report format (default: pdf)",
    )
    ev.add_argument(
        "--evaluators",
        nargs="+",
        help="Specific evaluators to use (space-separated list)",
    )
    ev.add_argument(
        "--params",
        help="JSON string or path to JSON file with custom OPA parameters",
    )
    ev.set_defaults(func=_cmd_evaluate)

    return parser


def _inject_evaluate_for_legacy_invocation(argv: list) -> list:
    """Backwards-compat shim.

    The pre-0.7.1 CLI was flat: ``aicertify --contract X --policy Y ...``.
    If the first positional arg is a flag and ``--contract`` appears, inject
    ``evaluate`` as the subcommand so old scripts keep working.
    """
    if len(argv) >= 2 and argv[1].startswith("--") and "--contract" in argv:
        return [argv[0], "evaluate", *argv[1:]]
    return argv


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    sys.argv[:] = _inject_evaluate_for_legacy_invocation(sys.argv)

    parser = _build_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger("aicertify").setLevel(logging.DEBUG)

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
