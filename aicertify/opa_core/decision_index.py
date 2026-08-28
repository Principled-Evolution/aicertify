"""
What each gopal policy calls its decision, read from the library itself.

AICertify used to query `data.<package>.report_output` for every policy. Four
of gopal's 91 policies define that rule, so an EU AI Act evaluation reported 4
verdicts out of 29 and a UK, NIST, BFS, legal or global evaluation reported
none at all, while still exiting successfully (issue #78).

The policies were never the problem. They expose their decisions under names
that vary by author and vintage: `allow`, `is_compliant`, `compliant`. Rather
than guess, gopal now publishes `docs/coverage/coverage.json`, generated from
its own tree and checked in its CI, which names the primary decision rule for
every policy and says whether a `true` from it means compliant or means a
concern was detected. This module reads that file.

Reading it rather than inferring matters for one policy in particular. A
detector such as `prohibited_practices/social_scoring` returns `true` when it
has found something wrong. Treating that as a pass would invert the finding on
exactly the policies where being wrong costs the most.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)

COVERAGE_RELATIVE_PATH = Path("docs") / "coverage" / "coverage.json"


@dataclass(frozen=True)
class PolicyDescriptor:
    """What the library says about one policy."""

    package: str
    title: Optional[str] = None
    #: The rule that carries the verdict, e.g. "allow" or "is_compliant".
    decision_rule: Optional[str] = None
    #: "compliant" when a true verdict is a pass, "concern" when true means a
    #: problem was detected and the sense has to be inverted for a report.
    true_means: Optional[str] = None
    references: List[str] = field(default_factory=list)
    is_library: bool = False

    @property
    def reports_a_verdict(self) -> bool:
        """False for the shared helper libraries, which decide nothing."""
        return bool(self.decision_rule) and not self.is_library

    def interpret(self, raw: object) -> Optional[bool]:
        """
        Turn the rule's raw value into pass or fail.

        Returns None rather than False when the value is missing or not a
        boolean. In Rego an undefined value is not `false`: it means the policy
        reached no conclusion, usually because an input it reads is absent.
        Collapsing the two would report "we could not tell" as "compliant",
        which is the failure mode this whole library exists to avoid.
        """
        if not isinstance(raw, bool):
            return None
        return (not raw) if self.true_means == "concern" else raw


def _walk(node: object) -> Iterator[dict]:
    """Yield every policy record in the coverage document, at any depth."""
    if isinstance(node, dict):
        if "package" in node and "path" in node:
            yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


@lru_cache(maxsize=8)
def load_index(policy_dir: str) -> Dict[str, PolicyDescriptor]:
    """
    Read coverage.json from a gopal checkout.

    An empty index is returned rather than raised when the file is absent, so
    an older pinned submodule degrades to the previous behaviour instead of
    breaking evaluation outright.
    """
    coverage = Path(policy_dir) / COVERAGE_RELATIVE_PATH
    if not coverage.is_file():
        logger.warning(
            "No coverage data at %s. Falling back to report rules only; "
            "policies that publish only a decision rule will not be reported.",
            coverage,
        )
        return {}

    try:
        document = json.loads(coverage.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read %s: %s", coverage, exc)
        return {}

    index: Dict[str, PolicyDescriptor] = {}
    for record in _walk(document):
        package = record.get("package")
        if not package:
            continue
        decision = record.get("primary_decision")
        if not decision:
            # Older coverage data predates primary_decision. Fall back to the
            # first declared decision rule, which is the same choice the
            # generator makes.
            rules = record.get("decision_rules") or []
            named = [
                r.get("name") for r in rules if isinstance(r, dict) and r.get("name")
            ]
            decision = named[0] if named else None
        index[package] = PolicyDescriptor(
            package=package,
            title=record.get("title"),
            decision_rule=decision,
            true_means=record.get("decision_true_means"),
            references=list(record.get("references") or []),
            is_library=bool(record.get("is_library")),
        )

    logger.debug(
        "Loaded %d policy descriptors, %d of which report a verdict.",
        len(index),
        sum(1 for d in index.values() if d.reports_a_verdict),
    )
    return index


def descriptor_for(policy_dir: str, package: str) -> Optional[PolicyDescriptor]:
    """The descriptor for one package, or None if the library does not know it."""
    return load_index(policy_dir).get(package)
