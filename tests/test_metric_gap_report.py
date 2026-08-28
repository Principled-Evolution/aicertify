"""
Tests for the metric gap report.

The report answers "what would I have to build before this library is useful
to me?", so the risk is not that it crashes. It is that it reports a gap that
does not exist, or hides one that does, because the two sides of the comparison
spell the same metric differently.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "metric_gap_report", ROOT / "scripts" / "metric_gap_report.py"
)
gap = importlib.util.module_from_spec(SPEC)
sys.modules["metric_gap_report"] = gap
SPEC.loader.exec_module(gap)

COVERAGE_PRESENT = gap.COVERAGE.is_file()
needs_policies = pytest.mark.skipif(
    not COVERAGE_PRESENT,
    reason="gopal submodule not checked out; run: git submodule update --init",
)


class TestMeasuredVsDeclared:
    """Only measured metrics belong in this report; declared facts do not."""

    @pytest.mark.parametrize(
        "name",
        [
            "metrics.content_safety.score",
            "evaluation.fairness_score",
            "summary.toxicity_values",
            "content_safety.score",
            "fairness_score",
        ],
    )
    def test_measured_inputs_are_recognised(self, name):
        assert gap.is_measured(name)

    @pytest.mark.parametrize(
        "name",
        [
            "ce_marking.affixed",
            "deployer.logs_kept_six_months",
            "system.high_risk",
            "governance.accountable_person_named",
        ],
    )
    def test_declared_facts_are_excluded(self, name):
        assert not gap.is_measured(name)


class TestSpellingReconciliation:
    """
    Evaluators declare `content_safety.score`; policies ask for
    `metrics.content_safety.score`. Comparing raw strings would report a gap
    that does not exist.
    """

    def test_prefix_difference_still_matches(self):
        supplies = {"content_safety.score": ["ContentSafetyEvaluator"]}
        assert gap.match("metrics.content_safety.score", supplies, {}) == [
            "ContentSafetyEvaluator"
        ]

    def test_underscored_and_dotted_still_match(self):
        supplies = {"fairness.score": ["FairnessEvaluator"]}
        assert gap.match("evaluation.fairness_score", supplies, {}) == [
            "FairnessEvaluator"
        ]
        assert gap.match("fairness_score", supplies, {}) == ["FairnessEvaluator"]

    def test_an_unrelated_metric_does_not_match(self):
        """The report is worthless if it matches everything to everything."""
        supplies = {"content_safety.score": ["ContentSafetyEvaluator"]}
        assert gap.match("metrics.patient_safety.score", supplies, {}) == []
        assert (
            gap.match("governance.audit_logging.completeness_score", supplies, {}) == []
        )

    def test_alias_table_widens_a_match(self):
        """
        A legacy spelling matches an evaluator offering a different legacy
        spelling of the same metric, when gopal's table says they are the same.
        """
        aliases = {
            "metrics.toxicity.score": [
                "metrics.toxicity.score",
                "metrics.toxicity.max_toxicity",
                "evaluation.toxicity_score",
            ]
        }
        supplies = {"metrics.toxicity.max_toxicity": ["ContentSafetyEvaluator"]}
        assert gap.match("evaluation.toxicity_score", supplies, aliases) == [
            "ContentSafetyEvaluator"
        ]

    def test_the_alias_table_does_not_match_across_domains(self):
        """
        Widening must stop at what the table actually says. ContentSafety
        supplies `content_safety.max_toxicity`, which gopal's table does not
        list as a spelling of `metrics.toxicity.score`. Reporting that as
        covered would be the report lying in the direction that flatters us.
        """
        aliases = {
            "metrics.toxicity.score": [
                "metrics.toxicity.score",
                "metrics.toxicity.max_toxicity",
                "evaluation.toxicity_score",
            ]
        }
        supplies = {"content_safety.max_toxicity": ["ContentSafetyEvaluator"]}
        assert gap.match("evaluation.toxicity_score", supplies, aliases) == []

    def test_no_evaluator_means_an_empty_list_not_an_error(self):
        assert gap.match("metrics.nothing.supplies_this", {}, {}) == []


@needs_policies
class TestAgainstTheRealLibrary:
    def test_the_report_runs_and_finds_frameworks(self):
        required = gap.required_metrics()
        assert (
            required
        ), "no measured metrics found; the coverage data may have changed shape"
        assert any("eu_ai_act" in f for f in required)

    def test_evaluators_are_discovered(self):
        supplies = gap.supplied_metrics()
        assert supplies, "no evaluator declared SUPPORTED_METRICS"
        names = {e for v in supplies.values() for e in v}
        assert "ContentSafetyEvaluator" in names
        assert "FairnessEvaluator" in names

    def test_the_eu_ai_act_metrics_are_fully_supplied(self):
        """
        The framework most people arrive for. If this regresses, the README
        should stop implying the EU policies work out of the box.
        """
        required = gap.required_metrics()
        supplies = gap.supplied_metrics()
        aliases = gap.load_alias_table()
        eu = next(v for k, v in required.items() if "eu_ai_act" in k)
        unmatched = [m for m in eu if not gap.match(m, supplies, aliases)]
        assert not unmatched, f"EU AI Act metrics with no evaluator: {unmatched}"

    def test_declared_facts_never_appear_in_the_report(self):
        for metrics in gap.required_metrics().values():
            for name in metrics:
                assert gap.is_measured(
                    name
                ), f"{name} is a declared fact, not a measured metric"


@needs_policies
class TestTheAliasTableIsActuallyRead:
    """
    The parser shipped once returning every canonical name with an empty alias
    list, so widening was a silent no-op and the report under-counted coverage.
    An empty list per entry looks like a working parser from the outside, which
    is why these assert content rather than shape.
    """

    def test_aliases_are_parsed_not_just_the_keys(self):
        table = gap.load_alias_table()
        assert table, "no alias table parsed from the pinned gopal checkout"
        total = sum(len(v) for v in table.values())
        assert total >= 20, f"only {total} aliases parsed across {len(table)} metrics"

    def test_every_entry_lists_itself_first(self):
        for name, paths in gap.load_alias_table().items():
            assert paths and paths[0] == name, f"{name} does not list itself first"

    def test_a_known_legacy_spelling_is_present(self):
        table = gap.load_alias_table()
        assert (
            "documentation.model_card.completeness_score"
            in table["metrics.model_card.completeness"]
        )

    def test_the_two_toxicity_statistics_stay_separate(self):
        """gopal split these deliberately; merging them here would undo it."""
        table = gap.load_alias_table()
        assert "metrics.toxicity.max_toxicity" not in table["metrics.toxicity.score"]
        assert "metrics.toxicity.score" not in table["metrics.toxicity.max_toxicity"]
