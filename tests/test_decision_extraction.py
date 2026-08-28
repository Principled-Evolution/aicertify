"""
Tests for issue #78: AICertify could only report on 4 of gopal's 91 policies.

It queried `data.<package>.report_output`, which four policies define. The
other 87 published their verdicts under other names, so evaluations against
the UK, NIST, BFS, legal or global sets reported nothing at all while still
exiting successfully.

These cover the two things most likely to go wrong in the fix: reporting a
detector's verdict upside down, and reporting a policy that reached no
conclusion as a failure it never declared.
"""

from pathlib import Path

import pytest

from aicertify.opa_core.decision_index import (
    PolicyDescriptor,
    load_index,
)
from aicertify.opa_core.extraction import (
    extract_results_from_packages,
    synthesise_policy_result,
)

POLICY_DIR = str(Path(__file__).resolve().parents[1] / "aicertify" / "opa_policies")

NORMAL = PolicyDescriptor(
    package="test.normal",
    title="Normal",
    decision_rule="allow",
    true_means="compliant",
)
DETECTOR = PolicyDescriptor(
    package="test.detector",
    title="Detector",
    decision_rule="flag_for_review",
    true_means="concern",
)
LIBRARY = PolicyDescriptor(package="test.lib", is_library=True)


class TestVerdictSense:
    def test_allow_true_is_a_pass(self):
        r = synthesise_policy_result("test.normal", {"allow": True}, NORMAL)
        assert r is not None and r.result is True

    def test_allow_false_is_a_failure(self):
        r = synthesise_policy_result("test.normal", {"allow": False}, NORMAL)
        assert r is not None and r.result is False

    def test_detector_true_means_a_concern_so_it_fails(self):
        """
        The inversion that matters. A prohibited-practice detector returns true
        when it has found something wrong. Reporting that as a pass would
        invert the finding on the policies where being wrong costs the most.
        """
        r = synthesise_policy_result(
            "test.detector", {"flag_for_review": True}, DETECTOR
        )
        assert r is not None and r.result is False
        assert (r.details or {}).get("detector") is True

    def test_detector_false_means_nothing_found_so_it_passes(self):
        r = synthesise_policy_result(
            "test.detector", {"flag_for_review": False}, DETECTOR
        )
        assert r is not None and r.result is True


class TestUndefinedIsNotFalse:
    """In Rego an undefined value is not `false`; it means no conclusion."""

    @pytest.mark.parametrize(
        "value", [{}, {"allow": None}, {"allow": "yes"}, {"allow": 1}]
    )
    def test_no_boolean_verdict_is_omitted_not_failed(self, value):
        assert synthesise_policy_result("test.normal", value, NORMAL) is None

    def test_libraries_are_omitted(self):
        assert synthesise_policy_result("test.lib", {"allow": True}, LIBRARY) is None

    def test_unknown_package_is_omitted(self):
        assert synthesise_policy_result("test.unknown", {"allow": True}, None) is None


class TestMetrics:
    def test_report_metrics_are_carried_through(self):
        value = {
            "allow": False,
            "report": {
                "metrics": {"bias": {"name": "Bias assessed", "control_passed": False}}
            },
        }
        r = synthesise_policy_result("test.normal", value, NORMAL)
        assert r is not None and r.metrics is not None
        assert r.metrics["bias"]["control_passed"] is False

    def test_policy_metrics_used_when_there_is_no_report(self):
        value = {
            "allow": True,
            "policy_metrics": {"m": {"name": "M", "control_passed": True}},
        }
        r = synthesise_policy_result("test.normal", value, NORMAL)
        assert r is not None and r.metrics is not None and "m" in r.metrics

    def test_decision_only_policies_say_so(self):
        r = synthesise_policy_result("test.normal", {"allow": True}, NORMAL)
        assert r is not None and r.metrics is None
        assert (r.details or {}).get("detail_level") == "decision only"


COVERAGE_FILE = Path(POLICY_DIR) / "docs" / "coverage" / "coverage.json"

#: A clone without --recursive has no policies to read. Skipping is right for a
#: contributor's first checkout; CI fetches submodules so these do run there,
#: and a green CI without them would be the vacuous pass this fix is about.
needs_policies = pytest.mark.skipif(
    not COVERAGE_FILE.is_file(),
    reason="gopal submodule not checked out; run: git submodule update --init",
)


@needs_policies
class TestIndexAgainstTheRealLibrary:
    """These read the vendored gopal checkout, so they fail if the pin regresses."""

    def test_index_names_a_decision_for_every_policy(self):
        index = load_index(POLICY_DIR)
        assert index, "coverage.json missing from the gopal submodule"
        reporting = [d for d in index.values() if d.reports_a_verdict]
        assert len(reporting) >= 80, (
            f"only {len(reporting)} policies name a decision rule; "
            "the submodule may predate primary_decision"
        )

    def test_libraries_are_excluded(self):
        index = load_index(POLICY_DIR)
        assert not any(d.reports_a_verdict for d in index.values() if d.is_library)

    def test_the_decision_rule_is_not_always_allow(self):
        """
        Guessing `allow` would have missed several policies, which is why the
        rule name is read from the library rather than assumed.
        """
        names = {
            d.decision_rule
            for d in load_index(POLICY_DIR).values()
            if d.reports_a_verdict
        }
        assert len(names) > 1 and "allow" in names

    def test_extraction_covers_far_more_than_report_output(self):
        index = load_index(POLICY_DIR)
        packages = {
            p: {d.decision_rule: True}
            for p, d in index.items()
            if d.reports_a_verdict and d.true_means != "concern"
        }
        results = extract_results_from_packages(packages, POLICY_DIR)
        assert len(results) >= 80, f"expected 80+ verdicts, built {len(results)}"
        assert all(r.result for r in results)
