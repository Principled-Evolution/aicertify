from langfair.metrics.counterfactual import CounterfactualMetrics
from langfair.metrics.stereotype import StereotypeMetrics

# Check CounterfactualMetrics API
print("CounterfactualMetrics API:")
counterfactual = CounterfactualMetrics()
print("  Methods:", [m for m in dir(counterfactual) if not m.startswith("_")])
print(
    "  evaluate() signature:",
    (
        counterfactual.evaluate.__doc__
        if hasattr(counterfactual, "evaluate")
        else "No evaluate method"
    ),
)

# Check StereotypeMetrics API
print("\nStereotypeMetrics API:")
stereotype = StereotypeMetrics()
print("  Methods:", [m for m in dir(stereotype) if not m.startswith("_")])

# Check if any bias methods exist
bias_methods = [m for m in dir(stereotype) if "bias" in m.lower()]
print("  Bias-related methods:", bias_methods if bias_methods else "None found")
