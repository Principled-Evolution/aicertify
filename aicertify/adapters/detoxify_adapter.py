"""Detoxify to GOPAL.

[Detoxify](https://github.com/unitaryai/detoxify) is the most widely used open
toxicity classifier. `Detoxify("original").predict(texts)` returns a dict keyed
by class name:

    {"toxicity": [...], "severe_toxicity": [...], "obscene": [...],
     "threat": [...], "insult": [...], "identity_attack": [...]}

with one float per input text. Passing a single string instead of a list gives
a scalar per class rather than a list, which is the shape most people hit first
and the one most likely to be handled wrongly, so both are accepted here.

The mapping to GOPAL:

    toxicity, averaged  ->  metrics.toxicity.score          (compared against 0.1)
    toxicity, maximum   ->  metrics.toxicity.max_toxicity   (compared against 0.7)

Those are two different questions and GOPAL keeps them apart. An average over a
thousand benign outputs hides the one that was not; a maximum fed into a 0.1
threshold fails almost every real system and gets the check switched off. Both
are emitted so each policy reads the one it asked for.

The other five classes have no canonical GOPAL name. They are returned under
`metrics.toxicity.categories` so nothing is silently dropped, and policies that
do not read them ignore them.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

__all__ = ["from_detoxify"]

# Detoxify's own class names, after the renaming it applies internally
# (toxic -> toxicity, identity_hate -> identity_attack, severe_toxic ->
# severe_toxicity). "sexual_explicit" appears in the unbiased checkpoint only.
_CATEGORIES = (
    "toxicity",
    "severe_toxicity",
    "obscene",
    "threat",
    "insult",
    "identity_attack",
    "sexual_explicit",
)


def _as_floats(value: Any) -> List[float]:
    """Coerce one class's predictions to a list of floats.

    Detoxify returns a numpy scalar for a single string and a list of floats
    for a list of strings. numpy types are not JSON-serialisable, and a value
    that reaches OPA as a numpy float32 fails there rather than here, which is
    a long way from the cause.
    """
    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        return []
    if isinstance(value, Sequence):
        items = list(value)
    else:
        items = [value]

    out: List[float] = []
    for item in items:
        try:
            out.append(float(item))
        except (TypeError, ValueError):
            continue
    return out


def from_detoxify(predictions: Mapping[str, Any]) -> Dict[str, Any]:
    """Convert Detoxify output into a GOPAL input fragment.

    Args:
        predictions: what ``Detoxify(...).predict(...)`` returned. Accepts both
            the scalar-per-class shape from a single string and the
            list-per-class shape from a list of strings.

    Returns:
        ``{"metrics": {"toxicity": {...}}}``, or ``{}`` if nothing usable was
        found. An empty result is the honest answer for an empty run: emitting
        a zero would report an unmeasured system as clean on a scale where
        lower is better.

    Example:
        >>> from detoxify import Detoxify                        # doctest: +SKIP
        >>> raw = Detoxify("original").predict(outputs)          # doctest: +SKIP
        >>> from_detoxify(raw)                                   # doctest: +SKIP
        {'metrics': {'toxicity': {'score': 0.014, 'max_toxicity': 0.83, ...}}}
    """
    if not isinstance(predictions, Mapping):
        return {}

    scores = _as_floats(predictions.get("toxicity"))
    if not scores:
        return {}

    toxicity: Dict[str, Any] = {
        "score": sum(scores) / len(scores),
        "max_toxicity": max(scores),
        "sample_size": len(scores),
    }

    # Everything else Detoxify measured, kept rather than dropped. No canonical
    # GOPAL name reads these today; a policy that grows one will find them here.
    categories: Dict[str, Dict[str, float]] = {}
    for name in _CATEGORIES:
        if name == "toxicity":
            continue
        values = _as_floats(predictions.get(name))
        if values:
            categories[name] = {
                "score": sum(values) / len(values),
                "max": max(values),
            }
    if categories:
        toxicity["categories"] = categories

    return {"metrics": {"toxicity": toxicity}}
