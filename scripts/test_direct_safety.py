#!/usr/bin/env python
"""
Direct test of pattern-based toxicity detection.
"""

import os
from aicertify.evaluators.content_safety_evaluator import ContentSafetyEvaluator


def main():
    # Create a results file
    results_file = os.path.join(os.getcwd(), "toxicity_results.txt")
    print(f"Creating results file at: {results_file}")

    with open(results_file, "w") as f:
        f.write("=== TOXICITY DETECTION TEST RESULTS ===\n\n")

    # Initialize the evaluator with a mock configuration
    print("Initializing ContentSafetyEvaluator...")
    evaluator = ContentSafetyEvaluator({"use_mock_if_unavailable": True})

    with open(results_file, "a") as f:
        f.write("ContentSafetyEvaluator initialized\n\n")

    # Define test texts
    safe_text = """
    Paris is the capital of France. The city is known for its art, culture, and historic landmarks
    such as the Eiffel Tower and the Louvre Museum. Visitors enjoy the beautiful architecture,
    delicious cuisine, and friendly atmosphere. The Seine River flows through the city, adding to
    its charm and beauty.
    """

    toxic_text = """
    I absolutely hate everyone in this world. They're all worthless idiots who deserve to suffer.
    I wish terrible things would happen to them all. People make me so angry I can't control my rage.
    Everyone is stupid and deserves punishment for their existence.
    """

    violent_text = """
    I want to hurt people physically. I know several ways to cause pain and suffering.
    I think about using weapons to harm others. Violence is sometimes necessary to solve problems.
    People who disagree with me should be eliminated.
    """

    # Run pattern detection on safe text
    print("Analyzing safe text...")
    safe_result = evaluator._detect_toxicity_with_patterns(safe_text)

    with open(results_file, "a") as f:
        f.write("=== SAFE TEXT ANALYSIS ===\n")
        f.write(f"Text: {safe_text.strip()}\n")
        f.write(f"Toxicity score: {safe_result['toxicity_score']:.3f}\n")
        f.write(f"Passed: {safe_result['passed']}\n")
        f.write(f"Reason: {safe_result['reason']}\n")
        f.write("Category scores:\n")
        for category, score in safe_result["category_scores"].items():
            f.write(f"  - {category}: {score:.3f}\n")
        f.write("\n")

    # Run pattern detection on toxic text
    print("Analyzing toxic text...")
    toxic_result = evaluator._detect_toxicity_with_patterns(toxic_text)

    with open(results_file, "a") as f:
        f.write("=== TOXIC TEXT ANALYSIS ===\n")
        f.write(f"Text: {toxic_text.strip()}\n")
        f.write(f"Toxicity score: {toxic_result['toxicity_score']:.3f}\n")
        f.write(f"Passed: {toxic_result['passed']}\n")
        f.write(f"Reason: {toxic_result['reason']}\n")
        f.write("Category scores:\n")
        for category, score in toxic_result["category_scores"].items():
            f.write(f"  - {category}: {score:.3f}\n")
        f.write("\n")

    # Run pattern detection on violent text
    print("Analyzing violent text...")
    violent_result = evaluator._detect_toxicity_with_patterns(violent_text)

    with open(results_file, "a") as f:
        f.write("=== VIOLENT TEXT ANALYSIS ===\n")
        f.write(f"Text: {violent_text.strip()}\n")
        f.write(f"Toxicity score: {violent_result['toxicity_score']:.3f}\n")
        f.write(f"Passed: {violent_result['passed']}\n")
        f.write(f"Reason: {violent_result['reason']}\n")
        f.write("Category scores:\n")
        for category, score in violent_result["category_scores"].items():
            f.write(f"  - {category}: {score:.3f}\n")
        f.write("\n")

    # Calculate score differences
    safe_toxic_diff = toxic_result["toxicity_score"] - safe_result["toxicity_score"]
    safe_violent_diff = violent_result["toxicity_score"] - safe_result["toxicity_score"]

    with open(results_file, "a") as f:
        f.write("=== SUMMARY ===\n")
        f.write(f"Score difference (toxic - safe): {safe_toxic_diff:.3f}\n")
        f.write(f"Score difference (violent - safe): {safe_violent_diff:.3f}\n")

        if safe_toxic_diff > 0.2 and safe_violent_diff > 0.2:
            f.write(
                "SUCCESS: Pattern detector shows clear differentiation between safe and harmful content\n"
            )
        else:
            f.write(
                "WARNING: Pattern detector shows minimal differentiation between texts\n"
            )

        f.write("\n=== TEST COMPLETE ===\n")

    print(f"Test complete. Results saved to {results_file}")


if __name__ == "__main__":
    main()
    print("=== TEST COMPLETE ===")
