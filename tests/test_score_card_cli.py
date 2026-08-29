"""The score-card command, which runs GOPAL rather than a copy of it.

The rubric used to live in Python here, exported to JSON so a browser could
read it, with parity fixtures and a CI job keeping the two implementations in
step. It is a GOPAL policy now, so those tests are gone with the machinery they
guarded: there is no second implementation left to disagree with the first.

What is worth asserting instead is that the command really does reach the
policy, and that it refuses to invent a number when it cannot.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
POLICY = (
    REPO
    / "aicertify"
    / "opa_policies"
    / "global"
    / "v1"
    / "documentation"
    / "model_card_score.rego"
)

needs_gopal = pytest.mark.skipif(
    shutil.which("opa") is None or not POLICY.exists(),
    reason="needs the opa binary and the pinned gopal checkout",
)

CARD = """---
license: apache-2.0
datasets:
  - squad
---

# Fixture

## Model Details

A card with enough prose in a couple of sections to score above zero and well
below the threshold, which is what a real model card does.

## Uses

### Direct Use

Classifying short English passages where a person reviews the result before
anything happens because of it.

## Training Details

### Training Data

SQuAD, deduplicated and filtered for length before use.
"""


@needs_gopal
class TestScoringRunsTheePolicy:
    def test_the_rubric_is_not_reimplemented_here(self):
        """
        No Python file should carry section weights or content bands any more.
        If one does, the drift this refactor removed has come back.
        """
        offenders = []
        for path in (REPO / "aicertify").rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "QUALITY_LEVELS" in text or "content_quality_thresholds" in text:
                offenders.append(str(path.relative_to(REPO)))
        assert not offenders, f"the rubric is back in Python: {offenders}"

    def test_a_card_scores_through_gopal(self):
        from aicertify.adapters import score_model_card

        scored = score_model_card(CARD)
        assert 0.0 < scored["completeness"] < 0.8
        assert scored["section_scores"]

    def test_an_unreadable_card_returns_nothing_rather_than_zero(self):
        """Zero would read as a real measurement of a very bad card."""
        from aicertify.adapters import score_model_card

        assert score_model_card("") == {}
        assert score_model_card("# Title only, no sections\n") == {}

    def test_the_heading_table_comes_from_the_policy(self):
        from aicertify.adapters import load_heading_sources

        table = load_heading_sources()
        assert len(table) == 9
        # Both conventions real cards use, read from GOPAL rather than restated.
        assert "uses" in table["intended_use"]["primary_uses"]
        assert "intended uses & limitations" in table["intended_use"]["primary_uses"]


@needs_gopal
class TestTheCommand:
    def _run(self, *args):
        return subprocess.run(
            [
                sys.executable,
                "-c",
                "from aicertify.cli import main; import sys; "
                "sys.argv=['aicertify',*sys.argv[1:]]; raise SystemExit(main())",
                *args,
            ],
            capture_output=True,
            text=True,
            cwd=REPO,
            timeout=300,
        )

    def test_it_scores_a_local_card(self, tmp_path):
        card = tmp_path / "README.md"
        card.write_text(CARD)
        out = self._run("score-card", "--file", str(card), "--json")
        assert out.returncode == 0, out.stderr
        payload = json.loads(out.stdout)
        assert 0.0 < payload["completeness"] < 1.0
        assert payload["threshold"] == 0.8
        assert payload["passes"] is False

    def test_it_names_the_gopal_version_that_produced_the_number(self, tmp_path):
        """
        A figure quoted in a post has to be reproducible, and the rubric is a
        GOPAL policy now, so the GOPAL version is what identifies it. Without it
        a reader who reruns this later and gets something else cannot tell a
        changed rubric from a wrong claim.
        """
        card = tmp_path / "README.md"
        card.write_text(CARD)
        out = self._run("score-card", "--file", str(card), "--json")
        assert out.returncode == 0, out.stderr
        versions = json.loads(out.stdout)["versions"]
        assert set(versions) == {"aicertify", "gopal"}
        assert versions["gopal"] != "unknown"

    def test_an_unreadable_card_exits_non_zero(self, tmp_path):
        empty = tmp_path / "README.md"
        empty.write_text("")
        out = self._run("score-card", "--file", str(empty))
        assert out.returncode == 2
        assert "no readable model card" in (out.stderr + out.stdout)
