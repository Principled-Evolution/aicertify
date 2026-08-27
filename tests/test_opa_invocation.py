"""Tests for how AICertify invokes the `opa` binary.

Two regressions live here, and they share a failure mode: the evaluation
appeared to succeed while producing nothing.

The YAML one is the worse of the two. `opa eval --data <dir>` walks the whole
tree and parses every .yaml/.json it finds as a data document. The gopal policy
library ships GitHub issue-template forms under `.github/ISSUE_TEMPLATE/`, and
those collide with each other:

    .github/ISSUE_TEMPLATE/new_framework.yml: merge error

OPA then exits 2 having evaluated nothing. Every policy query came back empty
and the caller received a report reading "Total Policies: 0" rather than an
error, so `aicertify demo` printed "Demo complete" over an empty deliverable.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from aicertify.opa_core.evaluator import (
    OPA_IGNORE_PATTERNS,
    opa_ignore_flags,
)


class TestIgnoreFlags:
    def test_flags_are_pairs_of_ignore_and_pattern(self):
        flags = opa_ignore_flags()
        assert len(flags) == 2 * len(OPA_IGNORE_PATTERNS)
        assert flags[0::2] == ["--ignore"] * len(OPA_IGNORE_PATTERNS)
        assert flags[1::2] == OPA_IGNORE_PATTERNS

    @pytest.mark.parametrize(
        "pattern",
        [
            ".github",  # the issue-template forms that caused the merge error
            "*.yml",
            "*.yaml",
            "*.json",  # example fixtures under examples/
            "custom",  # a user's private policies
            "dist",  # built bundles, if someone runs the build in place
        ],
    )
    def test_the_patterns_that_matter_are_present(self, pattern):
        assert pattern in OPA_IGNORE_PATTERNS

    def test_patterns_are_unique(self):
        assert len(OPA_IGNORE_PATTERNS) == len(set(OPA_IGNORE_PATTERNS))


class TestEveryInvocationSitePassesIgnores:
    """Guards against a fourth call site being added without the flags.

    This is a source check rather than a behavioural one, deliberately: the
    original defect was one invocation out of three lacking the flags, and no
    amount of testing the other two would have caught it.
    """

    def test_no_opa_eval_command_omits_the_ignore_flags(self):
        source = (
            Path(__file__).resolve().parents[1] / "aicertify/opa_core/evaluator.py"
        ).read_text(encoding="utf-8")

        # Every command list that invokes `opa eval` should reach the shared
        # helper, either by splatting it or by splicing it in.
        eval_sites = source.count('"eval",')
        helper_uses = source.count("opa_ignore_flags()")

        # One use is the definition's own return, so subtract it.
        assert helper_uses - 1 >= eval_sites, (
            f"{eval_sites} `opa eval` invocation(s) but only "
            f"{helper_uses - 1} use(s) of opa_ignore_flags(). "
            "A new call site probably omitted the flags."
        )


class TestAgainstTheBundledPolicyLibrary:
    """Proves the real tree still trips OPA without the flags, and not with."""

    @staticmethod
    def _policy_dir() -> Path:
        from aicertify.opa_core.policy_loader import PolicyLoader

        return Path(PolicyLoader().get_policy_dir())

    def test_the_offending_yaml_files_are_actually_there(self):
        """If gopal stops shipping these, the ignores stay useful anyway."""
        policy_dir = self._policy_dir()
        if not policy_dir.exists():
            pytest.skip("gopal submodule not checked out")

        templates = policy_dir / ".github/ISSUE_TEMPLATE"
        if not templates.exists():
            pytest.skip("issue templates not present in this gopal revision")
        assert list(
            templates.glob("*.yml")
        ), "expected YAML issue forms; these are what OPA tried to load as data"

    def test_opa_eval_fails_without_the_ignores_and_succeeds_with_them(self, tmp_path):
        """The regression, end to end, against the real policy tree."""
        import shutil
        import subprocess

        opa = shutil.which("opa")
        if opa is None:
            pytest.skip("opa binary not on PATH")
        policy_dir = self._policy_dir()
        if not policy_dir.exists():
            pytest.skip("gopal submodule not checked out")

        input_file = tmp_path / "input.json"
        input_file.write_text("{}", encoding="utf-8")
        query = "data.international.eu_ai_act.v1.transparency.allow"

        def run(extra_flags):
            return subprocess.run(
                [
                    opa,
                    "eval",
                    *extra_flags,
                    "--format",
                    "json",
                    "--data",
                    str(policy_dir),
                    "-i",
                    str(input_file),
                    query,
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        without = run([])
        with_flags = run(opa_ignore_flags())

        # Without the flags OPA reports merge errors instead of a verdict.
        assert '"errors"' in without.stdout or without.returncode != 0, (
            "expected OPA to fail loading the tree without --ignore; if this "
            "now passes, gopal stopped shipping conflicting data files and "
            "this test can be relaxed"
        )
        # With them, a real verdict comes back.
        assert '"errors"' not in with_flags.stdout, with_flags.stdout[:400]
        assert (
            '"result"' in with_flags.stdout
        ), f"expected a verdict for {query}, got: {with_flags.stdout[:400]}"
