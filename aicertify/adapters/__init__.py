"""Adapters from popular evaluation tools to GOPAL's canonical metric names.

Every adapter here is a pure function: it takes what some third-party tool
already produced and returns a GOPAL input fragment, shaped as
``{"metrics": {...}}`` using the canonical names in GOPAL's
``helper_functions/metrics.rego``.

That return shape is deliberately the same one you would write by hand. Merge
it into an AICertify contract's ``context``, or dump it to JSON and pass it
straight to ``opa eval``. Nothing here imports the tool it adapts, so you can
use the Detoxify adapter on a saved Detoxify result without installing
Detoxify, and none of it drags a dependency into anyone who is not using it.

Two rules every adapter follows:

* **Absent is not zero.** Nothing measurable in, nothing out. Returning a 0.0
  toxicity for an empty run would report an unmeasured system as clean, and
  GOPAL would believe it.
* **The name describes the statistic.** ``metrics.toxicity.score`` is an
  aggregate compared against 0.1 and ``metrics.toxicity.max_toxicity`` is the
  worst single output compared against 0.7. Adapters never conflate them.
"""

from aicertify.adapters.detoxify_adapter import from_detoxify
from aicertify.adapters.huggingface_adapter import (
    from_model_card,
    from_model_index,
)

__all__ = ["from_detoxify", "from_model_card", "from_model_index"]
