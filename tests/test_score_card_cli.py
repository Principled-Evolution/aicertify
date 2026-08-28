"""The score-card command and the rubric it publishes.

`aicertify score-card <repo>` prints a number that also appears in the GOPAL
playground, computed there by a second implementation in JavaScript. The rubric
is exported to JSON so that implementation reads the same weights, thresholds
and heading aliases rather than a copy of them, and these tests keep the export
honest.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
EXPORTER = REPO / "scripts" / "export_model_card_rubric.py"
RUBRIC = REPO / "aicertify" / "adapters" / "model_card_rubric.json"
FIXTURES = REPO / "aicertify" / "adapters" / "model_card_parity_fixtures.json"


class TestTheExportedRubric:
    def test_it_is_current(self):
        """
        Fails when the rubric changed in Python and the committed JSON did not.
        A stale export means the playground scores cards by yesterday's rules
        while the CLI uses today's, and the two publish different numbers.
        """
        out = subprocess.run(
            [sys.executable, str(EXPORTER), "--check"],
            capture_output=True,
            text=True,
            cwd=REPO,
            timeout=300,
        )
        assert out.returncode == 0, out.stderr or out.stdout

    def test_it_carries_everything_the_score_depends_on(self):
        rubric = json.loads(RUBRIC.read_text())
        assert set(rubric["sections"]) == {
            "model_details",
            "intended_use",
            "factors",
            "metrics",
            "evaluation_data",
            "training_data",
            "quantitative_analyses",
            "ethical_considerations",
            "caveats_recommendations",
        }
        for section in rubric["sections"].values():
            assert section["subsections"]
            assert isinstance(section["weight"], (int, float))
        assert (
            rubric["content_thresholds"]["minimal"]
            < rubric["content_thresholds"]["partial"]
        )
        assert rubric["quality_levels"]["missing"] == 0.0
        assert rubric["heading_sources"]

    def test_the_weights_sum_to_one(self):
        """Otherwise completeness is not on the 0-1 scale it is compared on."""
        rubric = json.loads(RUBRIC.read_text())
        total = sum(s["weight"] for s in rubric["sections"].values())
        assert total == pytest.approx(1.0)


class TestTheParityFixtures:
    def test_python_still_produces_the_recorded_scores(self):
        """
        The JavaScript scorer is checked against these numbers. If Python drifts
        from them without the fixtures being regenerated, the browser is held to
        a standard Python no longer meets.
        """
        from aicertify.adapters import from_model_card
        from aicertify.evaluators.documentation import ModelCardEvaluator

        evaluator = ModelCardEvaluator()
        for case in json.loads(FIXTURES.read_text())["cases"]:
            result = evaluator.evaluate(
                from_model_card(case["card"]).get("documentation", {})
            )
            emitted = (result.details or {}).get("metrics", {}).get("model_card", {})
            assert emitted.get("completeness", 0.0) == pytest.approx(
                case["expected"]["completeness"]
            ), case["name"]

    def test_the_fixtures_span_a_useful_range(self):
        """
        Four identical scores would pass parity while testing almost nothing.
        """
        scores = {
            c["expected"]["completeness"]
            for c in json.loads(FIXTURES.read_text())["cases"]
        }
        assert len(scores) >= 3
        assert min(scores) == 0.0
        assert max(scores) > 0.3


class TestTheCommand:
    def _run(self, *args):
        return subprocess.run(
            [
                sys.executable,
                "-c",
                "from aicertify.cli import main; import sys; sys.argv=['aicertify',*sys.argv[1:]]; "
                "raise SystemExit(main())",
                *args,
            ],
            capture_output=True,
            text=True,
            cwd=REPO,
            timeout=300,
        )

    def test_it_scores_a_local_card(self, tmp_path):
        card = tmp_path / "README.md"
        card.write_text(json.loads(FIXTURES.read_text())["cases"][0]["card"])
        out = self._run("score-card", "--file", str(card), "--json")
        assert out.returncode == 0, out.stderr
        payload = json.loads(out.stdout)
        assert 0.0 < payload["completeness"] < 1.0
        assert payload["threshold"] == 0.8

    def test_it_stamps_what_produced_the_number(self):
        """
        A figure quoted in a blog post has to be reproducible. Without the
        versions, a reader who reruns it later and gets something else cannot
        tell a changed rubric from a wrong claim.
        """
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(json.loads(FIXTURES.read_text())["cases"][0]["card"])
            card = fh.name
        out = self._run("score-card", "--file", card, "--json")
        assert out.returncode == 0, out.stderr
        versions = json.loads(out.stdout)["versions"]
        assert set(versions) == {"aicertify", "gopal", "rubric"}
        assert versions["rubric"] != "unknown"

    def test_an_unreadable_card_fails_rather_than_scoring_zero(self, tmp_path):
        """
        Zero would read as a real measurement of a very bad card.
        """
        empty = tmp_path / "README.md"
        empty.write_text("")
        out = self._run("score-card", "--file", str(empty))
        assert out.returncode == 2
        assert "no readable model card" in (out.stderr + out.stdout)
