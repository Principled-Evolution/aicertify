"""Do the metrics evaluators compute actually reach the policies?

The gap report answers a narrower question than it looks: which metrics some
evaluator *declares*. Declaration turned out to be three steps away from
delivery. An evaluator can declare a metric and never compute it; it can
compute one and never be registered; and it can be registered and still publish
under a path no policy reads.

That last one was the real hole. GOPAL reads measured metrics at
``input.metrics.<domain>.<name>``, while evaluator output is keyed by evaluator
name, so only ``fairness``, ``content_safety`` and ``risk_management`` ever
resolved, purely because those canonical names happen to spell an evaluator
name with ``score`` on the end. ``metrics.model_card.completeness`` did not.

These tests go end to end through GOPAL's own resolver with ``opa eval``, so
they fail if either side of the contract drifts.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from aicertify.opa_core.introspection import attach_measured_metrics

GOPAL = Path(__file__).resolve().parent.parent / "aicertify" / "opa_policies"
METRICS_REGO = GOPAL / "helper_functions" / "metrics.rego"

needs_opa = pytest.mark.skipif(
    shutil.which("opa") is None or not METRICS_REGO.exists(),
    reason="needs the opa binary and the pinned gopal checkout",
)

# What a real run produces, in the shape evaluate_contract_with_phase1_evaluators
# returns. Values are illustrative; the paths are the contract under test.
PHASE1 = {
    "results": {
        "content_safety": {
            "score": 0.0,
            "details": {
                "safety_score": 0.0,
                "metrics": {
                    "toxicity": {
                        "score": 0.29,
                        "max_toxicity": 0.8,
                        "toxic_fraction": 0.33,
                    }
                },
            },
        },
        "model_card": {
            "score": 0.42,
            "details": {
                "metrics": {
                    "model_card": {
                        "score": 0.42,
                        "completeness": 0.42,
                        "quality": 0.65,
                        "section_scores": {"intended_use": 0.5},
                    }
                }
            },
        },
        "audit_logging": {
            "score": 0.8,
            "details": {"metrics": {"audit_logging": {"completeness": 0.8}}},
        },
        "fairness": {"score": 0.91, "details": {}},
        "risk_management": {"score": 0.75, "details": {}},
    }
}

DELIVERED = {
    "metrics.content_safety.score": 0.0,
    "metrics.fairness.score": 0.91,
    "metrics.risk_management.score": 0.75,
    "metrics.toxicity.score": 0.29,
    "metrics.toxicity.max_toxicity": 0.8,
    "metrics.model_card.completeness": 0.42,
    "metrics.audit_logging.completeness": 0.8,
}

# Genuinely not computable in-process. A patient-safety score is a clinical
# measurement; the only thing this codebase could synthesise is documentation
# completeness, and shipping that under a name gated at 0.95 would let a system
# with tidy paperwork clear a patient-safety threshold. Supplied by the
# operator from an external clinical evaluation instead.
NOT_DELIVERED = {
    "metrics.patient_safety.score",
    "metrics.clinical_validation.score",
    "metrics.risk_assessment.score",
}

PROBE = """package probe

import rego.v1
import data.helper_functions.metrics

resolved[n] := v if {
\tsome n in input._probe_names
\tv := metrics.resolve(input, n)
}
"""


def _opa_input():
    """Exactly what the pipeline hands OPA, both transformations applied."""
    opa_input = dict(PHASE1)
    opa_input = attach_measured_metrics(opa_input, PHASE1)
    if "metrics" not in opa_input:  # _transform_input_for_opa
        opa_input["metrics"] = opa_input["results"]
    return opa_input


def _resolve(tmp_path, names):
    doc = _opa_input()
    doc["_probe_names"] = sorted(names)
    probe = tmp_path / "probe.rego"
    probe.write_text(PROBE)
    inp = tmp_path / "input.json"
    inp.write_text(json.dumps(doc))
    out = subprocess.run(
        [
            "opa",
            "eval",
            "-d",
            str(METRICS_REGO),
            "-d",
            str(probe),
            "-i",
            str(inp),
            "data.probe.resolved",
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert out.returncode == 0, out.stderr
    payload = json.loads(out.stdout)
    result = payload.get("result")
    if not result:
        return {}
    return result[0]["expressions"][0]["value"]


@needs_opa
class TestCanonicalMetricsResolveThroughGopal:
    def test_every_delivered_metric_resolves_to_its_value(self, tmp_path):
        got = _resolve(tmp_path, DELIVERED)
        missing = sorted(set(DELIVERED) - set(got))
        assert not missing, (
            f"these canonical metrics no longer reach the policies: {missing}. "
            "An evaluator stopped emitting under details['metrics'], or the "
            "hoist in attach_measured_metrics broke."
        )
        for name, expected in DELIVERED.items():
            assert got[name] == pytest.approx(expected), name

    def test_the_alias_path_still_carries_its_three(self, tmp_path):
        """
        Regression guard. Setting input.metrics from measured metrics alone
        makes _transform_input_for_opa skip its results-to-metrics aliasing,
        which silently drops exactly these three.
        """
        alias_only = {
            "metrics.fairness.score",
            "metrics.content_safety.score",
            "metrics.risk_management.score",
        }
        got = _resolve(tmp_path, alias_only)
        assert (
            set(got) == alias_only
        ), f"alias path broken: missing {sorted(alias_only - set(got))}"

    def test_metrics_needing_external_evidence_stay_absent(self, tmp_path):
        """
        Absent, not zero. These must not acquire a synthesised value: GOPAL
        compares them against 0.90 and 0.95 gates, and resolve() returning
        undefined is what makes the policy fail closed.
        """
        got = _resolve(tmp_path, NOT_DELIVERED)
        assert not got, f"something is now synthesising a clinical score: {sorted(got)}"
