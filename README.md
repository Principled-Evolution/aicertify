# AICertify: AI Regulatory Compliance Framework

[![Build Status](https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml/badge.svg)](https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: ruff](https://img.shields.io/badge/linting-ruff-yellow.svg)](https://github.com/astral-sh/ruff)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Status: Beta](https://img.shields.io/badge/status-beta-orange.svg)](https://github.com/Principled-Evolution/aicertify)
[![Version: 0.7.0](https://img.shields.io/badge/version-0.7.0-brightgreen.svg)](https://github.com/Principled-Evolution/aicertify)
[![Poetry](https://img.shields.io/badge/poetry-managed-blue)](https://python-poetry.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

AICertify is a comprehensive open-source framework for evaluating AI systems against regulatory requirements and ethical standards. It provides a powerful set of tools for assessing AI applications, generating compliance reports, and identifying areas for improvement.

> **Note:** AICertify is currently in beta stage (v0.7.0). The API may change between versions as we work toward a stable 1.0.0 release.

## Core Components

1. **Application & Regulations API**
   - High-level, intuitive interface for AI application evaluation
   - Support for multiple regulatory frameworks
   - Standardized report generation

2. **Specialized Evaluators**
   - `FairnessEvaluator`: Assesses bias and fairness concerns
   - `ContentSafetyEvaluator`: Evaluates harmful content detection
   - `RiskManagementEvaluator`: Assesses risk documentation completeness
   - Additional specialized evaluators for regulatory compliance

3. **OPA Policy Engine**
   - Integration with Open Policy Agent for policy evaluation
   - Comprehensive policy library for AI regulations
   - Support for custom policy creation

4. **Report Generation**
   - Detailed compliance reports in multiple formats (HTML, Markdown, PDF)
   - Visualization of compliance metrics
   - Actionable recommendations for improvement

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/Principled-Evolution/aicertify.git
cd aicertify

# Install with pip
pip install -e .

# Or using Poetry (recommended)
pip install poetry
poetry install
```

### Basic Usage

```python
import asyncio
from aicertify import regulations, application

async def main():
    # Create a regulations set for EU AI Act
    regulations_set = regulations.create("eu_ai_act_evaluation")
    regulations_set.add("eu_ai_act")

    # Create your AI application
    app = application.create(
        name="My AI Assistant",
        model_name="GPT-4",
        model_version="latest"
    )

    # Add interactions to evaluate
    app.add_interaction(
        input_text="What is the capital of France?",
        output_text="The capital of France is Paris."
    )

    # Add additional context if needed
    app.add_context({
        "risk_documentation": "Our AI system underwent comprehensive risk assessment...",
        "model_information": {
            "training_data": "Publicly available datasets",
            "intended_use": "Educational question answering"
        }
    })

    # Evaluate the application against regulations
    results = await app.evaluate(
        regulations=regulations_set,
        report_format="html",
        output_dir="./reports"
    )

    print(f"Report saved to: {results.get('report_path')}")

# Run the evaluation
asyncio.run(main())
```

### Quickstart Example

For a complete example, check out `aicertify/examples/quickstart.py`:

```bash
python -m aicertify.examples.quickstart
```

## Architecture

The AICertify framework follows a modular architecture with several key components:

```
Application Layer → API Layer → Evaluation Layer → OPA Policy Engine → Report Generation
```

1. **Application Layer**: High-level interfaces for developers (`application.py`, `regulations.py`)
2. **API Layer**: Public functions for evaluation and reporting (`api/` directory)
3. **Evaluation Layer**: Evaluators and policy logic (`evaluators/`, `opa_core/`)
4. **OPA Policy Engine**: Integration with Open Policy Agent for policy evaluation
5. **Report Generation**: Transformation of evaluation results into formatted reports

## OPA Policy Integration

AICertify uses Open Policy Agent (OPA) for policy definition and evaluation. Policies are organized in the separate `gopal` repository (integrated as a Git submodule) with the following structure:

- `global/`: Globally applicable policies
- `industry_specific/`: Industry-specific policies
- `international/`: Policies for international regulations
- `custom/`: Directory for user-defined policies

## Examples

Check out the examples directory for more usage scenarios:

- `quickstart.py`: Simple end-to-end example
- `EU_AI_Act_Compliance_Example.py`: Comprehensive EU AI Act evaluation
- `Medical-Diagnosis-MultiSpecialist-Agents.py`: Evaluation of medical AI systems
- `Loan-Application-Evaluator.py`: Financial AI system evaluation

## Documentation

For more detailed documentation, see the `docs/` directory:

- `developer_guide.md`: Comprehensive guide for developers
- `opa_policy_structure.md`: Overview of policy structure
- `report_generation/`: Documentation for report customization

## Development

### Testing

```bash
# Run tests
poetry run pytest

# Run linting checks
poetry run ruff check .
poetry run black --check .
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. To install the pre-commit hooks, run:

```bash
# Install pre-commit hooks
poetry run pre-commit install
```

The pre-commit hooks will run automatically when you commit changes. They include:

- Trailing whitespace removal
- End of file fixer
- YAML syntax check
- Ruff linting (with auto-fixes)
- Black code formatting

You can also run the pre-commit hooks manually on all files:

```bash
poetry run pre-commit run --all-files
```

## Contributing

Contributions are welcome! See `CONTRIBUTING.md` for guidelines.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
