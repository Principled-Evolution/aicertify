"""Tests for the RequiredMetrics / RequiredParams comment-header parser.

The header is how a GOPAL policy declares the input it needs, and
``get_required_metrics_for_folder`` feeds those names straight into evaluator
discovery. A parser that drops entries therefore does not just produce a short
list: it runs the evaluation without the data the policies needed.

The dropped-every-other-line case below is a regression test. The pattern used
``\\s`` for the whitespace around each entry, and ``\\s`` matches newlines, so the
trailing optional group consumed the line break plus the next line's
indentation and the scan resumed halfway down the block. Across the bundled
policy library that silently discarded 160 of 362 declared fields.
"""

from __future__ import annotations

import textwrap

import pytest

from aicertify.opa_core.rego_parser import parse_rego_file_metadata


def write_policy(tmp_path, body: str, name: str = "policy.rego") -> str:
    path = tmp_path / name
    path.write_text(textwrap.dedent(body).lstrip("\n"), encoding="utf-8")
    return str(path)


class TestRequiredMetrics:
    def test_parses_every_entry_not_every_other_one(self, tmp_path):
        """Four declared metrics must parse as four. Regression: it returned two."""
        path = write_policy(
            tmp_path,
            """
            # RequiredMetrics:
            #   - governance.accountable_person_named
            #   - governance.oversight_body_in_place
            #   - governance.lifecycle_roles_defined
            #   - governance.supply_chain_accountability_documented
            #
            # RequiredParams: none
            package test.policy
            """,
        )
        metrics = parse_rego_file_metadata(path).required_metrics
        assert metrics == [
            "governance.accountable_person_named",
            "governance.oversight_body_in_place",
            "governance.lifecycle_roles_defined",
            "governance.supply_chain_accountability_documented",
        ]

    @pytest.mark.parametrize("count", [1, 2, 3, 5, 8, 13])
    def test_parses_blocks_of_any_length(self, tmp_path, count):
        """The old bug halved even-length blocks, so length is parametrised."""
        lines = "\n".join(f"#   - field.number_{i}" for i in range(count))
        path = write_policy(
            tmp_path,
            f"""
            # RequiredMetrics:
            {lines}
            #
            package test.policy
            """.replace("            #   -", "#   -"),
        )
        metrics = parse_rego_file_metadata(path).required_metrics
        assert len(metrics) == count
        assert metrics == [f"field.number_{i}" for i in range(count)]

    def test_ignores_a_trailing_comment_on_an_entry(self, tmp_path):
        path = write_policy(
            tmp_path,
            """
            # RequiredMetrics:
            #   - system.high_risk  # Annex III
            #   - system.deployed
            #
            package test.policy
            """,
        )
        assert parse_rego_file_metadata(path).required_metrics == [
            "system.high_risk",
            "system.deployed",
        ]

    def test_absent_section_yields_no_metrics(self, tmp_path):
        path = write_policy(tmp_path, "package test.policy\n")
        assert parse_rego_file_metadata(path).required_metrics == []

    def test_package_name_is_captured(self, tmp_path):
        path = write_policy(
            tmp_path,
            """
            # RequiredMetrics:
            #   - a.b
            package international.uk.v1.fairness
            """,
        )
        assert (
            parse_rego_file_metadata(path).package_name
            == "international.uk.v1.fairness"
        )


class TestRequiredParams:
    def test_parses_every_param_with_its_default(self, tmp_path):
        """Same off-by-one-line defect applied to the params block."""
        path = write_policy(
            tmp_path,
            """
            # RequiredParams:
            #   - fairness_threshold (default 0.8)
            #   - toxicity_threshold (default 0.7)
            #   - strict_mode (default true)
            #   - label (default "eu")
            #
            package test.policy
            """,
        )
        params = parse_rego_file_metadata(path).required_params
        assert params == {
            "fairness_threshold": 0.8,
            "toxicity_threshold": 0.7,
            "strict_mode": True,
            "label": "eu",
        }

    def test_param_without_a_default_is_none(self, tmp_path):
        path = write_policy(
            tmp_path,
            """
            # RequiredParams:
            #   - some_threshold
            #
            package test.policy
            """,
        )
        assert parse_rego_file_metadata(path).required_params == {
            "some_threshold": None
        }

    def test_whole_number_default_stays_an_int(self, tmp_path):
        path = write_policy(
            tmp_path,
            """
            # RequiredParams:
            #   - retention_days (default 3650)
            #
            package test.policy
            """,
        )
        assert parse_rego_file_metadata(path).required_params == {
            "retention_days": 3650
        }

    def test_none_keyword_is_not_parsed_as_a_param(self, tmp_path):
        """`RequiredParams: none` is prose, not a list, and must stay empty."""
        path = write_policy(
            tmp_path,
            """
            # RequiredMetrics:
            #   - a.b
            #
            # RequiredParams: none
            package test.policy
            """,
        )
        assert parse_rego_file_metadata(path).required_params == {}


class TestAgainstTheBundledLibrary:
    """Guards the fix against the real policies, not just synthetic input."""

    def test_a_known_four_field_policy_reports_four(self):
        from pathlib import Path

        from aicertify.opa_core.policy_loader import PolicyLoader

        policy = (
            Path(PolicyLoader().get_policy_dir())
            / "international/uk/v1/accountability_governance.rego"
        )
        if not policy.exists():
            pytest.skip("gopal submodule not checked out")

        metrics = parse_rego_file_metadata(str(policy)).required_metrics
        assert len(metrics) == 4, f"expected 4 declared metrics, parsed {metrics}"

    def test_parsed_fields_match_what_the_policy_reads(self):
        """Every parsed metric should correspond to an input.* the policy reads.

        Catches a parser that invents or mangles entries, which a count-only
        assertion would miss.
        """
        import re
        from pathlib import Path

        from aicertify.opa_core.policy_loader import PolicyLoader

        policy = (
            Path(PolicyLoader().get_policy_dir())
            / "international/uk/v1/accountability_governance.rego"
        )
        if not policy.exists():
            pytest.skip("gopal submodule not checked out")

        source = policy.read_text(encoding="utf-8")
        read_paths = set(re.findall(r"input\.([a-z_]+\.[a-z_]+)", source))
        for metric in parse_rego_file_metadata(str(policy)).required_metrics:
            assert metric in read_paths, f"{metric} is declared but never read"
