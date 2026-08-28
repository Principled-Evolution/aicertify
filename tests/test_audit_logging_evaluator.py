"""Tests for the worked-example evaluator in docs/writing-an-evaluator.md."""

import pytest

from aicertify.evaluators.audit_logging_evaluator import AuditLoggingEvaluator

COMPLETE = {
    "governance": {
        "audit_logging": {
            "enabled": True,
            "retention_period_days": 365,
            "records_access": True,
            "records_changes": True,
            "tamper_evident": True,
        }
    }
}


@pytest.fixture
def evaluator():
    return AuditLoggingEvaluator()


class TestScoring:
    def test_a_complete_description_scores_one(self, evaluator):
        r = evaluator.evaluate(COMPLETE)
        assert r.score == 1.0 and r.compliant

    def test_an_empty_contract_scores_zero(self, evaluator):
        r = evaluator.evaluate({})
        assert r.score == 0.0 and not r.compliant

    def test_a_partial_description_scores_proportionally(self, evaluator):
        r = evaluator.evaluate({"governance": {"audit_logging": {"enabled": True}}})
        assert r.score == pytest.approx(0.2)
        assert "retention_period_days" in r.details["missing"]

    def test_a_negative_answer_still_counts_as_answered(self, evaluator):
        """
        "tamper evident: no" is a real answer. Treating False as unanswered
        would drop it from the denominator and flatter the score, when what it
        should do is let the policy fail on it.
        """
        r = evaluator.evaluate(
            {
                "governance": {
                    "audit_logging": {
                        "enabled": False,
                        "retention_period_days": 0,
                        "records_access": False,
                        "records_changes": False,
                        "tamper_evident": False,
                    }
                }
            }
        )
        assert (
            r.score == 1.0
        ), "every field was answered, even though every answer was no"
        assert r.details["missing"] == []

    def test_an_empty_string_is_not_an_answer(self, evaluator):
        r = evaluator.evaluate({"governance": {"audit_logging": {"enabled": ""}}})
        assert r.score == 0.0


class TestTheContractWithGopal:
    def test_it_declares_gopal_canonical_names(self):
        """
        The gap report matches evaluators to policies by name. Inventing a
        spelling here would leave the policy looking unsupplied.
        """
        assert (
            "metrics.audit_logging.completeness"
            in AuditLoggingEvaluator.SUPPORTED_METRICS
        )
        assert (
            "governance.audit_logging.completeness_score"
            in AuditLoggingEvaluator.SUPPORTED_METRICS
        )

    def test_it_emits_the_metric_under_the_canonical_path(self, evaluator):
        r = evaluator.evaluate(COMPLETE)
        assert r.details["metrics"]["audit_logging"]["completeness"] == 1.0

    def test_the_threshold_is_configurable(self):
        strict = AuditLoggingEvaluator({"threshold": 1.0})
        partial = {
            "governance": {"audit_logging": {"enabled": True, "tamper_evident": True}}
        }
        assert not strict.evaluate(partial).compliant


@pytest.mark.asyncio
async def test_the_async_form_agrees_with_the_sync_one():
    e = AuditLoggingEvaluator()
    assert (await e.evaluate_async(COMPLETE)).score == e.evaluate(COMPLETE).score
