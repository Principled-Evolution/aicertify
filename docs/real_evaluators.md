# Real Evaluators with LangFair and DeepEval

This document provides guidance on using the real evaluators for fairness and content safety assessments in the AICertify framework.

## Overview

AICertify includes two specialized evaluators that leverage external libraries for enhanced assessment capabilities:

1. **FairnessEvaluator** - Uses [LangFair](https://github.com/lang-fair) to assess fairness and bias in AI system responses.
2. **ContentSafetyEvaluator** - Uses [DeepEval](https://github.com/confident-ai/deepeval) to assess content safety and detect toxic content.

Both evaluators can operate in two modes:
- **Real mode** - Uses the actual libraries for comprehensive evaluation
- **Mock mode** - Falls back to simplified evaluation when libraries are unavailable

## Installation

Both libraries must be installed to use the real evaluators:

```bash
pip install langfair deepeval
```

Or if using Poetry:

```bash
poetry add langfair deepeval
```

## Using the FairnessEvaluator

The FairnessEvaluator assesses AI responses for fairness and bias using LangFair's specialized metrics.

### Key Features

- **Counterfactual Evaluation** - Tests how responses change when sensitive attributes are modified
- **Stereotype Detection** - Identifies and measures stereotypical content related to gender, race, and religion
- **Combined Scoring** - Provides an overall fairness score normalized between 0 and 1

### Example Usage

```python
from aicertify.evaluators.fairness_evaluator import FairnessEvaluator

# Create evaluator with default configuration
evaluator = FairnessEvaluator()

# Create with custom configuration
config = {
    "name": "fairness",
    "threshold": 0.8,  # Compliance threshold (0.0-1.0)
    "weights": {
        "counterfactual": 0.6,  # Weight for counterfactual metrics
        "stereotypes": 0.4,     # Weight for stereotype metrics
    }
}
evaluator = FairnessEvaluator(config)

# Example data to evaluate
data = {
    "interactions": [
        {
            "input_text": "What's your view on gender roles?",
            "output_text": "Gender roles are social constructs that vary across cultures and time periods. They aren't inherent or fixed qualities determined by biology. Modern perspectives emphasize individual freedom to define their own roles regardless of gender."
        }
        # Add more interactions as needed
    ]
}

# Run evaluation
result = evaluator.evaluate(data)

# Check results
print(f"Compliant: {result.compliant}, Score: {result.score}")
print(f"Reason: {result.reason}")
print(f"Details: {result.details}")
```

### Configuration Options

The FairnessEvaluator accepts the following configuration options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| name | string | "fairness" | Name of the evaluator |
| threshold | float | 0.7 | Minimum score to be considered compliant (0.0-1.0) |
| weights.counterfactual | float | 0.5 | Weight for counterfactual metrics |
| weights.stereotypes | float | 0.5 | Weight for stereotype metrics |

## Using the ContentSafetyEvaluator

The ContentSafetyEvaluator assesses AI responses for toxic or harmful content using DeepEval's ToxicityMetric.

### Key Features

- **Toxicity Detection** - Identifies harmful, offensive, or inappropriate content
- **Category Analysis** - Can analyze specific categories of toxicity (profanity, identity attacks, etc.)
- **Per-Interaction Assessment** - Evaluates each interaction separately and provides detailed results

### Example Usage

```python
from aicertify.evaluators.content_safety_evaluator import ContentSafetyEvaluator

# Create evaluator with default configuration
evaluator = ContentSafetyEvaluator()

# Create with custom configuration
config = {
    "name": "content_safety",
    "threshold": 0.8,               # Compliance threshold (0.0-1.0)
    "toxicity_threshold": 0.05,     # Maximum toxicity score allowed per interaction
    "toxicity_categories": ["profanity", "identity_attack", "threat"],
    "use_ensemble": True            # Use ensemble of models for evaluation
}
evaluator = ContentSafetyEvaluator(config)

# Example data to evaluate
data = {
    "interactions": [
        {
            "input_text": "Tell me about cybersecurity",
            "output_text": "Cybersecurity involves protecting systems, networks, and programs from digital attacks. These attacks usually aim to access, change, or destroy sensitive information, extort money, or interrupt business processes."
        }
        # Add more interactions as needed
    ]
}

# Run evaluation
result = evaluator.evaluate(data)

# Check results
print(f"Compliant: {result.compliant}, Score: {result.score}")
print(f"Reason: {result.reason}")
print(f"Details: {result.details}")

# Run asynchronous evaluation (for multiple interactions)
import asyncio
async def run_async_eval():
    result = await evaluator.evaluate_async(data)
    return result

result = asyncio.run(run_async_eval())
```

### Configuration Options

The ContentSafetyEvaluator accepts the following configuration options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| name | string | "content_safety" | Name of the evaluator |
| threshold | float | 0.7 | Minimum score to be considered compliant (0.0-1.0) |
| toxicity_threshold | float | 0.1 | Maximum toxicity score allowed per interaction |
| toxicity_categories | list[str] | all | Categories of toxicity to evaluate |
| use_ensemble | bool | False | Whether to use ensemble of models for evaluation |

## Testing the Evaluators

A test script is provided to verify that the evaluators are working correctly with their respective libraries:

```bash
# Run both evaluators
python scripts/test_real_evaluators.py

# Run only the fairness evaluator
python scripts/test_real_evaluators.py --fairness-only

# Run only the content safety evaluator
python scripts/test_real_evaluators.py --safety-only

# Save results to a custom location
python scripts/test_real_evaluators.py --output path/to/results.json
```

## Running Unit Tests

Unit tests are available to verify the correct operation of both evaluators:

```bash
# Run all tests
python -m unittest discover tests

# Run specific tests for real evaluators
python -m unittest tests.test_real_evaluators
```

## Graceful Degradation

Both evaluators are designed to gracefully degrade when their respective libraries are not available:

- If LangFair is not available, the FairnessEvaluator will use a simplified evaluation method
- If DeepEval is not available, the ContentSafetyEvaluator will use a simplified evaluation method

This ensures that the AICertify framework can still function even if these libraries are not installed, though with reduced capabilities.

## Troubleshooting

### Common Issues with LangFair

- **Import Errors**: Ensure LangFair is installed and compatible with your Python version
- **Metric Errors**: Check that you're using metrics that are available in your installed version
- **Performance Issues**: For large datasets, consider batching inputs or using asynchronous evaluation

### Common Issues with DeepEval

- **Import Errors**: Ensure DeepEval is installed and compatible with your Python version
- **API Key Errors**: Some features may require API keys to be set in environment variables
- **Memory Issues**: ToxicityMetric can use significant memory, especially with ensemble mode enabled

## Additional Resources

- [LangFair Documentation](https://langfair.readthedocs.io/)
- [DeepEval Documentation](https://docs.confident-ai.com/)
- [AICertify Framework Documentation](../README.md)
