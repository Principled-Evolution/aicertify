"""Answer "what do I have to feed this policy set?" without running it.

Every GOPAL policy declares the input it needs in a ``RequiredMetrics`` comment
header, and the parser for those headers has been in ``rego_parser`` all along.
Nothing surfaced it, so the only way to discover that the EU AI Act policies want
77 distinct fields was to run an evaluation and read the failures.

This module turns those headers into something answerable up front, and the
``explain`` and ``init-contract`` CLI commands print it.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .policy_loader import PolicyLoader
from .rego_parser import parse_rego_file_metadata

logger = logging.getLogger(__name__)


# Roots that an evaluator fills in at run time. Everything else has to be
# declared by whoever writes the contract, because no evaluator can observe it:
# nothing in a transcript reveals whether a conformity assessment was completed.
#
# This is a prefix heuristic, not a guarantee. It is honest about that in the
# CLI output, and the authoritative answer is always a real evaluation.
# GOPAL 2.0.0 removed the legacy spellings, so a measured value is spelled
# metrics.<name> and nothing else. "results" stays because AICertify mirrors
# results.<name> onto metrics.<name> before evaluating, so a contract written
# against the older AICertify shape still resolves.
EVALUATOR_ROOTS = frozenset(
    {
        "metrics",
        "results",
    }
)

# Flat score fields the shared GOPAL helpers once read directly off the input.
# Empty since GOPAL 2.0.0 retired fairness_score, content_safety_score and
# risk_management_score; kept as the seam for any future flat field.
EVALUATOR_LEAF_FIELDS: frozenset = frozenset()

# Which evaluator is the usual source, for the fields we can attribute. Used only
# to annotate output, never to decide anything.
EVALUATOR_HINTS = {
    "fairness": "fairness",
    "fairness_score": "fairness",
    "content_safety": "content_safety",
    "content_safety_score": "content_safety",
    "toxicity": "content_safety",
    "risk_management": "risk_management",
    "risk_management_score": "risk_management",
    "accuracy": "accuracy",
}


@dataclass
class PolicyInfo:
    """One policy file and what it asks for."""

    package: str
    path: str
    required_metrics: List[str] = field(default_factory=list)
    required_params: Dict[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str:
        """The trailing segment of the package, e.g. ``transparency``."""
        return self.package.rsplit(".", 1)[-1] if self.package else Path(self.path).stem


@dataclass
class FrameworkIntrospection:
    """Everything discoverable about one framework's input requirements."""

    query: str
    policies: List[PolicyInfo] = field(default_factory=list)
    # field path -> the policies that ask for it
    declared_fields: Dict[str, List[str]] = field(default_factory=dict)
    evaluator_fields: Dict[str, List[str]] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    param_sources: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def policy_count(self) -> int:
        return len(self.policies)

    @property
    def field_count(self) -> int:
        return len(self.declared_fields) + len(self.evaluator_fields)


def is_evaluator_field(field_path: str) -> bool:
    """True when an evaluator normally produces this field at run time."""
    if field_path in EVALUATOR_LEAF_FIELDS:
        return True
    return field_path.split(".", 1)[0] in EVALUATOR_ROOTS


def evaluator_for(field_path: str) -> Optional[str]:
    """Best guess at which evaluator produces a field, or None."""
    parts = field_path.split(".")
    for part in parts:
        if part in EVALUATOR_HINTS:
            return EVALUATOR_HINTS[part]
    return None


def available_frameworks(loader: Optional[PolicyLoader] = None) -> List[str]:
    """Framework identifiers that ``explain`` and ``init-contract`` accept."""
    loader = loader or PolicyLoader()
    names: List[str] = []
    for category, subcategory in loader.get_all_categories():
        names.append(f"{category}/{subcategory}" if subcategory else category)
    return sorted(set(names))


def introspect(
    query: str, loader: Optional[PolicyLoader] = None
) -> FrameworkIntrospection:
    """Collect the input requirements of every policy matching ``query``.

    ``query`` is resolved the same way ``--policy`` is, so ``eu_ai_act``,
    ``international/eu_ai_act`` and ``uk`` all work.

    Raises:
        LookupError: if the query matches no policies.
    """
    loader = loader or PolicyLoader()
    policy_files = loader.get_policies_by_category(query)
    if not policy_files:
        raise LookupError(
            f"No policies matched '{query}'. "
            f"Available: {', '.join(available_frameworks(loader))}"
        )

    result = FrameworkIntrospection(query=query)

    for policy_file in sorted(set(policy_files)):
        # Tests declare nothing and would only add noise.
        if policy_file.endswith("_test.rego"):
            continue
        try:
            metadata = parse_rego_file_metadata(policy_file)
        except FileNotFoundError:
            logger.warning("Policy file disappeared while reading: %s", policy_file)
            continue
        except Exception:
            logger.exception("Could not parse %s", policy_file)
            continue

        info = PolicyInfo(
            package=metadata.package_name or "",
            path=policy_file,
            required_metrics=sorted(metadata.required_metrics),
            required_params=dict(metadata.required_params),
        )
        result.policies.append(info)

        for metric in info.required_metrics:
            bucket = (
                result.evaluator_fields
                if is_evaluator_field(metric)
                else result.declared_fields
            )
            bucket.setdefault(metric, []).append(info.name)

        for param, default in info.required_params.items():
            # First definition wins, matching get_required_params_for_folder.
            result.params.setdefault(param, default)
            result.param_sources.setdefault(param, []).append(info.name)

    for mapping in (
        result.declared_fields,
        result.evaluator_fields,
        result.param_sources,
    ):
        for key in mapping:
            mapping[key] = sorted(set(mapping[key]))

    result.policies.sort(key=lambda p: p.package or p.path)
    return result


def _assign(tree: Dict[str, Any], dotted_path: str, value: Any) -> None:
    """Set ``tree['a']['b'] = value`` for a dotted path ``a.b``.

    A conflict, where one field is both a leaf and the parent of another, leaves
    the existing branch alone rather than silently dropping half the fields.
    """
    parts = dotted_path.split(".")
    node = tree
    for part in parts[:-1]:
        existing = node.get(part)
        if not isinstance(existing, dict):
            if existing is not None:
                logger.debug(
                    "Field %s conflicts with an existing leaf at %s; keeping the branch",
                    dotted_path,
                    part,
                )
            node[part] = {}
        node = node[part]
    leaf = parts[-1]
    if isinstance(node.get(leaf), dict):
        return
    node[leaf] = value


def build_field_skeleton(
    introspection: FrameworkIntrospection,
    placeholder: Any = None,
) -> Dict[str, Any]:
    """Nest the declared field paths into the object shape a policy reads."""
    tree: Dict[str, Any] = {}
    for path in sorted(introspection.declared_fields):
        _assign(tree, path, placeholder)
    return tree


def build_contract_skeleton(
    introspection: FrameworkIntrospection,
    application_name: str = "your-application",
    model_name: str = "your-model",
) -> Dict[str, Any]:
    """A contract with every field this framework needs, ready to fill in.

    The declared fields go under ``context``, which is the part of a contract
    that carries facts about the system rather than about a single interaction.
    Evaluator-produced fields are deliberately left out: filling them in by hand
    would mean asserting your own fairness and toxicity scores.
    """
    skeleton = build_field_skeleton(introspection)

    evaluator_note = sorted(introspection.evaluator_fields)
    contract: Dict[str, Any] = {
        "application_name": application_name,
        "model_info": {
            "model_name": model_name,
            "model_version": "v1",
            "metadata": {},
        },
        "interactions": [
            {
                "input_text": "Replace with a real prompt from your system.",
                "output_text": "Replace with the response your system produced.",
                "metadata": {},
            }
        ],
        "context": skeleton,
    }

    if introspection.params:
        contract["params"] = dict(sorted(introspection.params.items()))

    contract["_aicertify"] = {
        "generated_for": introspection.query,
        "policies": introspection.policy_count,
        "declared_fields": len(introspection.declared_fields),
        "note": (
            "Fields under context are declarations no evaluator can observe; "
            "replace every null. params carries each policy's documented "
            "defaults and can be deleted to accept them."
        ),
        "provided_by_evaluators": evaluator_note,
    }
    return contract


def unfilled_paths(tree: Any, prefix: str = "") -> List[str]:
    """Dotted paths in a skeleton still holding ``None``."""
    out: List[str] = []
    if isinstance(tree, dict):
        for key, value in tree.items():
            child = f"{prefix}.{key}" if prefix else key
            if value is None:
                out.append(child)
            else:
                out.extend(unfilled_paths(value, child))
    return out


def _deep_merge_preserving(
    base: Dict[str, Any], incoming: Dict[str, Any]
) -> Dict[str, Any]:
    """Merge ``incoming`` into ``base`` without overwriting anything already set.

    Nested dictionaries merge key by key. A scalar already present in ``base``
    always wins, which is what keeps a declaration from displacing a measurement.
    """
    merged = dict(base)
    for key, value in incoming.items():
        if key in merged:
            if isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = _deep_merge_preserving(merged[key], value)
            # Otherwise keep what is already there.
            continue
        merged[key] = value
    return merged


def _drop_nulls(value: Any) -> Any:
    """Strip keys still holding ``None``, recursively.

    A scaffolded contract is full of nulls for fields the author has not filled
    in. Passing them through would be worse than leaving them out: a policy
    reading ``input.decision.significant`` would see an explicit null rather than
    an absent field, and a rule testing ``is_boolean`` would report the system as
    assessed-and-not-significant instead of not assessed at all.
    """
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            if item is None:
                continue
            reduced = _drop_nulls(item)
            if isinstance(reduced, dict) and not reduced:
                continue
            cleaned[key] = reduced
        return cleaned
    return value


def collect_measured_metrics(
    evaluation_results: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Lift each evaluator's canonical metric block out of its result.

    GOPAL reads measured metrics at ``input.metrics.<domain>.<name>``, the
    canonical names in ``helper_functions/metrics.rego``. Evaluator output
    arrives keyed by evaluator name instead, as ``results.<evaluator>``, and the
    only reason three metrics ever resolved is that ``metrics.fairness.score``,
    ``metrics.content_safety.score`` and ``metrics.risk_management.score``
    happen to spell an evaluator name in the middle and ``score`` at the end.
    Nothing else lined up. ``metrics.model_card.completeness`` did not, so no
    policy reading it ever saw a measurement, whatever the gap report said.

    The contract is now explicit: an evaluator publishes canonical metrics by
    putting them under ``details["metrics"]`` in the shape GOPAL reads, and this
    function merges every evaluator's block into one tree that is attached at
    the top level of the OPA input.

    Declaring a metric in ``SUPPORTED_METRICS`` does not supply it. This reads
    what was actually emitted, so an evaluator that names a metric and never
    computes it contributes nothing here.
    """
    collected: Dict[str, Any] = {}
    results = (evaluation_results or {}).get("results") or {}
    if not isinstance(results, dict):
        return collected
    for result in results.values():
        if not isinstance(result, dict):
            continue
        details = result.get("details")
        if not isinstance(details, dict):
            continue
        block = details.get("metrics")
        if isinstance(block, dict):
            collected = _deep_merge_preserving(collected, _drop_nulls(block))
    return collected


def attach_measured_metrics(
    opa_input: Dict[str, Any],
    evaluation_results: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Put canonical measured metrics where GOPAL looks for them.

    Merged over whatever ``input.metrics`` already holds, so the legacy
    ``results`` to ``metrics`` aliasing in ``_transform_input_for_opa`` keeps
    working for the three metrics that relied on it. A canonical metric an
    evaluator actually computed wins over the alias, because it is the more
    specific statement.
    """
    measured = collect_measured_metrics(evaluation_results)
    if not measured:
        return opa_input

    merged = dict(opa_input)

    # Reproduce the results-to-metrics aliasing here rather than leaving it to
    # _transform_input_for_opa, which only applies it when "metrics" is absent.
    # Setting metrics from measured alone would suppress that alias and drop the
    # three metrics that depend on it, so both layers are merged now: the alias
    # underneath, an actually-computed canonical metric on top.
    base: Dict[str, Any] = {}
    existing = merged.get("metrics")
    if isinstance(existing, dict):
        base = existing
    else:
        results = merged.get("results")
        if isinstance(results, dict):
            base = results

    # measured first, so it wins over the alias where the two collide.
    merged["metrics"] = _deep_merge_preserving(measured, base)
    return merged


def merge_declared_context(
    evaluation_results: Optional[Dict[str, Any]],
    contract: Any,
) -> Dict[str, Any]:
    """Combine measured evaluator output with the contract's declared facts.

    GOPAL policies read declarations at the top level of the input document, for
    example ``input.decision.significant`` and ``input.system.high_risk``, so the
    contract's ``context`` is merged in at the top level rather than nested under
    a ``context`` key.

    Measured values win. Evaluator output is layered over the declarations, not
    under them, so a contract cannot assert its own fairness score or claim a
    toxicity level it did not measure. Declarations only fill what no evaluator
    produced.

    ``params`` is carried across untouched; the OPA evaluator merges it with each
    policy's documented defaults.
    """
    results: Dict[str, Any] = dict(evaluation_results or {})

    def _read(name: str) -> Any:
        if isinstance(contract, dict):
            return contract.get(name)
        return getattr(contract, name, None)

    declared: Dict[str, Any] = {}
    for source in ("context", "compliance_context"):
        block = _read(source)
        if isinstance(block, dict) and block:
            declared = _deep_merge_preserving(declared, _drop_nulls(block))

    if not declared:
        merged = results
    else:
        # results first so measurements take precedence over declarations.
        merged = _deep_merge_preserving(results, declared)

    params = _read("params")
    if isinstance(params, dict) and params and "params" not in merged:
        merged["params"] = params

    return merged


def summarise(introspection: FrameworkIntrospection) -> Tuple[int, int, int]:
    """(policies, fields you declare, fields evaluators produce)."""
    return (
        introspection.policy_count,
        len(introspection.declared_fields),
        len(introspection.evaluator_fields),
    )
