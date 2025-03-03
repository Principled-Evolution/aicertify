import langfair
import langfair.metrics
import langfair.metrics.counterfactual
import langfair.metrics.counterfactual.metrics
import langfair.metrics.stereotype

print("LangFair version:", langfair.__version__ if hasattr(langfair, "__version__") else "Unknown")
print("\nCounterfactual module contents:")
for name in sorted(dir(langfair.metrics.counterfactual.metrics)):
    if not name.startswith("__"):
        print(f"  - {name}")

print("\nStereotype module contents:")
for name in sorted(dir(langfair.metrics.stereotype)):
    if not name.startswith("__"):
        print(f"  - {name}")

# Check if specific classes exist
print("\nChecking specific classes:")
print("SentimentBias exists:", "SentimentBias" in dir(langfair.metrics.counterfactual.metrics))
print("BLEUSimilarity exists:", "BLEUSimilarity" in dir(langfair.metrics.counterfactual.metrics))
print("BleuSimilarity exists:", "BleuSimilarity" in dir(langfair.metrics.counterfactual.metrics))
print("RougeScoreSimilarity exists:", "RougeScoreSimilarity" in dir(langfair.metrics.counterfactual.metrics))
print("RougelSimilarity exists:", "RougelSimilarity" in dir(langfair.metrics.counterfactual.metrics)) 