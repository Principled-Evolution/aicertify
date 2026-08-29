"""Score a model card by running GOPAL, not by reimplementing it.

The rubric used to live here, in Python: which sections a card must carry, what
each is worth, how much text counts as content. Putting it in a browser then
meant writing it a second time in JavaScript, with generated fixtures and a CI
job holding the two in step.

It is a policy now, `global/v1/documentation/model_card_score`, and this calls
it. Two things follow. The number here and the number in the playground are the
same number because they come from the same rules rather than from two
implementations that agree today. And the rubric is reviewable, diffable and
tested as Rego, which is what it always was: which sections a card must carry
is a normative judgement about required documentation, not a measurement.

What is still Python is turning markdown into sections. That is input
preparation rather than policy, and the heading table it needs comes from the
policy too, so there is no second copy of that either.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

__all__ = ["score_model_card", "load_heading_sources", "GopalUnavailable"]

POLICY_DIR = (
    Path(__file__).resolve().parent.parent
    / "opa_policies"
    / "global"
    / "v1"
    / "documentation"
)
PACKAGE = "data.global.v1.documentation.model_card_score"


class GopalUnavailable(RuntimeError):
    """The opa binary or the pinned GOPAL checkout is missing.

    Raised rather than falling back to a Python approximation. An approximation
    would produce a number that looks like the real one and is not, which is
    worse than no number: the whole point of moving the rubric into Rego was
    that there is exactly one of it.
    """


def _opa() -> str:
    binary = shutil.which("opa")
    if not binary:
        raise GopalUnavailable(
            "the opa binary is not on PATH. Scoring runs GOPAL rather than a "
            "copy of it, so opa is required. See https://www.openpolicyagent.org/"
        )
    if not (POLICY_DIR / "model_card_score.rego").exists():
        raise GopalUnavailable(
            f"{POLICY_DIR} is missing. Run `git submodule update --init` to "
            "fetch the pinned GOPAL policies."
        )
    return binary


def _query(rule: str, document: Optional[Dict[str, Any]] = None) -> Any:
    """Evaluate one rule of the scoring policy.

    Returns None when the rule is undefined, which Rego uses to say the body did
    not hold. For this policy that means no card was supplied, and it is not the
    same as a score of zero.
    """
    argv = [
        _opa(),
        "eval",
        "-d",
        str(POLICY_DIR / "model_card_score.rego"),
        "--format",
        "json",
        f"{PACKAGE}.{rule}",
    ]
    stdin = None
    if document is not None:
        argv[-1:-1] = ["--stdin-input"]
        stdin = json.dumps(document)

    out = subprocess.run(argv, input=stdin, capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise GopalUnavailable(f"opa eval failed: {out.stderr.strip()[:300]}")

    payload = json.loads(out.stdout or "{}")
    result = payload.get("result")
    if not result:
        return None
    return result[0]["expressions"][0]["value"]


@lru_cache(maxsize=1)
def load_heading_sources() -> Dict[str, Dict[str, list]]:
    """The heading aliases the policy uses, read from the policy.

    Cards do not use the nine section names from the paper; they use the current
    Hugging Face template, the older convention most high-download repositories
    still carry, or whatever their author wrote. That mapping is part of the
    rubric, so it lives in the policy and is read from it rather than kept here
    in a second copy that drifts.
    """
    table = _query("heading_sources")
    if not isinstance(table, dict):
        raise GopalUnavailable("the policy returned no heading_sources table")
    return table


def score_model_card(card: str) -> Dict[str, Any]:
    """Score raw model card text against GOPAL's documentation rubric.

    Args:
        card: the card's text, frontmatter included.

    Returns:
        A dict with ``completeness``, ``quality``, ``section_scores``,
        ``weakest_sections`` and the parsed ``document`` that produced them.
        Returns ``{}`` when the card has no sections the rubric recognises,
        because the policy leaves the score undefined in that case and a zero
        would read as a real measurement of a very bad card.
    """
    from aicertify.adapters.huggingface_adapter import from_model_card

    fragment = from_model_card(card, load_heading_sources())
    if not fragment.get("documentation", {}).get("model_card"):
        return {}

    document = {"documentation": fragment["documentation"]}
    completeness = _query("completeness", document)
    if not isinstance(completeness, (int, float)):
        return {}

    return {
        "completeness": float(completeness),
        "quality": float(_query("quality", document) or 0.0),
        "section_scores": _query("section_scores", document) or {},
        "weakest_sections": _query("weakest_sections", document) or [],
        "document": fragment,
    }
