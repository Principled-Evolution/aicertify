#!/usr/bin/env python
"""AICertify command-line interface.

Primary subcommands:

* ``aicertify demo`` — run the bundled local demonstration.
* ``aicertify evaluate`` — evaluate a contract against a policy set.
* ``aicertify explain`` — show the fields a framework's policies require.
* ``aicertify init-contract`` — scaffold those required fields into a contract.
* ``aicertify score-card`` — score model-card documentation with GOPAL's rubric.

For backwards compatibility, ``aicertify --contract X --policy Y`` (no
subcommand) is treated as ``aicertify evaluate --contract X --policy Y``.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
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
                with_llm_metrics=args.with_llm_metrics,
            )
        )
    except Exception as exc:
        logger.error(f"Error running demo: {exc}")
        return 1


def _cmd_explain(args: argparse.Namespace) -> int:
    """Handle the ``explain`` subcommand."""
    from aicertify.opa_core.introspection import (
        available_frameworks,
        evaluator_for,
        introspect,
    )

    try:
        info = introspect(args.framework)
    except LookupError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "framework": info.query,
                    "policy_count": info.policy_count,
                    "policies": [
                        {
                            "package": p.package,
                            "path": p.path,
                            "required_metrics": p.required_metrics,
                            "required_params": p.required_params,
                        }
                        for p in info.policies
                    ],
                    "declared_fields": info.declared_fields,
                    "evaluator_fields": info.evaluator_fields,
                    "params": info.params,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    width = 46
    print(f"\n{info.query}  —  {info.policy_count} policies\n")

    if info.declared_fields:
        print(f"Fields you must declare ({len(info.declared_fields)})")
        print("  No evaluator can observe these. They are facts about your system,")
        print(
            "  your process, or your paperwork, so you assert them in the contract.\n"
        )
        for path in sorted(info.declared_fields):
            users = info.declared_fields[path]
            shown = ", ".join(users[:3])
            if len(users) > 3:
                shown += f", +{len(users) - 3} more"
            print(f"  {path:<{width}} {shown}")
        print()

    if info.evaluator_fields:
        print(f"Fields produced by evaluators ({len(info.evaluator_fields)})")
        print("  Computed at evaluation time from your interactions. Do not hand-write")
        print("  these: asserting your own fairness score defeats the point.\n")
        for path in sorted(info.evaluator_fields):
            users = info.evaluator_fields[path]
            hint = evaluator_for(path)
            suffix = f"[{hint} evaluator]" if hint else ""
            print(f"  {path:<{width}} {', '.join(users[:2])} {suffix}".rstrip())
        print()

    if info.params:
        print(f"Tunable parameters ({len(info.params)})")
        print("  Thresholds with documented defaults. Override in the contract's")
        print("  params object or with `evaluate --params`.\n")
        for name in sorted(info.params):
            users = ", ".join(info.param_sources.get(name, [])[:3])
            print(f"  {name:<{width}} default {info.params[name]!r:<10} {users}")
        print()

    if args.policies:
        print(f"Policies ({info.policy_count})\n")
        for p in info.policies:
            print(f"  {p.package}")
            print(f"    {len(p.required_metrics)} required fields  ·  {p.path}")
        print()

    print(f"Next: aicertify init-contract --policy {args.framework} > contract.json")
    if not args.policies:
        print("      Add --policies to list the individual policies.")
    print(
        "\nFields are classified by prefix, which is a heuristic. A real "
        "evaluation is\nthe authoritative answer.  Frameworks: "
        + ", ".join(available_frameworks())
        + "\n"
    )
    return 0


def _cmd_init_contract(args: argparse.Namespace) -> int:
    """Handle the ``init-contract`` subcommand."""
    from aicertify.opa_core.introspection import (
        build_contract_skeleton,
        introspect,
        unfilled_paths,
    )

    try:
        info = introspect(args.policy)
    except LookupError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    contract = build_contract_skeleton(
        info,
        application_name=args.application_name,
        model_name=args.model_name,
    )
    rendered = json.dumps(contract, indent=2, sort_keys=False)

    if args.output:
        if os.path.exists(args.output) and not args.force:
            print(
                f"error: {args.output} already exists. Pass --force to overwrite.",
                file=sys.stderr,
            )
            return 2
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered + "\n")
        todo = len(unfilled_paths(contract.get("context", {})))
        print(f"Wrote {args.output}", file=sys.stderr)
        print(
            f"  {info.policy_count} policies, {todo} fields to fill in under context.",
            file=sys.stderr,
        )
        print(
            f"  Run `aicertify explain {args.policy}` to see what each field means.",
            file=sys.stderr,
        )
    else:
        # Stdout stays pure JSON so `> contract.json` produces a valid file.
        print(rendered)

    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aicertify",
        description=(
            "AICertify — compliance-as-code for AI systems. "
            "Run `aicertify demo` for a self-contained local demonstration."
        ),
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    # Accepted after the subcommand too. `aicertify demo --verbose` is what
    # people type, and with --verbose defined only on the top-level parser it
    # failed with "unrecognized arguments: --verbose" after already spending
    # several seconds importing the evaluator stack. Sharing one parent parser
    # keeps a single definition and lets it appear on either side.
    verbose_parent = argparse.ArgumentParser(add_help=False)
    verbose_parent.add_argument(
        "--verbose", action="store_true", help="Enable debug logging"
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # demo
    demo = subparsers.add_parser(
        "demo",
        parents=[verbose_parent],
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
    demo.add_argument(
        "--with-llm-metrics",
        action="store_true",
        help=(
            "Include the LLM-judged evaluators (fairness, toxicity). Off by "
            "default: they need an OPENAI_API_KEY, make a billable call per "
            "interaction, and take minutes. The OPA verdict does not need them."
        ),
    )
    demo.set_defaults(func=_cmd_demo)

    # evaluate
    ev = subparsers.add_parser(
        "evaluate",
        parents=[verbose_parent],
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
        "--params",
        help="JSON string or path to JSON file with custom OPA parameters",
    )
    ev.set_defaults(func=_cmd_evaluate)

    # explain
    ex = subparsers.add_parser(
        "explain",
        parents=[verbose_parent],
        help="Show what input a framework's policies need, and why",
        description=(
            "Print every field the policies in a framework require, split into "
            "the ones you must declare and the ones an evaluator computes for "
            "you. Answers 'what do I feed it?' without running an evaluation."
        ),
    )
    ex.add_argument(
        "framework",
        help="Framework to explain, e.g. eu_ai_act, uk, bfs, international/eu_ai_act",
    )
    ex.add_argument(
        "--policies",
        action="store_true",
        help="Also list the individual policies and their field counts",
    )
    ex.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of the human summary",
    )
    ex.set_defaults(func=_cmd_explain)

    # init-contract
    init = subparsers.add_parser(
        "init-contract",
        parents=[verbose_parent],
        help="Scaffold a contract with every field a framework needs",
        description=(
            "Write a contract skeleton containing every field the chosen "
            "framework declares, nested into the shape the policies read, so "
            "the first run is filling in blanks rather than guessing."
        ),
    )
    init.add_argument(
        "--policy",
        required=True,
        help="Framework to scaffold for, e.g. eu_ai_act, uk, bfs",
    )
    init.add_argument(
        "--output",
        "-o",
        help="Write to this file instead of stdout",
    )
    init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite --output if it already exists",
    )
    init.add_argument(
        "--application-name",
        default="your-application",
        help="Value for application_name (default: your-application)",
    )
    init.add_argument(
        "--model-name",
        default="your-model",
        help="Value for model_info.model_name (default: your-model)",
    )
    init.set_defaults(func=_cmd_init_contract)

    # score-card
    sc = subparsers.add_parser(
        "score-card",
        parents=[verbose_parent],
        help="Score a Hugging Face model card against GOPAL's documentation rubric",
        description=(
            "Fetch a model card from the Hub and score how much of GOPAL's "
            "documentation requirement it answers. The number is a "
            "documentation-completeness measure, not a compliance verdict: a "
            "card answers part of what Annex IV asks and then stops."
        ),
    )
    sc.add_argument(
        "repo_id",
        nargs="?",
        help="Hub repo, e.g. bert-base-uncased or openai-community/gpt2",
    )
    sc.add_argument("--file", help="Score a local README.md instead of the Hub")
    sc.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="Pass mark to compare against (default 0.8, the EU AI Act "
        "technical-documentation check)",
    )
    sc.add_argument("--json", action="store_true", help="Machine-readable output")
    sc.add_argument("--quiet", action="store_true", help="Omit the per-section table")
    sc.set_defaults(func=_cmd_score_card)

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


def _cmd_score_card(args) -> int:
    """Score a Hugging Face model card by running GOPAL's rubric."""
    import json as _json

    from aicertify.adapters import GopalUnavailable, score_model_card

    if args.file:
        card = pathlib.Path(args.file).read_text(encoding="utf-8")
        source = args.file
    else:
        try:
            from huggingface_hub import ModelCard
        except ImportError:
            print(
                "Reading from the Hub needs huggingface_hub. Install it, or pass "
                "--file with a README.md you already have.",
                file=sys.stderr,
            )
            return 2
        try:
            card = ModelCard.load(args.repo_id).content
        except Exception as exc:  # noqa: BLE001 - the reason matters more than the type
            print(f"Could not load {args.repo_id}: {exc}", file=sys.stderr)
            return 2
        source = args.repo_id

    try:
        scored = score_model_card(card)
    except GopalUnavailable as exc:
        print(f"Cannot score: {exc}", file=sys.stderr)
        return 2

    if not scored:
        print(f"{source}: no readable model card content", file=sys.stderr)
        return 2

    completeness = scored["completeness"]
    quality = scored["quality"]
    threshold = args.threshold
    versions = _versions()

    if args.json:
        print(
            _json.dumps(
                {
                    "source": source,
                    "completeness": completeness,
                    "quality": quality,
                    "threshold": threshold,
                    "passes": completeness >= threshold,
                    "sections": scored["section_scores"],
                    "weakest_sections": scored["weakest_sections"],
                    "versions": versions,
                },
                indent=2,
            )
        )
        return 0

    verdict = "PASS" if completeness >= threshold else "BELOW THRESHOLD"
    print(f"\n{source}")
    print(f"  completeness  {completeness:.2f}   (threshold {threshold})")
    print(f"  quality       {quality:.2f}")
    print(f"  {verdict}\n")

    if scored["section_scores"] and not args.quiet:
        for section, score in sorted(
            scored["section_scores"].items(), key=lambda kv: -kv[1]
        ):
            bar = "#" * int(round(score * 20))
            print(f"    {section:<24} {score:4.2f}  {bar}")
        print()

    if completeness < threshold:
        print(
            "A model card answers part of what Annex IV asks and then stops.\n"
            "This is the documentation-completeness gap, not a compliance verdict."
        )
    print(
        f"\nscored by GOPAL {versions['gopal']} "
        f"(global/v1/documentation/model_card_score), via aicertify "
        f"{versions['aicertify']}"
    )
    return 0


def _versions() -> dict:
    """What produced this number, so a rerun can be compared against it."""

    try:
        import importlib.metadata as _md

        aicertify_version = _md.version("aicertify")
    except Exception:  # noqa: BLE001
        aicertify_version = "unknown"

    gopal_version = "unknown"
    changelog = pathlib.Path(__file__).resolve().parent / "opa_policies" / "VERSION"
    if changelog.exists():
        gopal_version = changelog.read_text().strip()

    # No rubric version of its own any more. The rubric is a GOPAL policy, so
    # the GOPAL version identifies it, and a figure quoted anywhere can be
    # reproduced by pinning that one number.
    return {
        "aicertify": aicertify_version,
        "gopal": gopal_version,
    }


def main() -> int:
    # Quiet by default. CLI tools should not flood the terminal with INFO-level
    # chatter from downstream libraries (langfair, deepeval, transformers, the
    # OPA policy loader, …) unless the user opts in via --verbose. Note: this
    # runs BEFORE argparse so it's in effect when the (deferred) aicertify
    # package imports happen inside the subcommand handlers.
    # force=True matters. Seven modules call logging.basicConfig(level=INFO) at
    # import time, and importing the aicertify package runs them before main()
    # does. Without force the root logger already has a handler, basicConfig
    # returns early, and the intended quiet default never takes effect: every
    # command printed INFO chatter from the policy loader and the evaluators.
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )

    sys.argv[:] = _inject_evaluate_for_legacy_invocation(sys.argv)

    parser = _build_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger("aicertify").setLevel(logging.DEBUG)

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
