# AICertify Project Overview

## Project Mission

AICertify is an open-source framework for validating and certifying AI applications against regulatory, compliance, and operational requirements. The framework provides a standardized way to evaluate AI systems against various criteria including fairness, regulatory compliance, and performance.

## Key Components and Architecture

### Core Components

1. **Contract System**
   - `models/contract_models.py`: Defines the AiCertifyContract data structure that captures AI interactions
   - Functions: `create_contract()`, `save_contract()`, `load_contract()`
   - Contracts store application metadata, model information, and captured interactions

2. **Evaluation System**
   - `evaluators/`: Contains evaluation implementations
   - `evaluators/simple_evaluator.py`: Lightweight evaluator implementation
   - `evaluators/api.py`: Main evaluation API
   - `system_evaluators/`: System-level evaluation capabilities

3. **Policy Engine**
   - `opa_core/`: OPA integration components
   - `opa_policies/`: OPA policy definitions in Rego
     - `opa_policies/compliance/`: Regulatory compliance policies
     - `opa_policies/acceptance/`: Acceptance criteria policies
     - `opa_policies/validation/`: Validation policies

4. **Report Generation**
   - `report_generation/report_generator.py`: Creates reports in Markdown and PDF formats
   - `report_generation/data_extraction.py`: Extracts relevant data for reports
   - Uses ReportLab for PDF generation

5. **CLI Tools**
   - `cli/cli.py`: Main command-line interface
   - `cli/evaluate.py`: Evaluation command implementations
   - Subcommands: `eval-policy`, `eval-folder`, `eval-all`

6. **Public API**
   - `api.py`: Main API functions for external use
   - `__init__.py`: Exposes main functions for import

### Data Flow

```
1. AI Application → Captured Interactions → AiCertifyContract
2. AiCertifyContract → Evaluators → Evaluation Results
3. Evaluation Results → OPA Policies → Compliance Assessment
4. Compliance Assessment → Report Generation → Markdown/PDF Reports
```

## Integration Approach

AICertify is designed to be minimally intrusive for developers while providing powerful validation capabilities:

1. **Capture Interactions**: Developers capture AI interactions in a standardized format
2. **Create Contract**: Generate an AiCertifyContract to formalize the evaluation target
3. **Request Evaluation**: Use a simple API to evaluate the contract against selected policies
4. **Process Results**: Review compliance results and generated reports

Key developer APIs:
```python
# Create and manage contracts
contract = create_contract(application_name, model_info, captured_interactions)
save_contract(contract, file_path)
loaded_contract = load_contract(file_path)

# Evaluate contracts
result = evaluate_contract(contract_path, policy_category)
result = evaluate_contract_object(contract, policy_category)

# Generate reports
generate_report(evaluation_result, output_path, format="markdown")
```

## Development Guidelines

### Directory Structure Management

When developing, pay careful attention to file paths and package structure:

- Always use the correct relative paths from the project root
- Keep related functionality in appropriate directories
- Use proper relative or absolute Python imports

### Coding Style

- Use explicit type hints for all function signatures
- Follow Google-style docstrings for all public functions
- Implement proper error handling with specific exceptions
- Use Python's logging module for reporting issues
- Follow PEP 8 standards with 88-character line length
- Use snake_case for Python files and variables
- Use kebab-case for OPA policy files

### Testing Approach

- Create unit tests for all new functionality
- Use pytest for test implementation
- Ensure tests can run in isolation
- Mock external dependencies appropriately
- Include both positive and negative test cases

### Error Handling Best Practices

- Use specific exception types rather than generic exceptions
- Provide clear, actionable error messages
- Log errors with appropriate logging levels
- Implement graceful failure modes
- Expose errors to users in a friendly format

## Commercial Considerations

AICertify is designed as an open-source solution with potential for commercial extensions:

1. **OSS Core**: The core functionality is open-source and freely available
2. **Commercial Extensions**: Future commercial options may include:
   - Enterprise support
   - Advanced policy libraries
   - Integration services
   - Cloud-based evaluation services

When developing, consider:
- Maintain a clean separation between core features and potential commercial features
- Design for extensibility to support future commercial modules
- Document public APIs thoroughly for both OSS users and potential commercial users

## Reference Documentation

- **Environment**: Python 3.12, Poetry for dependency management
- **Key Dependencies**:
  - LangFair for fairness evaluations
  - Open Policy Agent (OPA) for policy validation
  - PydanticAI/Pydantic for data models
  - FastAPI for service implementations
  - ReportLab for PDF generation
- **Development Environment**: Windows, but cross-platform compatible
