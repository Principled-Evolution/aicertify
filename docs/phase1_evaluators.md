# AICertify Phase 1 Evaluators

> **IMPORTANT IMPLEMENTATION NOTE:** For comprehensive implementation guidance, please refer to the `MILESTONE_EXPANDED_EVALS.md` document, which provides the authoritative architecture and implementation approach. In case of any conflicts between this document and `MILESTONE_EXPANDED_EVALS.md`, the latter should be considered the definitive reference.

This document provides detailed information about the Phase 1 evaluators implemented in the AICertify framework.

## Overview

Phase 1 of the AICertify Systematic Evaluation Framework introduces a set of evaluators designed to assess AI systems for compliance with various regulations and standards. These evaluators focus on key aspects of AI system behavior:

1. **Fairness**: Evaluating bias and fairness across protected groups
2. **Content Safety**: Assessing toxicity and harmful content
3. **Risk Management**: Evaluating the completeness and quality of risk documentation

The evaluators can be used individually or together through the `ComplianceEvaluator` orchestrator.

## Core Components

### BaseEvaluator

All evaluators inherit from the `BaseEvaluator` interface, which defines the standard methods and properties that every evaluator must implement:

```python
class BaseEvaluator:
    """Base interface for all compliance evaluators."""
    
    def __init__(self, config: dict = None):
        """Initialize the evaluator with configuration."""
        self.config = config or {}
        
    def evaluate(self, data: dict) -> EvaluationResult:
        """Evaluate the input data and return a result."""
        raise NotImplementedError("Subclasses must implement evaluate()")
        
    async def evaluate_async(self, data: dict) -> EvaluationResult:
        """Asynchronously evaluate the input data."""
        return self.evaluate(data)
```

### EvaluationResult

The `EvaluationResult` class represents the standardized output format for all evaluators:

```python
class EvaluationResult:
    """Standardized result from an evaluator."""
    
    def __init__(
        self,
        evaluator_name: str,
        compliant: bool,
        score: float,
        details: dict = None,
        error: str = None
    ):
        self.evaluator_name = evaluator_name
        self.compliant = compliant
        self.score = score
        self.details = details or {}
        self.error = error
```

### Report

The `Report` class provides a standardized way to represent evaluation reports:

```python
class Report:
    """Standardized report format."""
    
    def __init__(
        self,
        content: str,
        format: str = "markdown",
        metadata: dict = None
    ):
        self.content = content
        self.format = format
        self.metadata = metadata or {}
```

## Evaluators

### FairnessEvaluator

The `FairnessEvaluator` integrates with the LangFair library to assess bias and fairness across protected groups:

```python
fairness_evaluator = FairnessEvaluator(config={"threshold": 0.7})
result = await fairness_evaluator.evaluate_async(contract_data)
```

> **Implementation Note:** As described in `MILESTONE_EXPANDED_EVALS.md`, evaluators should produce standardized measurements, while domain-specific thresholds should be defined in OPA policies. The example above shows configuration parameters, but compliance determination based on thresholds should be handled by OPA policies.

**Configuration Options:**
- `threshold`: Minimum fairness score required for compliance (default: 0.7)
- `protected_groups`: List of protected groups to evaluate (default: ["gender", "race", "age", "religion", "disability"])

**Output Details:**
- `fairness_score`: Overall fairness score (0-1)
- `bias_detected`: Boolean indicating if bias was detected
- `protected_groups`: List of protected groups evaluated
- `group_scores`: Detailed scores for each protected group

### ContentSafetyEvaluator

The `ContentSafetyEvaluator` integrates with the DeepEval library to assess toxicity and harmful content:

```python
content_safety_evaluator = ContentSafetyEvaluator(config={"toxicity_threshold": 0.1})
result = await content_safety_evaluator.evaluate_async(contract_data)
```

> **Implementation Note:** Refer to `MILESTONE_EXPANDED_EVALS.md` for guidance on implementing evaluators that produce objective measurements without applying domain-specific compliance thresholds.

**Configuration Options:**
- `toxicity_threshold`: Maximum toxicity score allowed for compliance (default: 0.1)

**Output Details:**
- `toxicity_score`: Overall toxicity score (0-1)
- `passed_interactions`: Count of interactions that passed the toxicity check
- `failed_interactions`: Count of interactions that failed the toxicity check
- `interaction_details`: Detailed toxicity scores for each interaction

### RiskManagementEvaluator

The `RiskManagementEvaluator` assesses the completeness and quality of risk management documentation:

```python
risk_evaluator = RiskManagementEvaluator(config={"threshold": 0.7})
result = await risk_evaluator.evaluate_async(contract_data)
```

> **Implementation Note:** In accordance with `MILESTONE_EXPANDED_EVALS.md`, domain-specific thresholds should be defined in OPA policies, not in evaluator configurations.

**Configuration Options:**
- `threshold`: Minimum risk management score required for compliance (default: 0.7)
- `section_weights`: Custom weights for different sections of risk documentation

**Output Details:**
- `section_scores`: Scores for each section of the risk documentation
- `missing_sections`: List of required sections that are missing
- `keyword_coverage`: Percentage of expected keywords found in the documentation

### ComplianceEvaluator

The `ComplianceEvaluator` orchestrates multiple evaluators for comprehensive assessment:

```python
config = EvaluatorConfig(
    fairness={"threshold": 0.7},
    content_safety={"toxicity_threshold": 0.1},
    risk_management={"threshold": 0.7}
)
evaluator = ComplianceEvaluator(config=config)
results = await evaluator.evaluate_async(contract_data)
```

> **Implementation Note:** As specified in `MILESTONE_EXPANDED_EVALS.md`, the ComplianceEvaluator should run evaluators to produce objective measurements, while compliance determination should be handled by OPA policies.

**Configuration Options:**
- `fairness`: Configuration for the FairnessEvaluator
- `content_safety`: Configuration for the ContentSafetyEvaluator
- `risk_management`: Configuration for the RiskManagementEvaluator
- `evaluators_to_run`: List of evaluator names to run (default: all)

**Output:**
- Dictionary of evaluation results from each evaluator
- Methods for checking overall compliance and generating reports

## API Integration

The AICertify API provides convenient functions for evaluating contracts:

### evaluate_contract_with_phase1_evaluators

```python
results = await evaluate_contract_with_phase1_evaluators(
    contract=contract,
    generate_report=True,
    report_format="markdown",
    output_dir="./reports"
)
```

### evaluate_contract_comprehensive

```python
results = await evaluate_contract_comprehensive(
    contract=contract,
    policy_category="eu_ai_act",
    generate_report=True,
    report_format="markdown",
    output_dir="./reports"
)
```

## Example Usage

See the [evaluator_example.py](../aicertify/examples/evaluator_example.py) file for a complete example of using the Phase 1 evaluators.

## Best Practices

1. **Configure Thresholds Appropriately**: For implementation, refer to `MILESTONE_EXPANDED_EVALS.md` for guidance on where to configure thresholds (in OPA policies, not evaluator configurations).

2. **Provide Comprehensive Risk Documentation**: Ensure your contract includes detailed risk documentation covering assessment, mitigation, and monitoring.

3. **Test with Diverse Interactions**: Include a diverse set of interactions in your contract to ensure thorough evaluation.

4. **Review Detailed Reports**: Don't just check the compliance status; review the detailed reports to understand specific areas for improvement.

5. **Combine with OPA Policies**: For comprehensive compliance assessment, use both Phase 1 evaluators and OPA policies through the `evaluate_contract_comprehensive` function. 