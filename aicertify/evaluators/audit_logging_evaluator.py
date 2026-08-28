"""
Audit-logging completeness.

`global/v1/common/accountability` reads
`governance.audit_logging.completeness_score` and had no evaluator, so the
policy could never be satisfied by anyone who did not already know to hand-write
that number.

It is also the simplest useful evaluator in the codebase, which makes it the
worked example in docs/writing-an-evaluator.md: no model, no API key, no
inference. It counts how many of the audit-logging facts a contract actually
carries, which is a real measurement of a real thing and needs nothing but the
contract itself.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Tuple

from aicertify.evaluators.base_evaluator import BaseEvaluator, EvaluationResult

logger = logging.getLogger(__name__)


class AuditLoggingEvaluator(BaseEvaluator):
    """Measures how completely a contract describes its audit logging."""

    #: The canonical gopal names this supplies. Using gopal's canonical spelling
    #: rather than inventing one is what makes the gap report match this
    #: evaluator to the policies that need it.
    SUPPORTED_METRICS: Tuple[str, ...] = (
        "metrics.audit_logging.completeness",
        "governance.audit_logging.completeness_score",
    )

    #: The facts a complete audit-logging description carries. Each present and
    #: truthy field is one point of completeness.
    EXPECTED_FIELDS: Tuple[str, ...] = (
        "enabled",
        "retention_period_days",
        "records_access",
        "records_changes",
        "tamper_evident",
    )

    DEFAULT_THRESHOLD = 0.8

    def _initialize(self) -> None:
        self.threshold = float(self.config.get("threshold", self.DEFAULT_THRESHOLD))

    def evaluate(self, data: Dict) -> EvaluationResult:
        governance = (data or {}).get("governance") or {}
        logging_block = governance.get("audit_logging") or {}

        present = [
            f for f in self.EXPECTED_FIELDS if _is_populated(logging_block.get(f))
        ]
        score = len(present) / len(self.EXPECTED_FIELDS)
        missing = [f for f in self.EXPECTED_FIELDS if f not in present]

        return EvaluationResult(
            evaluator_name="AuditLoggingEvaluator",
            compliant=score >= self.threshold,
            score=score,
            threshold=self.threshold,
            reason=(
                f"{len(present)} of {len(self.EXPECTED_FIELDS)} audit-logging facts present"
                + (f"; missing {', '.join(missing)}" if missing else "")
            ),
            details={
                "present": present,
                "missing": missing,
                # Emitted under the canonical name so a policy reading
                # metrics.audit_logging.completeness finds it without the caller
                # having to know which spelling this evaluator prefers.
                "metrics": {"audit_logging": {"completeness": score}},
            },
        )

    async def evaluate_async(self, data: Dict) -> EvaluationResult:
        # Nothing here is I/O bound: it counts fields already in memory. The
        # async form exists because the interface requires it, and pretending
        # otherwise by spawning a thread would cost more than it saves.
        return self.evaluate(data)


def _is_populated(value: Any) -> bool:
    """
    Present and meaningful.

    `False` and `0` count as answered: "tamper evident: no" is a real answer and
    a policy should be allowed to fail on it, rather than the field being
    treated as unanswered and quietly dropped from the denominator.
    """
    return value is not None and value != ""
