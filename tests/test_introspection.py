"""Tests for policy introspection and the declared-context merge.

The merge is the load-bearing part. Most GOPAL obligations turn on facts no
evaluator can observe (was a conformity assessment completed, can a human
intervene), and before ``merge_declared_context`` existed those facts could not
reach OPA at all: the input was evaluator output and nothing else, so every
policy resting on a declaration denied no matter what the contract said.

Two properties matter and are asserted directly:

* a measurement is never displaced by a declaration, so a contract cannot
  assert its own fairness score;
* an unfilled scaffold, which is all nulls, merges to nothing rather than to a
  wall of explicit nulls that a policy might read as "assessed, and false".
"""

from __future__ import annotations

import pytest

from aicertify.opa_core.introspection import (
    build_contract_skeleton,
    build_field_skeleton,
    evaluator_for,
    is_evaluator_field,
    merge_declared_context,
    unfilled_paths,
    attach_measured_metrics,
    collect_measured_metrics,
)


class TestFieldClassification:
    @pytest.mark.parametrize(
        "path",
        [
            "metrics.content_safety.score",
            "evaluation.fairness_score",
            "summary.toxicity_values.max_toxicity",
            "results.fairness",
            "fairness_score",
            "content_safety_score",
            "risk_management_score",
        ],
    )
    def test_evaluator_produced_fields(self, path):
        assert is_evaluator_field(path)

    @pytest.mark.parametrize(
        "path",
        [
            "system.high_risk",
            "assessment.completed",
            "decision.significant",
            "safeguards.human_intervention_available",
            "ce_marking.affixed",
            "governance.accountable_person_named",
        ],
    )
    def test_declared_fields(self, path):
        """Nothing in a transcript reveals whether the CE marking was affixed."""
        assert not is_evaluator_field(path)

    def test_evaluator_attribution(self):
        assert evaluator_for("metrics.content_safety.score") == "content_safety"
        assert evaluator_for("metrics.fairness.gender_bias") == "fairness"
        assert evaluator_for("system.high_risk") is None


class TestSkeleton:
    def test_dotted_paths_become_nested_objects(self):
        class Stub:
            declared_fields = {
                "decision.significant": ["adm"],
                "decision.special_category_data_involved": ["adm"],
                "system.high_risk": ["ce"],
            }

        assert build_field_skeleton(Stub()) == {
            "decision": {"significant": None, "special_category_data_involved": None},
            "system": {"high_risk": None},
        }

    def test_a_leaf_does_not_swallow_a_deeper_branch(self):
        """`a.b` and `a.b.c` together must keep the branch, not drop half."""

        class Stub:
            declared_fields = {"a.b": ["p"], "a.b.c": ["p"]}

        tree = build_field_skeleton(Stub())
        assert tree["a"]["b"] == {"c": None}

    def test_unfilled_paths_finds_every_null(self):
        tree = {"a": {"b": None, "c": 1}, "d": None}
        assert sorted(unfilled_paths(tree)) == ["a.b", "d"]


class TestMergeDeclaredContext:
    def test_declarations_land_at_the_top_level(self):
        """Policies read input.decision.significant, not input.context.decision."""
        merged = merge_declared_context(
            {}, {"context": {"decision": {"significant": True}}}
        )
        assert merged == {"decision": {"significant": True}}

    def test_measurements_are_never_displaced_by_declarations(self):
        """A contract must not be able to assert its own content-safety score."""
        measured = {"metrics": {"content_safety": {"score": 0.1}}}
        lying = {"context": {"metrics": {"content_safety": {"score": 0.99}}}}
        assert merge_declared_context(measured, lying) == measured

    def test_declarations_fill_only_what_the_evaluators_left_empty(self):
        measured = {"metrics": {"fairness": {"score": 0.9}}}
        declared = {"context": {"system": {"high_risk": True}}}
        assert merge_declared_context(measured, declared) == {
            "metrics": {"fairness": {"score": 0.9}},
            "system": {"high_risk": True},
        }

    def test_sibling_keys_merge_rather_than_replace(self):
        measured = {"governance": {"measured_thing": 1}}
        declared = {"context": {"governance": {"accountable_person_named": True}}}
        assert merge_declared_context(measured, declared) == {
            "governance": {"measured_thing": 1, "accountable_person_named": True}
        }

    def test_an_unfilled_scaffold_merges_to_nothing(self):
        """The critical safety property.

        A scaffold is all nulls. Passing them through would hand the policy an
        explicit null for every field, and a rule checking `is_boolean` would
        then read "assessed and false" instead of "never assessed". Dropping
        them means an unfilled scaffold denies, which is what it should do.
        """
        scaffold = {
            "context": {
                "decision": {"significant": None, "meaningful_human_involvement": None},
                "system": {"high_risk": None},
            }
        }
        assert merge_declared_context({}, scaffold) == {}

    def test_a_partly_filled_scaffold_keeps_only_what_was_filled(self):
        scaffold = {
            "context": {
                "decision": {
                    "significant": True,
                    "special_category_data_involved": None,
                },
                "system": {"high_risk": None},
            }
        }
        assert merge_declared_context({}, scaffold) == {
            "decision": {"significant": True}
        }

    def test_false_is_a_real_declaration_and_survives(self):
        """False is an answer. Only null means "not filled in"."""
        scaffold = {"context": {"decision": {"meaningful_human_involvement": False}}}
        assert merge_declared_context({}, scaffold) == {
            "decision": {"meaningful_human_involvement": False}
        }

    def test_compliance_context_is_merged_too(self):
        contract = {"compliance_context": {"system": {"high_risk": True}}}
        assert merge_declared_context({}, contract) == {"system": {"high_risk": True}}

    def test_params_are_carried_across(self):
        contract = {"params": {"toxicity_threshold": 0.5}}
        assert merge_declared_context({}, contract)["params"] == {
            "toxicity_threshold": 0.5
        }

    def test_no_context_is_a_no_op(self):
        assert merge_declared_context({"a": 1}, {}) == {"a": 1}

    def test_none_evaluation_results_are_tolerated(self):
        assert merge_declared_context(None, {"context": {"a": {"b": 1}}}) == {
            "a": {"b": 1}
        }

    def test_a_pydantic_style_contract_object_works(self):
        """aicertify_app_for_policy passes a model, not a dict."""

        class Contract:
            context = {"system": {"high_risk": True}}
            compliance_context: dict = {}
            params: dict = {}

        assert merge_declared_context({}, Contract()) == {"system": {"high_risk": True}}


class TestAgainstTheBundledLibrary:
    def test_uk_scaffold_covers_every_declared_field(self):
        from aicertify.opa_core.introspection import introspect

        try:
            info = introspect("uk")
        except LookupError:
            pytest.skip("gopal submodule not checked out")

        contract = build_contract_skeleton(info)
        scaffolded = set(unfilled_paths(contract["context"]))
        assert scaffolded == set(
            info.declared_fields
        ), "every declared field should appear in the scaffold as a null"

    def test_uk_scaffold_is_a_valid_contract_shape(self):
        from aicertify.opa_core.introspection import introspect

        try:
            info = introspect("uk")
        except LookupError:
            pytest.skip("gopal submodule not checked out")

        contract = build_contract_skeleton(info)
        for key in ("application_name", "model_info", "interactions", "context"):
            assert key in contract
        assert contract["interactions"], "a contract needs at least one interaction"
        assert "model_name" in contract["model_info"]


class TestMeasuredMetricsReachThePolicies:
    """
    GOPAL reads measured metrics at input.metrics.<domain>.<name>. Evaluator
    output is keyed by evaluator name, so before attach_measured_metrics only
    three canonical names resolved, and only by coincidence: fairness,
    content_safety and risk_management happen to spell an evaluator name in the
    middle with "score" at the end. metrics.model_card.completeness did not
    line up, so no policy reading it ever saw a measurement even though the gap
    report called it supplied.
    """

    @staticmethod
    def _phase1():
        return {
            "results": {
                "content_safety": {
                    "score": 0.0,
                    "details": {
                        "safety_score": 0.0,
                        "metrics": {"toxicity": {"score": 0.29, "max_toxicity": 0.8}},
                    },
                },
                "model_card": {
                    "score": 0.42,
                    "details": {"metrics": {"model_card": {"completeness": 0.42}}},
                },
                "fairness": {"score": 0.91, "details": {}},
            }
        }

    def test_a_canonical_metric_an_evaluator_emitted_is_attached(self):
        out = attach_measured_metrics(dict(self._phase1()), self._phase1())
        assert out["metrics"]["model_card"]["completeness"] == 0.42
        assert out["metrics"]["toxicity"]["score"] == 0.29

    def test_the_results_alias_still_works(self):
        """
        Regression guard. Setting input.metrics from measured metrics alone made
        _transform_input_for_opa skip its results-to-metrics aliasing, which
        silently dropped the only three metrics that had ever resolved.
        """
        out = attach_measured_metrics(dict(self._phase1()), self._phase1())
        assert out["metrics"]["fairness"]["score"] == 0.91
        assert out["metrics"]["content_safety"]["score"] == 0.0

    def test_an_emitted_metric_beats_the_alias(self):
        phase1 = {
            "results": {
                "toxicity": {"score": 0.99, "details": {}},
                "content_safety": {
                    "score": 0.0,
                    "details": {"metrics": {"toxicity": {"score": 0.01}}},
                },
            }
        }
        out = attach_measured_metrics(dict(phase1), phase1)
        assert out["metrics"]["toxicity"]["score"] == 0.01

    def test_nothing_emitted_changes_nothing(self):
        phase1 = {"results": {"fairness": {"score": 0.9, "details": {}}}}
        before = dict(phase1)
        assert attach_measured_metrics(before, phase1) == before

    def test_declaring_a_metric_does_not_supply_it(self):
        """SUPPORTED_METRICS is a claim; this reads only what was emitted."""
        phase1 = {
            "results": {"ghost": {"score": 1.0, "details": {"not_metrics": {"x": 1}}}}
        }
        assert collect_measured_metrics(phase1) == {}

    def test_malformed_results_do_not_explode(self):
        for bad in (
            None,
            {},
            {"results": None},
            {"results": [1, 2]},
            {"results": {"a": None}},
            {"results": {"a": {"details": 7}}},
        ):
            assert collect_measured_metrics(bad) == {}
