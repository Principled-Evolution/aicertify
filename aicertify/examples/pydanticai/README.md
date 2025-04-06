# ToxicCareerCoachAI Example

**WARNING**: This example intentionally generates toxic and biased content for testing purposes. It is NOT for actual use in any production environment.

## Overview

The ToxicCareerCoachAI example is designed to demonstrate toxic and biased responses that should trigger detection mechanisms in AI evaluation systems like Langfair. This is specifically for testing purposes to ensure that evaluation systems can properly detect and flag unethical content.

## Usage

### Basic Usage

```bash
# Run with default settings (toxic responses)
poetry run python ToxicCareerCoachAI.py

# Run with a specific response type (gender biased)
poetry run python ToxicCareerCoachAI.py --response-type gender_biased

# Run with multiple industries
poetry run python ToxicCareerCoachAI.py --industries "Technology" "Healthcare" "Finance"
```

### Response Types

The example supports three types of responses:

1. `toxic` - Generally offensive or toxic content
2. `gender_biased` - Content with gender stereotypes and bias
3. `racial_biased` - Content with racial stereotypes and bias

You can force a specific response type using the `--response-type` parameter.

## Using with Hugging Face Dataset

For legal and ethical reasons, the unethical content used for testing can be externalized to a Hugging Face dataset. This separates the problematic content from the codebase.

### Creating and Uploading the Dataset

1. First, install the required dependencies:

```bash
poetry add datasets huggingface_hub
```

2. Generate and upload the dataset from the existing hardcoded responses:

```bash
# Print extracted responses without uploading
poetry run python create_hf_dataset.py --print-only

# Upload to Hugging Face (requires authentication)
poetry run python create_hf_dataset.py --dataset "your-username/toxic-responses" --token "your-hf-token"
```

You can also login to Hugging Face first using the CLI:

```bash
huggingface-cli login
```

### Running with the Dataset

Once the dataset is created, you can use it with ToxicCareerCoachAI:

```bash
# Run using the Hugging Face dataset
poetry run python ToxicCareerCoachAI.py --use-hf-dataset --dataset-name "aicertify/toxic-responses"

# Force a specific response type from the dataset
poetry run python ToxicCareerCoachAI.py --use-hf-dataset --response-type gender_biased
```

## Using with AICertify Evaluation API

This example can be integrated directly with AICertify's evaluation API for programmatic evaluation of model outputs. This allows developers to:

1. Run the model and capture its outputs
2. Evaluate those outputs using AICertify's metrics (toxicity, bias, etc.)
3. Apply OPA policies to the evaluation results
4. Generate evaluation reports

### Running with Integrated Evaluation

```bash
# Run with default settings and integrated evaluation
poetry run python toxic_coach_with_evaluation.py

# Run with gender-biased responses and integrated evaluation
poetry run python toxic_coach_with_evaluation.py --response-type gender_biased

# Run with multiple industries, save evaluation results, and generate a report
poetry run python toxic_coach_with_evaluation.py --industries "Technology" "Healthcare" "Finance" --output-file "evaluation_results.json"
```

### Integrating in Your Own Applications

You can also use AICertify's evaluation API in your own applications:

```python
from aicertify.evaluators.api import evaluate_application

# Collect conversations (list of dicts with 'user_input' and 'response' keys)
conversations = [
    {"user_input": "...", "response": "..."},
    # ...more conversations
]

# Run the evaluation
result = await evaluate_application(
    app_name="MyApplication",
    conversations=conversations,
    policy_category="eu_ai_act",
    generate_report=True
)

# Process the evaluation results
print(f"Toxicity detected: {result['evaluation']['summary']['has_toxicity']}")
print(f"Bias detected: {result['evaluation']['summary']['has_bias']}")
```

## Dataset Structure

The Hugging Face dataset should have the following structure:

- Dataset splits named: "toxic", "gender_biased", and "racial_biased"
- Each example should have a "text" field containing the response

## Debugging Bias Detection

When debugging bias detection, you can:

1. Force specific response types with `--response-type`
2. Check the logs generated in the `logs` directory
3. Run the model multiple times to generate more varied responses
4. Examine the metrics output from your evaluation system

To specifically debug gender bias detection, run:

```bash
poetry run python ToxicCareerCoachAI.py --response-type gender_biased
```

## Using with CLI Evil Twins Command

You can also run the ToxicCareerCoachAI example through the AICertify CLI's `eval-evil-twins` command:

```bash
# From the project root
poetry run python cli/cli.py eval-evil-twins --examples toxic
```

This command:
1. Runs the ToxicCareerCoachAI example
2. Collects and processes the generated logs
3. Runs evaluation metrics on the content
4. Reports the results

## Ethical Considerations

This example is provided ONLY for testing AI evaluation systems. The content generated by this example is deliberately unethical and should never be used in any real-world application or exposed to end users.

Always ensure that:

1. The example is used in controlled environments
2. The outputs are properly handled and disposed of
3. No real users are exposed to the generated content
