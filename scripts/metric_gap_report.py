#!/usr/bin/env python3
"""
Which metrics do gopal's policies need, and which can AICertify supply?

A gopal policy reads two kinds of input. Facts a person declares, and metrics a
tool measures. The declared facts are answerable by anyone who knows their own
organisation. The measured metrics are not: without an evaluator that produces
them, the policies reading them can never be satisfied, and there has been no
way to find out which those are short of reading the Rego.

This prints that list. For each framework it reports the measured metrics the
policies require, whether an evaluator declares it supplies them, and which
evaluator. What is left over is the work a user would have to do themselves,
and is the honest answer to "what do I need before this library is useful to
me?".

Usage:
    python scripts/metric_gap_report.py [--framework eu_ai_act] [--json]
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import logging
import pkgutil
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterator, List, Set

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "aicertify" / "opa_policies" / "docs" / "coverage" / "coverage.json"
ALIASES_REGO = ROOT / "aicertify" / "opa_policies" / "helper_functions" / "metrics.rego"

#: A required input counts as "measured" when it is produced by running
#: something over the system rather than asserted by a person.
MEASURED_PREFIXES = (
    "metrics.",
    "evaluation.",
    "summary.",
    "results.",
    "content_safety.",
)


def is_measured(name: str) -> bool:
    return name.startswith(MEASURED_PREFIXES) or name.endswith("_score")


def canonical_forms(name: str) -> Set[str]:
    """
    Every spelling that plausibly refers to the same metric.

    gopal now fixes one canonical name per metric and keeps the historical
    spellings as fallbacks, but the two sides of this comparison were written
    years apart: evaluators declare `content_safety.score` while policies ask
    for `metrics.content_safety.score`. Comparing raw strings would report a
    gap that does not exist, so both sides are reduced to a common form.
    """
    forms = {name}
    stripped = re.sub(r"^(metrics|evaluation|summary|results)\.", "", name)
    forms.add(stripped)
    # fairness_score and fairness.score are the same metric written two ways.
    forms.add(re.sub(r"_score$", ".score", stripped))
    forms.add(stripped.replace(".", "_"))
    return {f for f in forms if f}


def load_alias_table() -> Dict[str, List[str]]:
    """
    gopal's canonical-to-legacy table, when the pinned checkout has one.

    Absent on an older pin, in which case matching falls back to the shape
    rules above. Reported either way, so a thin match is visible rather than
    silently assumed.
    """
    if not ALIASES_REGO.is_file():
        return {}
    text = ALIASES_REGO.read_text(encoding="utf-8")
    table: Dict[str, List[str]] = {}
    # Scanned line by line rather than with one regex. The entries are nested
    # arrays, and a non-greedy pattern to the first "]," stops at the end of the
    # first inner path instead of the end of the entry. That yields an empty
    # alias list for every metric and makes the widening a silent no-op, which
    # is how this shipped the first time.
    current = None
    for line in text.splitlines():
        stripped = line.strip()
        opening = re.match(r'"(metrics\.[\w.]+)":\s*\[$', stripped)
        if opening:
            current = opening.group(1)
            table[current] = []
            continue
        if current is None:
            continue
        if stripped.startswith("],"):
            current = None
            continue
        segments = re.findall(r'"([^"]+)"', stripped)
        if segments:
            table[current].append(".".join(segments))
    return {name: paths for name, paths in table.items() if paths}


def policies(node) -> Iterator[dict]:
    if isinstance(node, dict):
        if "package" in node and "path" in node:
            yield node
        for v in node.values():
            yield from policies(v)
    elif isinstance(node, list):
        for v in node:
            yield from policies(v)


def framework_of(path: str) -> str:
    parts = path.split("/")
    if parts[0] in ("international", "industry_specific") and len(parts) > 1:
        return f"{parts[0]}/{parts[1]}"
    return parts[0]


def required_metrics() -> Dict[str, Dict[str, Set[str]]]:
    """framework -> metric -> set of policy paths requiring it."""
    if not COVERAGE.is_file():
        sys.exit(f"error: {COVERAGE} not found. Is the gopal submodule checked out?")
    doc = json.loads(COVERAGE.read_text(encoding="utf-8"))
    out: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
    for p in policies(doc):
        if p.get("is_library"):
            continue
        for name in p.get("required_metrics") or []:
            if is_measured(name):
                out[framework_of(p["path"])][name].add(p["path"])
    return out


def supplied_metrics() -> Dict[str, List[str]]:
    """metric -> evaluators declaring they produce it."""
    logging.disable(logging.CRITICAL)
    import aicertify.evaluators as pkg

    supplies: Dict[str, List[str]] = defaultdict(list)

    def scan(mod) -> None:
        for _, obj in vars(mod).items():
            if inspect.isclass(obj) and getattr(obj, "SUPPORTED_METRICS", None):
                for metric in obj.SUPPORTED_METRICS:
                    if obj.__name__ not in supplies[metric]:
                        supplies[metric].append(obj.__name__)

    scan(pkg)
    for _, name, _ in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        try:
            scan(importlib.import_module(name))
        except Exception:  # noqa: BLE001 - an evaluator with a missing optional
            continue  # dependency should not hide the rest of the report
    return dict(supplies)


def registered_evaluators() -> Set[str]:
    """Evaluator class names the pipeline will actually instantiate.

    Declaring SUPPORTED_METRICS is what makes an evaluator visible to this
    report, but ComplianceEvaluator only runs what is in EVALUATOR_CLASSES.
    An evaluator in the first set and not the second supplies nothing at
    runtime, and reporting it as `ok` would be a fail-open: the report would
    claim a metric is covered when no pipeline produces it.
    """
    logging.disable(logging.CRITICAL)
    try:
        from aicertify.evaluators.compliance_evaluator import ComplianceEvaluator
    except Exception:  # noqa: BLE001 - report degrades rather than dying
        return set()
    return {c.__name__ for c in ComplianceEvaluator.EVALUATOR_CLASSES.values()}


def match(
    required: str, supplies: Dict[str, List[str]], aliases: Dict[str, List[str]]
) -> List[str]:
    """Evaluators that supply this required metric, under any known spelling."""
    wanted = canonical_forms(required)
    for canonical, legacy in aliases.items():
        if required in legacy or required == canonical:
            wanted |= canonical_forms(canonical)
            for name in legacy:
                wanted |= canonical_forms(name)
    hits: List[str] = []
    for offered, evaluators in supplies.items():
        if canonical_forms(offered) & wanted:
            for e in evaluators:
                if e not in hits:
                    hits.append(e)
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--framework", help="report on one framework, e.g. eu_ai_act")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    required = required_metrics()
    supplies = supplied_metrics()
    aliases = load_alias_table()
    registered = registered_evaluators()

    result: Dict[str, dict] = {}
    for framework in sorted(required):
        if args.framework and args.framework not in framework:
            continue
        rows = []
        for metric in sorted(required[framework]):
            evaluators = match(metric, supplies, aliases)
            live = [e for e in evaluators if not registered or e in registered]
            unwired = [e for e in evaluators if e not in live]
            rows.append(
                {
                    "metric": metric,
                    "required_by": sorted(required[framework][metric]),
                    "evaluators": live,
                    "unregistered": unwired,
                }
            )
        result[framework] = {
            "metrics": rows,
            "covered": sum(1 for r in rows if r["evaluators"]),
            "total": len(rows),
        }

    if args.json:
        print(
            json.dumps(
                {
                    "alias_table_available": bool(aliases),
                    "evaluators_found": sorted(
                        {e for v in supplies.values() for e in v}
                    ),
                    "unregistered_evaluators": (
                        sorted({e for v in supplies.values() for e in v} - registered)
                        if registered
                        else []
                    ),
                    "frameworks": result,
                },
                indent=2,
            )
        )
        return 0

    if not aliases:
        print("note: gopal's canonical metric table was not found in the pinned")
        print("      submodule, so matching uses name shape alone and may be thin.\n")

    total_c = total_n = 0
    for framework, data in result.items():
        total_c += data["covered"]
        total_n += data["total"]
        print(
            f"{framework}  ({data['covered']}/{data['total']} measured metrics have an evaluator)"
        )
        for row in data["metrics"]:
            if row["evaluators"]:
                mark, who = "ok  ", ", ".join(row["evaluators"])
            elif row["unregistered"]:
                mark = "WIRE"
                who = (
                    f"{', '.join(row['unregistered'])} declares this but is not in "
                    "ComplianceEvaluator.EVALUATOR_CLASSES, so it never runs"
                )
            else:
                mark, who = "GAP ", "no evaluator declares this"
            print(f"  {mark} {row['metric']:<46} {who}")
        print()
    print(f"TOTAL: {total_c} of {total_n} measured metrics can be supplied today.")
    if total_c < total_n:
        print("The gaps are what you would need to write an evaluator for, or")
        print("supply by hand. See docs on writing one.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
