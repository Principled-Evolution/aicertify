# AICertify Phase 1 Implementation

This repository contains the Phase 1 implementation of AICertify, a framework for evaluating and certifying AI applications with domain-specific context helpers and policies.

## Overview

The Phase 1 implementation enhances AICertify with:

1. Domain-specific context helpers for healthcare and finance
2. Enhanced contract model with domain-specific validation
3. Domain-specific OPA policies with appropriate thresholds
4. Integration with example applications

## Getting Started

### Prerequisites

- Python 3.8 or higher
- OPA (Open Policy Agent) installed
- Required Python packages (see `requirements.txt`)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AICertify.git
   cd AICertify
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Install OPA if not already installed:
   ```bash
   # For Linux/macOS
   curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
   chmod 755 ./opa
   sudo mv opa /usr/local/bin/
   
   # For Windows (using PowerShell)
   Invoke-WebRequest -Uri https://openpolicyagent.org/downloads/latest/opa_windows_amd64.exe -OutFile opa.exe
   ```

## Usage

### Running Example Applications

#### Medical Diagnosis Multi-Specialist Agents

```bash
python examples/Medical-Diagnosis-MultiSpecialist-Agents.py --capture-contract --report-format pdf
```

This example demonstrates:
1. Creating domain-specific context for healthcare
2. Capturing interactions from multiple specialist agents
3. Using Phase 1 evaluators with healthcare OPA policies
4. Generating comprehensive PDF reports

#### Loan Application Evaluator

```bash
python examples/Loan-Application-Evaluator.py --capture-contract --report-format pdf
```

This example demonstrates:
1. Creating domain-specific context for financial applications
2. Capturing interactions from a loan approval agent
3. Using Phase 1 evaluators with financial OPA policies
4. Generating comprehensive PDF reports

### Running Validation Tests

The implementation follows the validation sequence outlined in MILESTONE_EXPANDED_EVALS_VALIDATION_GUIDE.md:

#### Complete Validation Sequence

To run the full validation sequence:

```bash
python scripts/run_phase1_validation.py
```

This will run:
1. Pre-Implementation Validation (core components, evaluators, OPA integration)
2. Phase 1 Implementation Validation (domain-specific contexts, contracts)

#### Specific Validation Stages

You can also run specific validation stages:

```bash
# Run only pre-implementation tests
python scripts/run_phase1_validation.py --stage pre

# Run only phase 1 implementation tests
python scripts/run_phase1_validation.py --stage phase1

# Run with verbose output
python scripts/run_phase1_validation.py --verbose
```

#### Individual Test Modules

You can also run individual test modules directly:

```bash
# Run pre-implementation tests
python -m unittest tests/test_evaluator_components.py

# Run phase 1 implementation tests
python -m unittest tests/test_phase1_implementation.py
```

## Documentation

Detailed documentation is available in the `docs/` directory:

- [Phase 1 Implementation Documentation](docs/phase1_implementation.md)
- [Context Helpers Documentation](docs/context_helpers.md)
- [OPA Policies Documentation](docs/opa_policies.md)

## Project Structure

```
AICertify/
├── aicertify/
│   ├── context_helpers.py       # Domain-specific context helpers
│   ├── models/
│   │   └── contract_models.py   # Enhanced contract models
│   ├── evaluators/              # Core evaluator components
│   │   ├── base.py              # Base evaluator classes
│   │   ├── fairness.py          # Fairness evaluator
│   │   ├── content_safety.py    # Content safety evaluator
│   │   ├── risk_management.py   # Risk management evaluator
│   │   └── compliance.py        # Compliance evaluator orchestration
│   └── opa_policies/
│       └── industry_specific/
│           ├── healthcare/      # Healthcare-specific policies
│           └── bfs/             # Financial-specific policies
├── examples/
│   ├── Medical-Diagnosis-MultiSpecialist-Agents.py
│   └── Loan-Application-Evaluator.py
├── tests/
│   ├── test_evaluator_components.py  # Pre-implementation tests
│   └── test_phase1_implementation.py # Phase 1 implementation tests
├── scripts/
│   ├── run_phase1_validation.py      # Validation sequence runner
│   └── generate_sample_report.py     # Sample report generator
└── docs/
    └── phase1_implementation.md
```

## Features

### Domain-Specific Context Helpers

The `context_helpers.py` module provides functions for creating domain-specific context for different application domains:

```python
# Healthcare context
medical_context = create_medical_context(
    patient_case="Patient case description...",
    specialists_involved=["Cardiology", "Neurology"]
)

# Financial context
financial_context = create_financial_context(
    customer_data=customer,
    loan_type="personal_loan"
)
```

### Enhanced Contract Model

The contract model has been enhanced to support domain-specific context and compliance context:

```python
contract = create_contract(
    application_name="Application Name",
    model_info={"model_name": "model-name"},
    interactions=interactions,
    final_output="Final output",
    context=domain_context,
    compliance_context={
        "jurisdictions": ["us", "eu"],
        "frameworks": ["framework1", "framework2"]
    }
)
```

### Domain-Specific OPA Policies

Domain-specific OPA policies have been created with appropriate thresholds:

- Healthcare policies with higher thresholds for fairness (0.85), content safety (0.90), and risk management (0.90)
- Financial policies with higher thresholds for fairness (0.90), with appropriate thresholds for content safety (0.85) and risk management (0.85)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 