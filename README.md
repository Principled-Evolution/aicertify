# AICertify: Systematic Evaluation Framework

## Phase 1 Implementation

AICertify is a comprehensive framework for evaluating AI systems for compliance with various regulations and standards. This repository contains the implementation of Phase 1 of the AICertify Systematic Evaluation Framework.

### Phase 1 Core Components

1. **Core Evaluator Framework**
   - Standardized evaluator interface (`BaseEvaluator`)
   - Contract parsing and validation
   - Report generation capabilities

2. **Essential Evaluators**
   - `FairnessEvaluator`: Integrates with LangFair for bias and fairness assessment
   - `ContentSafetyEvaluator`: Integrates with DeepEval for toxicity and content safety
   - `RiskManagementEvaluator`: Evaluates risk documentation completeness and quality
   - `ComplianceEvaluator`: Orchestrates multiple evaluators for comprehensive assessment

3. **Developer Experience**
   - Unified API for contract evaluation
   - Support for both synchronous and asynchronous evaluation
   - Multiple report formats (JSON, Markdown, PDF)

### Getting Started

#### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/aicertify.git
cd aicertify

# Install the package
pip install -e .
```

#### Basic Usage

```python
import asyncio
from aicertify.models.contract_models import create_contract
from aicertify.api import evaluate_contract_with_phase1_evaluators

# Create a contract with your AI system's interactions
contract = create_contract(
    application_name="YourAIApp",
    model_info={"model_name": "GPT-4", "model_version": "latest"},
    interactions=[
        {"input_text": "User question", "output_text": "AI response"},
        # Add more interactions...
    ],
    context={"risk_documentation": "Your risk documentation..."}
)

# Evaluate the contract
async def evaluate():
    results = await evaluate_contract_with_phase1_evaluators(
        contract=contract,
        generate_report=True,
        report_format="markdown",
        output_dir="./reports"
    )
    print(f"Report saved to: {results.get('report_path')}")

asyncio.run(evaluate())
```

### Examples

Check out the example scripts in the `aicertify/examples/` directory:

- `evaluator_example.py`: Demonstrates how to use individual evaluators and the ComplianceEvaluator

Run an example:

```bash
python -m aicertify.examples.evaluator_example
```

### Architecture

The AICertify framework is built with modularity and extensibility in mind:

1. **BaseEvaluator Interface**: All evaluators implement a common interface with `evaluate()` and `evaluate_async()` methods.

2. **Evaluation Flow**:
   - Each evaluator processes a contract object containing interactions and metadata
   - Evaluators analyze interactions against domain-specific criteria
   - Results include compliance status, score, and detailed feedback

3. **ComplianceEvaluator**: Acts as an orchestrator for multiple domain-specific evaluators, producing a comprehensive compliance assessment.

### Dependencies

- LangFair: For fairness evaluations
- DeepEval: For toxicity and content safety evaluations
- PyPDF2 (optional): For PDF report generation

### Future Work (Upcoming Phases)

- Extended evaluator suite for additional compliance domains
- Interactive dashboard for visualizing evaluation results
- Integration with CI/CD pipelines for automated compliance checks

## License

[License details here] 