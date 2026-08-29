"""Fairlearn to GOPAL.

[Fairlearn](https://fairlearn.org/) is the most widely used fairness toolkit for
Python. A `MetricFrame` computes a metric overall and per group, and exposes the
gap between groups two ways: `difference()`, where 0 means no disparity, and
`ratio()`, where 1 means no disparity.

GOPAL reads `metrics.fairness.score` and compares it with `>=`, so **higher is
better**. Fairlearn's `difference()` points the other way. Handing it over
unchanged would report the fairest possible system as the least fair one, which
is precisely how `is_toxic` once answered `true` for a system with no toxicity
at all.

So `ratio()` is preferred, and not only to dodge the sign. A ratio is already
bounded on [0, 1] with 1 as the ideal, which is the shape a `>= 0.85` threshold
expects, and it is the form the four-fifths rule in fair lending is written in.
A difference is accepted too and converted, with the conversion stated rather
than implied.

Nothing here imports Fairlearn, so a saved result converts without it installed.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

__all__ = ["from_fairlearn"]

# Selection rate is the quantity demographic parity is defined over, so it is
# the default when a frame carries several metrics and the caller has not said
# which one describes fairness.
DEFAULT_METRIC = "selection_rate"


def _scalar(value: Any) -> Optional[float]:
    """A float, or None. numpy scalars included, containers excluded."""
    if value is None or isinstance(value, bool):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if out == out else None  # reject NaN


def _pick(value: Any, metric: str) -> Optional[float]:
    """One number out of a MetricFrame result.

    A frame built with several metrics returns a pandas Series keyed by metric
    name; a frame built with one returns a bare scalar. Both are common and the
    scalar case is the one that quietly breaks a `[metric]` lookup.
    """
    direct = _scalar(value)
    if direct is not None:
        return direct
    if hasattr(value, "get"):
        return _scalar(value.get(metric))
    return None


def from_fairlearn(
    frame: Any = None,
    *,
    metric: str = DEFAULT_METRIC,
    ratio: Optional[float] = None,
    difference: Optional[float] = None,
) -> Dict[str, Any]:
    """Convert a Fairlearn result into a GOPAL input fragment.

    Args:
        frame: a ``MetricFrame``. Its ``ratio()`` is used where available.
        metric: which metric in the frame describes fairness. Ignored for a
            single-metric frame, which returns scalars rather than a Series.
        ratio: a disparity ratio you already have, 1.0 meaning no disparity,
            as from ``demographic_parity_ratio``.
        difference: a disparity difference, 0.0 meaning no disparity, as from
            ``demographic_parity_difference``. Converted to ``1 - difference``.

    Returns:
        ``{"metrics": {"fairness": {...}}}`` with ``score`` on GOPAL's
        higher-is-better scale, or ``{}`` if nothing usable was found. Empty
        rather than a default: a fairness score nobody computed must not read as
        a system that was measured and found fair.

    Example:
        >>> from fairlearn.metrics import MetricFrame, selection_rate  # doctest: +SKIP
        >>> mf = MetricFrame(metrics=selection_rate, y_true=y, y_pred=p,
        ...                  sensitive_features=g)                     # doctest: +SKIP
        >>> from_fairlearn(mf)                                         # doctest: +SKIP
        {'metrics': {'fairness': {'score': 0.667, 'ratio': 0.667, ...}}}
    """
    resolved_ratio = _scalar(ratio)
    resolved_difference = _scalar(difference)
    by_group: Dict[str, float] = {}
    overall: Optional[float] = None

    if frame is not None:
        if resolved_ratio is None and hasattr(frame, "ratio"):
            try:
                resolved_ratio = _pick(frame.ratio(), metric)
            except Exception:  # noqa: BLE001 - a frame that cannot ratio is not fatal
                resolved_ratio = None
        if resolved_difference is None and hasattr(frame, "difference"):
            try:
                resolved_difference = _pick(frame.difference(), metric)
            except Exception:  # noqa: BLE001
                resolved_difference = None
        overall = _pick(getattr(frame, "overall", None), metric)
        by_group = _by_group(getattr(frame, "by_group", None), metric)

    if resolved_ratio is not None:
        score = resolved_ratio
        basis = "ratio"
    elif resolved_difference is not None:
        # 1 - difference, because GOPAL compares with >= and Fairlearn's
        # difference is 0 at its best. Recorded in `basis` so a reader of the
        # document can see which way the number was turned.
        score = 1.0 - resolved_difference
        basis = "1 - difference"
    else:
        return {}

    fairness: Dict[str, Any] = {"score": score, "basis": basis, "metric": metric}
    if resolved_ratio is not None:
        fairness["ratio"] = resolved_ratio
    if resolved_difference is not None:
        fairness["difference"] = resolved_difference
    if overall is not None:
        fairness["overall"] = overall
    if by_group:
        fairness["by_group"] = by_group

    return {"metrics": {"fairness": fairness}}


def _by_group(value: Any, metric: str) -> Dict[str, float]:
    """Per-group values, flattened to plain floats keyed by group name.

    Kept because a single fairness score says a gap exists and not where. A
    policy that fails on it is far more useful with the groups attached.
    """
    if value is None:
        return {}

    # DataFrame: rows are groups, columns are metrics.
    columns = getattr(value, "columns", None)
    if columns is not None:
        if metric not in list(columns):
            return {}
        try:
            value = value[metric]
        except Exception:  # noqa: BLE001
            return {}

    items = getattr(value, "items", None)
    if not callable(items):
        return {}
    out: Dict[str, float] = {}
    for key, item in value.items():
        number = _scalar(item)
        if number is not None:
            out[str(key)] = number
    return out
