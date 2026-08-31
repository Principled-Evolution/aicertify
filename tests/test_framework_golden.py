"""
Golden tests: every advertised framework must deliver the verdicts it declares.

v0.8.0 fixed a defect where an EU AI Act evaluation reported 4 verdicts out of
29, and UK, NIST, BFS, legal, healthcare and education evaluations reported none
at all, while the process exited successfully. AICertify was querying
`data.<package>.report_output`, which only four policies define. Nothing failed,
because nothing asserted that a framework produces verdicts. The CLI still
prints "OPA Evaluation: Successful" and exits 0 whether a run produced 29
verdicts or none, so no exit code separates a working release from an empty one.

These tests assert it, in three layers, because each catches something the
others let through.

  1. The library is present.       declared >= a floor per framework.
  2. Everything declared arrives.  delivered == declared.
  3. Nothing is unaccounted for.   every evaluated package is known to the index.

What "declared" is measured against decides whether layer 2 works at all. It is
taken from gopal's coverage.json, filtered to the framework, and never from the
packages the evaluation returned. Deriving it from the returned packages is
fail-open in a way that is easy to miss: a package that fails to evaluate is
absent from the results and therefore absent from the expectation too, so the
count agrees with itself and the test passes.

That is not hypothetical. industry_specific.education.v1.fairness_and_equity
raised an eval-time conflict and returned nothing, and the two counts agreed at
4 and 4. Against the index, which says 5 packages declare a verdict for
education, the same run reads 5 declared and 4 delivered.

Layer 1 exists because layer 2 is vacuous on its own. With the policy submodule
missing or empty, nothing is declared and nothing is delivered, and
`delivered == declared` holds at zero: a green result meaning the question was
never asked.

Layer 3 covers the other direction. Layers 1 and 2 both read the index to decide
what to expect, so a policy present in the tree but absent from coverage.json is
invisible to both: never expected, never delivered, never missed. Layer 3
compares against what OPA actually evaluated instead.

These are slow. Each framework is a real OPA evaluation over the vendored policy
library, which is what makes them worth having: no mock can regress the way the
real query did.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aicertify.opa_core.decision_index import load_index
from aicertify.opa_core.evaluator import OpaEvaluator
from aicertify.opa_core.extraction import (
    _package_values_from,
    extract_results_from_packages,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_DIR = REPO_ROOT / "aicertify" / "opa_policies"
COVERAGE_FILE = POLICY_DIR / "docs" / "coverage" / "coverage.json"
CONTRACT_FILE = REPO_ROOT / "aicertify" / "_demo" / "sample_contract.json"

#: A clone without --recursive has no policies to read. Skipping is right for a
#: contributor's first checkout; CI fetches submodules and installs OPA, so
#: these do run there, and a green CI without them would be the vacuous pass
#: this file exists to prevent.
needs_policies = pytest.mark.skipif(
    not COVERAGE_FILE.is_file(),
    reason="gopal submodule not checked out; run: git submodule update --init",
)


# Release-blocking floors: 80% of the count declared today, never below 1.
#
# One rule rather than fourteen judgements, and it is the only guard against the
# policy library shrinking. Layer 2 does not cover that case: a policy removed
# from gopal outright drops out of both the declared and the delivered count, so
# the two still agree and the delivery check passes. The floor is what notices.
#
# 80% leaves room for a framework to be reorganised or a policy to be retired
# without failing a release, while a framework being gutted or a submodule
# pinned far behind still fails. Frameworks with a single policy floor at 1,
# which is as meaningful as a floor on one policy can be: it exists or it does
# not.
#
# Declared counts measured against aicertify/_demo/sample_contract.json and the
# pinned submodule. Regenerate with the same evaluation if the library moves.
MINIMUM_EXPECTED: dict[str, int] = {
    # framework        floor   declared today
    "eu_ai_act": 23,  # 29
    "aviation": 9,  # 12
    "uk": 4,  # 6
    "education": 4,  # 5
    "nist": 4,  # 5
    "global": 4,  # 5
    "bfs": 3,  # 4
    "operational": 3,  # 4
    "legal": 2,  # 3
    "healthcare": 1,  # 2
    "standards": 1,  # 2
    "india": 1,  # 1
    "brazil": 1,  # 1
    "automotive": 1,  # 1
}

#: Frameworks known to deliver fewer verdicts than they declare, with the cause.
#: Empty, and the mechanism is kept for the next one.
#:
#: Strict, so an exemption cannot outlive the defect: once the gap closes the
#: test passes, and pytest reports an unexpected pass as a failure, forcing the
#: entry out rather than leaving it as a permanent exception. That is how the
#: education entry was removed. It covered
#: industry_specific.education.v1.fairness_and_equity, which raised
#: eval_conflict_error and delivered nothing for three policies; when the gopal
#: submodule was bumped past the fix, this failed with XPASS(strict) and printed
#: the instruction to delete it.
KNOWN_DELIVERY_GAPS: dict[str, str] = {}


def _delivery_params():
    """Framework parameters for layer 2, with known gaps marked xfail(strict)."""
    for framework in sorted(MINIMUM_EXPECTED):
        reason = KNOWN_DELIVERY_GAPS.get(framework)
        marks = [pytest.mark.xfail(reason=reason, strict=True)] if reason else []
        yield pytest.param(framework, marks=marks)


@pytest.fixture(scope="module")
def contract() -> dict:
    return json.loads(CONTRACT_FILE.read_text())


@pytest.fixture(scope="module")
def evaluator() -> OpaEvaluator:
    ev = OpaEvaluator()
    ev.load_policies()
    return ev


@pytest.fixture(scope="module")
def index() -> dict:
    return load_index(str(POLICY_DIR))


def _package_prefix(evaluator: OpaEvaluator, framework: str) -> str:
    """
    The package prefix for a framework, taken from the folder the evaluator
    actually resolves rather than from a hand-written map, so the two cannot
    disagree about which policies belong to a framework.
    """
    folders = evaluator.find_matching_policy_folders(framework)
    assert folders, f"{framework}: no policy folder matches this name"
    return folders[0].split("opa_policies/")[-1].replace("/", ".")


def _declared(index: dict, prefix: str) -> list[str]:
    """Packages the policy library says reach a verdict for this framework."""
    return [
        pkg
        for pkg, d in index.items()
        if pkg.startswith(prefix + ".") and d.reports_a_verdict
    ]


#: One real OPA evaluation per framework, shared by the layers that need it.
#: Three layers over fourteen frameworks is forty-two tests, and evaluating the
#: library afresh for each would be forty-two full runs to answer fourteen
#: questions. The fixtures below are module-scoped for the same reason.
_EVALUATIONS: dict[str, tuple] = {}


def _delivered(evaluator: OpaEvaluator, framework: str, contract: dict):
    """(evaluated packages, verdicts) from a real OPA run, evaluated once."""
    if framework not in _EVALUATIONS:
        raw = evaluator.evaluate_by_folder_name(framework, contract)
        assert not (
            isinstance(raw, dict) and "error" in raw
        ), f"{framework}: evaluation failed: {raw.get('error')}"
        packages, _ = _package_values_from(raw)
        _EVALUATIONS[framework] = (
            packages,
            extract_results_from_packages(packages, str(POLICY_DIR)),
        )
    return _EVALUATIONS[framework]


@needs_policies
@pytest.mark.slow
class TestEveryAdvertisedFrameworkDeliversVerdicts:
    @pytest.mark.parametrize("framework", sorted(MINIMUM_EXPECTED))
    def test_the_policy_library_is_present(self, framework, evaluator, index):
        """
        Layer 1. Without this, the delivery check below passes against an empty
        policy directory, which is the shape of the defect it guards.
        """
        declared = _declared(index, _package_prefix(evaluator, framework))
        floor = MINIMUM_EXPECTED[framework]
        assert len(declared) >= floor, (
            f"{framework}: only {len(declared)} policies declare a verdict, "
            f"floor is {floor}. The policy submodule may be missing, truncated "
            f"or pinned behind."
        )

    @pytest.mark.parametrize("framework", _delivery_params())
    def test_every_declared_verdict_is_delivered(
        self, framework, evaluator, contract, index
    ):
        """
        Layer 2, and the regression itself: 26 of the EU AI Act's 29 policies
        declared a verdict, delivered nothing, and the run exited successfully.
        """
        prefix = _package_prefix(evaluator, framework)
        declared = set(_declared(index, prefix))
        packages, verdicts = _delivered(evaluator, framework, contract)

        # Verdicts carry titles, so the shortfall is reported by package: a
        # count alone does not say which policies went missing.
        evaluated = {p for p in packages if p.startswith(prefix + ".")}
        silent = sorted(declared - evaluated)

        assert len(verdicts) == len(declared), (
            f"{framework}: {len(declared)} policies declare a verdict but "
            f"{len(verdicts)} were delivered. "
            f"Packages that declare one and returned nothing: {silent or 'none'}. "
            f"A package returning nothing is usually an evaluation-time error; "
            f"run gopal's scripts/check-eval-conflicts.sh."
        )

    @pytest.mark.parametrize("framework", sorted(MINIMUM_EXPECTED))
    def test_no_evaluated_package_is_unknown_to_the_index(
        self, framework, evaluator, contract, index
    ):
        """
        Layer 3. A package OPA evaluates but coverage.json does not describe is
        dropped without trace, and the layers above cannot see it because they
        both read the index to decide what to expect.
        """
        packages, _ = _delivered(evaluator, framework, contract)
        unknown = sorted(p for p in packages if p not in index)
        assert not unknown, (
            f"{framework}: {len(unknown)} evaluated package(s) are absent from "
            f"gopal's coverage.json and are silently excluded from every report: "
            f"{unknown[:5]}. Regenerate coverage.json in gopal, or bump the "
            f"submodule to a commit that includes them."
        )


@needs_policies
class TestTheGoldenTableItself:
    """
    The floors are only useful if they cover what the product advertises. A
    framework left out of the table is tested by nothing, which is how the
    original defect went unnoticed across six frameworks at once.
    """

    def test_the_table_is_populated(self):
        assert MINIMUM_EXPECTED, (
            "MINIMUM_EXPECTED is empty, so every golden test above is "
            "parametrised over nothing and passes without evaluating anything."
        )

    def test_no_framework_has_a_zero_floor(self):
        zeroes = sorted(f for f, n in MINIMUM_EXPECTED.items() if n < 1)
        assert not zeroes, (
            f"{zeroes} have a floor below 1, which lets the delivery check pass "
            f"against an empty policy library."
        )

    def test_known_gaps_name_a_framework_in_the_table(self):
        """
        A gap entry for a framework the table does not cover marks nothing, so
        the exemption would look applied while the framework went unchecked.
        """
        stray = sorted(set(KNOWN_DELIVERY_GAPS) - set(MINIMUM_EXPECTED))
        assert not stray, (
            f"{stray} are listed in KNOWN_DELIVERY_GAPS but absent from "
            f"MINIMUM_EXPECTED, so the exemption applies to no test."
        )

    def test_every_framework_resolves_to_a_policy_folder(self, evaluator):
        unresolved = sorted(
            f for f in MINIMUM_EXPECTED if not evaluator.find_matching_policy_folders(f)
        )
        assert not unresolved, (
            f"{unresolved} have a floor but match no policy folder, so the "
            f"golden tests for them would error rather than check anything."
        )
