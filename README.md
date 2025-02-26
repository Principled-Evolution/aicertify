# AICertify

AICertify is an open-source framework for validating and certifying AI applications against regulatory, compliance, and operational requirements. It provides a simple yet powerful way to evaluate AI interactions and generate detailed reports.

## Supported Integration Methods (Updated)

AICertify supports two main integration methods, each designed for ease-of-use and quick time-to-value:

### 1. File-Based Evaluation (CLI)

Developers can generate interaction files in JSON format and use the CLI for evaluation and report generation. This approach is ideal for file-based workflows. For more details, see the [Developer Guide](docs/developer_guide.md).

#### Example Command:
```
python -m aicertify.cli.evaluate --contract examples/sample_contract.json --policy-category eu_ai_act
```

### 2. Python API Integration

For programmatic integration, use the AICertify Python API to create contracts, evaluate them, and generate reports directly from your application. This method ensures integration with advanced OPA policies for compliance verification. Detailed instructions and examples are available in the [Developer Guide](docs/developer_guide.md).

#### Example Code:
```python
from aicertify.models.contract_models import AiCertifyContract
from aicertify.api import evaluate_contract_object

# Create a sample contract
contract = AiCertifyContract(
    contract_id='12345',
    application_name='MyApp',
    interactions=[{
        'input_text': 'User prompt',
        'output_text': 'AI response',
        'metadata': {}
    }]
)

# Evaluate the contract (asynchronously)
result = await evaluate_contract_object(contract, policy_category='eu_ai_act')
print(result)
```

### Advanced OPA Policy Integration & Real-World Example

AICertify leverages Open Policy Agent (OPA) to validate AI interactions against industry-standard policies (e.g., EU AI Act). For advanced users, our API integration supports detailed logging and error reporting to help identify policy issues. 

Our examples showcase different integration patterns for various use cases:

- [Medical Diagnosis MultiSpecialist Agents](examples/Medical-Diagnosis-MultiSpecialist-Agents.py): A complex example showing how multiple specialized agents can be orchestrated and evaluated.
- [Loan Application Evaluator](examples/Loan-Application-Evaluator.py): A simpler example demonstrating PDF report generation for financial compliance use cases.

All example scripts generate their outputs (contracts, reports, etc.) in an organized folder structure within the `examples/outputs/` directory for easy access.

---

## Roadmap & Future Work

- **Future Integrations:** Additional integration methods (e.g., uvicorn API support) are planned for future releases.
- **Enhanced Reporting:** Further customization of report formats and content.
- **Extended Policy Library:** Integration with additional compliance frameworks and evaluation strategies.

For more details and advanced configuration options, please refer to the [Developer Guide](docs/developer_guide.md).

## Installation

This project requires Python 3.12 and Poetry. To install the dependencies, run:

```
poetry install
```

## Getting Started

1. Clone the repository.
2. Install dependencies via Poetry.
3. Choose your integration method and follow the examples above to get started.

For more detailed instructions, please refer to the developer guide in `docs/developer_guide.md`. 