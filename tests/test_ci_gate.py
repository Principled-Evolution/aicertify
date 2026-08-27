"""Tests for the CI gate example's verdict handling.

The gate's job is to turn an evaluation into an exit code, and the only way it
can be actively harmful is by reporting success when it has not checked
anything. So the cases that matter most here are the ones where no verdict was
produced: a missing contract, an OPA error, and an empty result set. All three
must be exit 2, never 0.

The empty result set is the subtle one. extract_all_policy_results returns [] on
a schema-validation failure as well as on a genuinely empty evaluation, and the
most likely real cause is forgetting `submodules: true` on checkout, which
leaves no policy files to evaluate against. Treating that as a pass would mean a
green required check that verified nothing.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

GATE_PATH = Path(__file__).resolve().parents[1] / "examples/github-actions/gate.py"


def load_gate():
    """Import gate.py by path, since examples/ is not a package."""
    spec = importlib.util.spec_from_file_location("ci_gate_example", GATE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gate():
    if not GATE_PATH.exists():
        pytest.skip("gate.py not present")
    return load_gate()


def run_gate(gate, monkeypatch, argv, opa_results=None, raise_exc=None, extracted=None):
    """Drive gate.main() with the evaluation stubbed out."""
    monkeypatch.setattr(sys, "argv", ["gate.py", *argv])

    async def fake_run(_args):
        if raise_exc is not None:
            raise raise_exc
        return {"opa_results": opa_results or {}, "report_path": "reports/r.md"}

    monkeypatch.setattr(gate, "run", fake_run)

    if extracted is not None:
        import aicertify.opa_core.extraction as extraction

        monkeypatch.setattr(
            extraction, "extract_all_policy_results", lambda _results: extracted
        )
    return gate.main()


class Result:
    """Stand-in for the PolicyResult shape the gate reads."""

    def __init__(self, name, result):
        self.name = name
        self.result = result


class TestNoVerdictIsNeverAPass:
    def test_missing_contract_is_exit_2(self, gate, monkeypatch, tmp_path):
        assert (
            run_gate(
                gate,
                monkeypatch,
                ["--contract", str(tmp_path / "nope.json"), "--policy", "uk"],
            )
            == 2
        )

    def test_evaluation_raising_is_exit_2(self, gate, monkeypatch, tmp_path):
        contract = tmp_path / "c.json"
        contract.write_text("{}", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert (
            run_gate(
                gate,
                monkeypatch,
                ["--contract", str(contract), "--policy", "uk"],
                raise_exc=RuntimeError("boom"),
            )
            == 2
        )

    def test_opa_error_is_exit_2(self, gate, monkeypatch, tmp_path):
        contract = tmp_path / "c.json"
        contract.write_text("{}", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert (
            run_gate(
                gate,
                monkeypatch,
                ["--contract", str(contract), "--policy", "uk"],
                opa_results={"error": "no matching policy folders"},
            )
            == 2
        )

    def test_zero_verdicts_is_exit_2_even_with_fail_on_none(
        self, gate, monkeypatch, tmp_path
    ):
        """The submodule-not-checked-out case.

        --fail-on none suppresses policy denials, but it must not suppress
        "nothing was evaluated". Otherwise the most likely CI misconfiguration
        produces a green check.
        """
        contract = tmp_path / "c.json"
        contract.write_text("{}", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert (
            run_gate(
                gate,
                monkeypatch,
                ["--contract", str(contract), "--policy", "uk", "--fail-on", "none"],
                opa_results={"result": {}},
                extracted=[],
            )
            == 2
        )


class TestVerdicts:
    def test_all_passing_is_exit_0(self, gate, monkeypatch, tmp_path):
        contract = tmp_path / "c.json"
        contract.write_text("{}", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert (
            run_gate(
                gate,
                monkeypatch,
                ["--contract", str(contract), "--policy", "uk", "--fail-on", "any"],
                extracted=[Result("A", True), Result("B", True)],
            )
            == 0
        )

    def test_a_denial_with_fail_on_any_is_exit_1(self, gate, monkeypatch, tmp_path):
        contract = tmp_path / "c.json"
        contract.write_text("{}", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert (
            run_gate(
                gate,
                monkeypatch,
                ["--contract", str(contract), "--policy", "uk", "--fail-on", "any"],
                extracted=[Result("A", True), Result("B", False)],
            )
            == 1
        )

    def test_a_denial_with_fail_on_none_is_exit_0(self, gate, monkeypatch, tmp_path):
        contract = tmp_path / "c.json"
        contract.write_text("{}", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert (
            run_gate(
                gate,
                monkeypatch,
                ["--contract", str(contract), "--policy", "uk", "--fail-on", "none"],
                extracted=[Result("A", False)],
            )
            == 0
        )

    def test_summary_json_records_every_policy(self, gate, monkeypatch, tmp_path):
        contract = tmp_path / "c.json"
        contract.write_text("{}", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        run_gate(
            gate,
            monkeypatch,
            ["--contract", str(contract), "--policy", "uk", "--fail-on", "none"],
            extracted=[Result("A", True), Result("B", False)],
        )
        summary = json.loads((tmp_path / "compliance-summary.json").read_text())
        assert summary["total"] == 2
        assert summary["passed"] == 1
        assert summary["failed"] == 1
        assert {p["name"]: p["passed"] for p in summary["policies"]} == {
            "A": True,
            "B": False,
        }

    def test_step_summary_is_written_when_github_provides_one(
        self, gate, monkeypatch, tmp_path
    ):
        contract = tmp_path / "c.json"
        contract.write_text("{}", encoding="utf-8")
        summary_file = tmp_path / "step-summary.md"
        monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))
        monkeypatch.chdir(tmp_path)
        run_gate(
            gate,
            monkeypatch,
            ["--contract", str(contract), "--policy", "uk", "--fail-on", "none"],
            extracted=[Result("Policy A", True)],
        )
        assert "Policy A" in summary_file.read_text(encoding="utf-8")

    def test_a_missing_step_summary_path_does_not_fail_the_gate(
        self, gate, monkeypatch, tmp_path
    ):
        contract = tmp_path / "c.json"
        contract.write_text("{}", encoding="utf-8")
        monkeypatch.setenv(
            "GITHUB_STEP_SUMMARY", str(tmp_path / "no" / "such" / "f.md")
        )
        monkeypatch.chdir(tmp_path)
        assert (
            run_gate(
                gate,
                monkeypatch,
                ["--contract", str(contract), "--policy", "uk", "--fail-on", "any"],
                extracted=[Result("A", True)],
            )
            == 0
        )
