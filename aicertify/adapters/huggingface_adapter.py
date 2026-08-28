"""Hugging Face model cards to GOPAL.

A model card is a `README.md` with YAML frontmatter, and it is the most widely
published description of an AI system in existence. It is not a compliance
document and this adapter does not pretend otherwise: it establishes what a
card structurally contains, which is a fraction of what a regulation asks. See
GOPAL's `docs/model-cards-vs-compliance.md` for that accounting.

What it does supply is real, and two things come out of a card:

**Documentation sections.** `ModelCardEvaluator` scores nine sections from
Mitchell et al., *Model Cards for Model Reporting*. Hugging Face cards do not
use those nine names. They use whatever the author wrote, and in practice that
is one of several conventions: the current template ("Uses", "Bias, Risks, and
Limitations", "Training Details"), the older one still on most popular
repositories ("Intended uses & limitations", "Limitations and bias", "Training
data"), or something ad hoc. Matching only the current template would score
`bert-base-uncased` and `gpt2` as almost entirely undocumented, which says
more about the matcher than the cards. The alias table below was written
against real cards, listed in the tests.

**Reported results.** `model-index` in the frontmatter is a structured record
of benchmark results, one metric block per task and dataset. Where present it
is far better evidence than prose, because it carries a number.

Nothing here is inferred. A section absent from the card is absent from the
output, and a card claiming no results produces no metrics.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Mapping, Optional, Tuple

__all__ = ["from_model_card", "from_model_index", "SUBSECTION_SOURCES"]


# (section, subsection) -> the headings that establish it, lowercased.
#
# ModelCardEvaluator does not score sections, it scores named subsections
# inside them, and a section whose subsections are all empty scores zero.
# So the mapping has to be at subsection granularity or a card with eight
# well-written sections scores 0.00, which is what the first version of this
# adapter did.
#
# Only mappings where the heading genuinely establishes that subsection are
# listed. Several subsections have no entry at all: a model card almost never
# states decision thresholds, intersectional results, or the motivation for
# choosing an evaluation set. Leaving those unmapped is the point rather than a
# gap in the table. The resulting score is partial by construction, because a
# model card really does answer part of what a regulator asks and no more.
SUBSECTION_SOURCES: Dict[str, Dict[str, Tuple[str, ...]]] = {
    "model_details": {
        "model_type": (
            "model details",
            "model description",
            "model summary",
            "model overview",
            "model architecture",
        ),
    },
    "intended_use": {
        "primary_uses": (
            "direct use",
            "intended use",
            "intended uses",
            "intended uses & limitations",
            "intended uses and limitations",
            "uses",
            "downstream use",
            "usage",
        ),
        "out_of_scope_uses": (
            "out-of-scope use",
            "out of scope use",
            "misuse",
            "limitations and bias",
            "known limitations",
        ),
    },
    "factors": {
        "relevant_factors": (
            "factors",
            "relevant factors",
            "bias, risks, and limitations",
            "risks, limitations and biases",
            "limitations and bias",
        ),
        "evaluation_factors": ("evaluation factors", "testing data, factors & metrics"),
    },
    "metrics": {
        "performance_metrics": (
            "metrics",
            "evaluation",
            "evaluation results",
            "results",
        ),
    },
    "evaluation_data": {
        "datasets": (
            "evaluation data",
            "testing data",
            "test data",
            "evaluation dataset",
        ),
    },
    "training_data": {
        "datasets": (
            "training data",
            "training dataset",
            "training details",
            "training",
        ),
        "preprocessing": ("preprocessing", "data preprocessing", "training procedure"),
    },
    "quantitative_analyses": {
        "unitary_results": (
            "evaluation results",
            "results",
            "benchmark results",
            "performance",
        ),
    },
    "ethical_considerations": {
        "data_bias": (
            "bias, risks, and limitations",
            "risks, limitations and biases",
            "limitations and bias",
            "bias",
        ),
        "risks": (
            "risks",
            "bias, risks, and limitations",
            "risks, limitations and biases",
            "ethical considerations",
        ),
        "mitigations": ("recommendations", "mitigations", "mitigation"),
    },
    "caveats_recommendations": {
        "limitations": (
            "limitations",
            "known limitations",
            "limitations and bias",
            "caveats",
        ),
        "recommendations": ("recommendations", "caveats and recommendations"),
    },
}


def _split_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Separate YAML frontmatter from the markdown body.

    Returns an empty mapping when there is no frontmatter or PyYAML is absent,
    rather than failing: the body is still worth parsing.
    """
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not match:
        return {}, text
    raw, body = match.group(1), match.group(2)
    try:
        import yaml

        data = yaml.safe_load(raw)
    except Exception:  # noqa: BLE001 - frontmatter is a bonus, not a requirement
        return {}, body
    return (data if isinstance(data, dict) else {}), body


def _headed_sections(body: str) -> List[Tuple[str, str]]:
    """Every markdown heading with the text beneath it, in document order.

    A section runs to the next heading of the same or higher level, not to the
    next heading of any level, so a section whose prose lives in subsections is
    not read as empty. SmolLM2's card writes "## Training" with everything
    under "### Model" and "### Hardware"; cutting at the next heading of any
    level scored that card as not documenting its training at all.
    """
    matches = list(re.finditer(r"^(#{1,6})[ \t]+(.+?)[ \t]*$", body, re.M))
    out: List[Tuple[str, str]] = []
    for i, m in enumerate(matches):
        level = len(m.group(1))
        end = len(body)
        for later in matches[i + 1 :]:
            if len(later.group(1)) <= level:
                end = later.start()
                break
        out.append((m.group(2).strip(), body[m.end() : end].strip()))
    return out


def _normalise(heading: str) -> str:
    """Lowercase and strip markdown, numbering and trailing punctuation."""
    h = re.sub(r"[*_`]", "", heading).strip().lower()
    h = re.sub(r"^\d+[.)]\s*", "", h)
    return h.rstrip(":").strip()


def _title_of(body: str) -> Optional[str]:
    """The card's H1, which is the closest thing it has to a model name."""
    m = re.search(r"^#[ \t]+(.+?)[ \t]*$", body, re.M)
    return m.group(1).strip() if m else None


def _matches(heading: str, alias: str) -> bool:
    """Whether a heading means this alias.

    Prefix rather than equality, so "Model Card for Llama 3" matches
    "model card for" and "Uses" does not accidentally match "Usage notes"
    through a bare substring test.
    """
    h = _normalise(heading)
    return h == alias or h.startswith(alias)


def from_model_card(card: str) -> Dict[str, Any]:
    """Convert a Hugging Face model card into a GOPAL input fragment.

    Args:
        card: the raw text of the card, frontmatter included. Get it with
            ``huggingface_hub.ModelCard.load(repo_id).content``, or read a
            local ``README.md``.

    Returns:
        A fragment carrying ``documentation.model_card`` with whichever of the
        nine sections the card actually contains, plus ``metrics`` derived from
        ``model-index`` when the frontmatter has one, plus the declared facts
        the frontmatter states outright. Returns ``{}`` for an empty card.

        Sections the card does not contain are omitted, not emptied.
        ``ModelCardEvaluator`` scores an absent section as missing, which is
        the correct reading of a card that does not discuss its training data.

    Example:
        >>> from huggingface_hub import ModelCard              # doctest: +SKIP
        >>> card = ModelCard.load("bert-base-uncased").content # doctest: +SKIP
        >>> fragment = from_model_card(card)                   # doctest: +SKIP
        >>> sorted(fragment["documentation"]["model_card"])    # doctest: +SKIP
        ['ethical_considerations', 'factors', 'intended_use', ...]
    """
    if not isinstance(card, str) or not card.strip():
        return {}

    front, body = _split_frontmatter(card)
    sections = _headed_sections(body)

    model_card: Dict[str, Any] = {}
    for section_id, subsections in SUBSECTION_SOURCES.items():
        filled: Dict[str, str] = {}
        for subsection, aliases in subsections.items():
            collected: List[str] = []
            for alias in aliases:
                for heading, content in sections:
                    if _matches(heading, alias) and content:
                        collected.append(content)
            if collected:
                filled[subsection] = "\n\n".join(dict.fromkeys(collected))
        if filled:
            model_card[section_id] = filled

    # Frontmatter states some things outright that the prose only implies.
    # A `datasets:` key names the training data in machine-readable form,
    # which is a stronger statement than a paragraph mentioning a corpus.
    if front:
        title = _title_of(body)
        if title:
            model_card.setdefault("model_details", {}).setdefault("model_name", title)
        descriptors = [
            str(front[k]) for k in ("pipeline_tag", "library_name") if front.get(k)
        ]
        if descriptors:
            model_card.setdefault("model_details", {}).setdefault(
                "model_type", ", ".join(descriptors)
            )
        datasets = front.get("datasets")
        if datasets:
            named = ", ".join(
                str(d)
                for d in (
                    datasets if isinstance(datasets, (list, tuple)) else [datasets]
                )
            )
            model_card.setdefault("training_data", {})
            existing = model_card["training_data"].get("datasets")
            model_card["training_data"]["datasets"] = (
                f"{named}\n\n{existing}" if existing else named
            )

    fragment: Dict[str, Any] = {}
    if model_card:
        fragment["documentation"] = {"model_card": model_card}

    if front:
        declared = _declared_from_frontmatter(front)
        if declared:
            fragment.setdefault("documentation", {}).update(declared)

        metrics = from_model_index(front)
        if metrics:
            fragment.update(metrics)

    return fragment


def _declared_from_frontmatter(front: Mapping[str, Any]) -> Dict[str, Any]:
    """Facts the frontmatter states outright, rather than describes.

    Only fields where presence in the YAML *is* the assertion. A `license` key
    is a declared licence. A `datasets` key names the training data. Nothing
    here is inferred from prose, because a card that mentions a licence in a
    sentence has not declared one in a machine-readable way, and treating the
    two as equivalent is how a documentation score stops meaning anything.
    """
    out: Dict[str, Any] = {}
    if front.get("license"):
        out["license"] = front["license"]
    datasets = front.get("datasets")
    if datasets:
        out["training_datasets"] = (
            list(datasets) if isinstance(datasets, (list, tuple)) else [datasets]
        )
    if front.get("base_model"):
        base = front["base_model"]
        out["base_model"] = list(base) if isinstance(base, (list, tuple)) else [base]
    return out


def from_model_index(frontmatter: Mapping[str, Any]) -> Dict[str, Any]:
    """Extract reported benchmark results from `model-index`.

    `model-index` is a list of models, each with `results`, each result naming
    a `task`, a `dataset` and a list of `metrics` of the form
    ``{"type": "accuracy", "value": 0.91, "name": "Accuracy"}``. Some carry
    ``verified: true``, meaning Hugging Face re-ran the evaluation itself.

    Returns ``{"metrics": {"reported": {...}}}`` keyed by metric type, or
    ``{}`` when there is no usable index.

    These land under ``metrics.reported.*`` rather than a canonical GOPAL name
    on purpose. A card's self-reported accuracy on a benchmark of the author's
    choosing is a claim about a dataset, not a measurement of the deployed
    system, and quietly promoting it to ``metrics.accuracy.score`` would let a
    good SST-2 number satisfy a policy asking whether *this* system is accurate
    in *its* context. Read them, cite them, but do not let them answer a
    question they were not asked.
    """
    if not isinstance(frontmatter, Mapping):
        return {}
    index = frontmatter.get("model-index") or frontmatter.get("model_index")
    if not isinstance(index, (list, tuple)):
        return {}

    reported: Dict[str, Any] = {}
    for entry in index:
        if not isinstance(entry, Mapping):
            continue
        for result in entry.get("results") or []:
            if not isinstance(result, Mapping):
                continue
            task = _name_of(result.get("task"))
            dataset = _name_of(result.get("dataset"))
            for metric in result.get("metrics") or []:
                if not isinstance(metric, Mapping):
                    continue
                mtype = metric.get("type") or metric.get("name")
                value = metric.get("value")
                if not mtype or not isinstance(value, (int, float)):
                    continue
                record = {
                    "value": float(value),
                    "verified": bool(metric.get("verified", False)),
                }
                if task:
                    record["task"] = task
                if dataset:
                    record["dataset"] = dataset
                reported.setdefault(str(mtype), []).append(record)

    return {"metrics": {"reported": reported}} if reported else {}


def _name_of(block: Any) -> Optional[str]:
    """The human name of a model-index task or dataset block."""
    if isinstance(block, Mapping):
        for key in ("name", "type"):
            if block.get(key):
                return str(block[key])
    elif isinstance(block, str):
        return block
    return None
