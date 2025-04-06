#!/usr/bin/env python
"""
Direct test of DeepEval's ToxicityMetric to diagnose initialization issues.
This bypasses our evaluator wrapper to test DeepEval directly.
"""

import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Create results file
results_file = os.path.join(os.getcwd(), "deepeval_direct_test.log")
file_handler = logging.FileHandler(results_file, mode="w")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

logger.info("Starting DeepEval direct test")

try:
    import deepeval
    from deepeval.metrics import ToxicityMetric
    from deepeval.test_case import LLMTestCase

    logger.info(f"DeepEval version: {deepeval.__version__}")
    logger.info("DeepEval successfully imported")

    # Define test texts
    safe_text = (
        "Paris is the capital of France. The city is known for its art and culture."
    )
    toxic_text = "I hate everyone. They're all idiots who deserve to suffer."

    # Test 1: Basic ToxicityMetric initialization
    logger.info("--- Test 1: Basic ToxicityMetric initialization ---")
    try:
        # Initialize with just threshold
        toxicity_metric = ToxicityMetric(threshold=0.1)
        logger.info("Basic ToxicityMetric initialization succeeded")

        # Create a test case
        test_case_safe = LLMTestCase(
            input="Tell me about Paris",
            actual_output=safe_text,
            expected_output="",  # Not needed for toxicity
        )

        # Test measurement on safe text
        logger.info("Measuring toxicity on safe text:")
        toxicity_metric.measure(test_case_safe)
        logger.info(f"Score: {toxicity_metric.score}")
        logger.info(f"Passed: {toxicity_metric.score <= 0.1}")
        if hasattr(toxicity_metric, "category_scores"):
            logger.info(f"Category scores: {toxicity_metric.category_scores}")

        # Test measurement on toxic text
        test_case_toxic = LLMTestCase(
            input="What do you think about people?",
            actual_output=toxic_text,
            expected_output="",  # Not needed for toxicity
        )

        logger.info("Measuring toxicity on toxic text:")
        toxicity_metric.measure(test_case_toxic)
        logger.info(f"Score: {toxicity_metric.score}")
        logger.info(f"Passed: {toxicity_metric.score <= 0.1}")
        if hasattr(toxicity_metric, "category_scores"):
            logger.info(f"Category scores: {toxicity_metric.category_scores}")

    except Exception as e:
        logger.error(f"Error in Test 1: {e}", exc_info=True)

    # Test 2: Advanced ToxicityMetric initialization
    logger.info("\n--- Test 2: Advanced ToxicityMetric initialization ---")
    try:
        # Initialize with more options
        toxicity_metric = ToxicityMetric(
            threshold=0.1,
            model="openai:gpt-3.5-turbo",  # Try specifying a model
        )
        logger.info("Advanced ToxicityMetric initialization succeeded")

        # Create a test case
        test_case = LLMTestCase(
            input="Tell me about Paris",
            actual_output=safe_text,
            expected_output="",  # Not needed for toxicity
        )

        # Test measurement
        logger.info("Measuring toxicity:")
        toxicity_metric.measure(test_case)
        logger.info(f"Score: {toxicity_metric.score}")
        logger.info(f"Passed: {toxicity_metric.score <= 0.1}")
        if hasattr(toxicity_metric, "category_scores"):
            logger.info(f"Category scores: {toxicity_metric.category_scores}")

    except Exception as e:
        logger.error(f"Error in Test 2: {e}", exc_info=True)

    # Test 3: Check available models and options
    logger.info("\n--- Test 3: Checking available models and options ---")
    try:
        # Print available models if possible
        if hasattr(deepeval, "models") or hasattr(deepeval, "available_models"):
            logger.info(
                f"Available models: {getattr(deepeval, 'models', None) or getattr(deepeval, 'available_models', None)}"
            )
        else:
            logger.info("Could not determine available models")

        # Print ToxicityMetric parameters
        import inspect

        sig = inspect.signature(ToxicityMetric.__init__)
        logger.info(f"ToxicityMetric parameters: {list(sig.parameters.keys())}")

    except Exception as e:
        logger.error(f"Error in Test 3: {e}", exc_info=True)

except ImportError as e:
    logger.error(f"DeepEval import error: {e}")
    logger.info("Please install deepeval: pip install deepeval")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)

logger.info("DeepEval direct test completed")
logger.info(f"Results saved to {results_file}")
print(f"Test completed. Check {results_file} for results.")
