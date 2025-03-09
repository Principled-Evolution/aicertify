# Evaluator Integration for EU AI Act Compliance

This document details the plan for ensuring proper integration between evaluators and OPA policies, focusing on Task 2.2 of the EU AI Act integration project: "Merge evaluator outputs with the OPA policy evaluation results for EU AI Act based on the integration plan guidelines."

## Table of Contents

1. [Current Architecture Analysis](#current-architecture-analysis)
2. [Evaluator Output Standardization](#evaluator-output-standardization)
3. [Model Card Interface Design](#model-card-interface-design)
4. [Integration Testing Framework](#integration-testing-framework)
5. [Implementation Plan](#implementation-plan)
6. [Developer Experience Improvements](#developer-experience-improvements)

## Current Architecture Analysis

### Evaluator Structure

The AICertify framework includes several evaluator types relevant to EU AI Act compliance:

1. **Core Evaluators**:
   - `FairnessEvaluator`
   - `ContentSafetyEvaluator`
   - `RiskManagementEvaluator`
   - `AccuracyEvaluator`
   - `BiometricCategorizationEvaluator`

2. **Prohibited Practices Evaluators**:
   - `ManipulationEvaluator`
   - `VulnerabilityExploitationEvaluator`
   - `SocialScoringEvaluator`
   - `EmotionRecognitionEvaluator`

3. **Documentation Evaluators**:
   - `ModelCardEvaluator`

### Integration Points

The `ComplianceEvaluator` class serves as the orchestrator, integrating all evaluators and producing a unified result. The main API functions that utilize evaluators include:

- `evaluate_contract_with_phase1_evaluators` - Core function for Phase 1 evaluators
- `evaluate_contract_comprehensive` - Combines Phase 1 evaluators with OPA policy evaluation
- `evaluate_contract_by_folder` - Folder-based approach for OPA policies, also using Phase 1 evaluators

### Output Formats

Currently, each evaluator produces an `EvaluationResult` object with:
- `evaluator_name`: Name of the evaluator
- `compliant`: Boolean compliance status
- `score`: Numeric score between 0-1
- `threshold`: The threshold used for compliance determination
- `reason`: Human-readable explanation
- `details`: Dictionary with detailed findings

## Evaluator Output Standardization

To ensure consistent integration with OPA policies, we need to standardize how evaluator outputs are structured and consumed.

### Proposed Standardization

1. **Metadata Schema**:
   ```python
   {
     "evaluator_id": str,           # Unique identifier for the evaluator
     "evaluator_type": str,         # Category (fairness, prohibited_practice, etc.)
     "article_references": List[str], # EU AI Act article references
     "version": str                 # Evaluator version
   }
   ```

2. **Measurement Schema**:
   ```python
   {
     "primary_score": float,        # Main compliance score (0-1)
     "threshold": float,            # Threshold for compliance
     "subscores": Dict[str, float], # Component scores
     "raw_measurements": Dict       # Raw measurement data
   }
   ```

3. **Result Schema**:
   ```python
   {
     "compliant": bool,             # Overall compliance status
     "confidence": float,           # Confidence in the result (0-1)
     "reasoning": str,              # Explanation for the result
     "recommendations": List[str],  # Actionable recommendations
     "evidence": Dict               # Supporting evidence for findings
   }
   ```

### Implementation Requirements

1. Update each evaluator to include these standardized fields
2. Create helper functions to transform legacy evaluator outputs to the new format
3. Ensure the `ComplianceEvaluator` properly aggregates these standardized outputs
4. Update API functions to handle and process the standardized output format

## Model Card Interface Design

To provide developers with an easy way to input model information and configuration parameters, we'll implement a well-structured Model Card interface.

### ModelCard Pydantic Model

```python
class ModelCard(BaseModel):
    """Model card for AI model documentation and compliance evaluation."""
    
    # Basic Information
    model_name: str
    model_version: Optional[str] = None
    model_type: str
    organization: str
    
    # Intended Use
    primary_uses: List[str]
    out_of_scope_uses: Optional[List[str]] = None
    
    # Model Details
    description: str
    model_architecture: Optional[str] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    
    # Performance
    performance_metrics: Optional[Dict[str, Any]] = None
    benchmark_results: Optional[Dict[str, Any]] = None
    
    # Data
    training_data: Optional[Dict[str, Any]] = None
    evaluation_data: Optional[Dict[str, Any]] = None
    
    # Risk & Mitigation
    ethical_considerations: Optional[List[str]] = None
    limitations: Optional[List[str]] = None
    bias_considerations: Optional[Dict[str, Any]] = None
    mitigation_strategies: Optional[List[str]] = None
    
    # Usage Guidelines
    usage_guidelines: Optional[List[str]] = None
    decision_thresholds: Optional[Dict[str, float]] = None
    
    # Additional Information
    additional_info: Optional[Dict[str, Any]] = Field(default_factory=dict)
```

### Integration with Contract Models

The `ModelCard` will be integrated with the existing contract models:

1. **Enhance ModelInfo**:
   ```python
   class ModelInfo(BaseModel):
       model_name: str
       model_version: Optional[str] = None
       metadata: Dict[str, Any] = Field(default_factory=dict)
       model_card: Optional[ModelCard] = None  # New field
   ```

2. **Create Helper Functions**:
   ```python
   def create_contract_with_model_card(
       application_name: str,
       model_card: ModelCard,
       interactions: List[Dict[str, Any]],
       final_output: Optional[str] = None,
       context: Optional[Dict[str, Any]] = None,
       compliance_context: Optional[Dict[str, Any]] = None
   ) -> AiCertifyContract:
       """Create a contract with a detailed model card."""
       # Implementation
   ```

3. **Update API Functions**:
   - Modify `evaluate_contract_object` and similar functions to accept `model_card` parameter
   - Add validation to ensure model card information is properly processed by relevant evaluators

## Integration Testing Framework

To ensure evaluators work correctly with the API and OPA policies, we'll implement a comprehensive testing framework.

### Test Categories

1. **Individual Evaluator Tests**:
   - Test each evaluator with known input/output pairs
   - Verify correct threshold application and score calculation
   - Ensure proper metadata and article references

2. **ComplianceEvaluator Integration Tests**:
   - Test aggregation of multiple evaluator results
   - Verify overall compliance determination
   - Check report generation with multiple evaluators

3. **API Integration Tests**:
   - Test end-to-end flow from contract to evaluation results
   - Verify OPA policy integration with evaluator results
   - Validate report generation

4. **Model Card Tests**:
   - Test creation and validation of model cards
   - Verify proper integration with evaluators, especially ModelCardEvaluator
   - Test helper functions for model card creation

### Test Data

We'll create a standardized test dataset including:
- Sample contracts with varying compliance issues
- Model cards with different levels of completeness
- Expected outputs for each evaluator
- Mock OPA policy results for comparison

## Implementation Plan

### Phase 1: Standardization (Week 1)

1. Update `EvaluationResult` class with standardized fields
2. Implement helper functions for legacy compatibility
3. Update each evaluator to conform to standardized output format
4. Write unit tests for the new standardization format

### Phase 2: Model Card Interface (Week 2)

1. Create the `ModelCard` Pydantic model
2. Update `ModelInfo` to integrate with `ModelCard`
3. Implement helper functions for model card creation
4. Add model card processing logic to the API functions
5. Update `ModelCardEvaluator` to properly evaluate model cards

### Phase 3: API Integration (Week 3)

1. Update API functions to properly merge evaluator outputs with OPA results
2. Implement standardized naming conventions for policies and evaluator outputs
3. Create mapping functions to link evaluator results to relevant OPA policies
4. Enhance report generation to include model card information

### Phase 4: Testing and Documentation (Week 4)

1. Implement the testing framework described above
2. Run comprehensive tests for all evaluators and integration points
3. Update developer documentation with model card examples
4. Create tutorials focusing on EU AI Act compliance

## Developer Experience Improvements

### API Simplification

1. **Easy Entry Points**:
   ```python
   # Simple evaluation with EU AI Act policies
   result = await evaluate_eu_ai_act_compliance(contract)
   
   # Evaluate with specific focus areas
   result = await evaluate_eu_ai_act_compliance(
       contract, 
       focus_areas=["prohibited_practices", "documentation"]
   )
   ```

2. **Sensible Defaults**:
   - Pre-configured thresholds based on EU AI Act requirements
   - Default evaluators selected based on contract domain
   - Automatic report generation

3. **Progressive Disclosure**:
   - Basic API for common use cases
   - Advanced options for fine-tuning evaluations
   - Expert-level API for custom evaluators and policies

### Documentation Enhancements

1. **Clear Examples**:
   - Concrete examples for each evaluator and policy category
   - Full model card examples for different domains
   - Step-by-step integration tutorials

2. **Visual Aids**:
   - Process flow diagrams
   - Decision trees for evaluator selection
   - Result interpretation guides

3. **EU AI Act Reference**:
   - Mapping between evaluators and EU AI Act articles
   - Compliance checklist for different AI system categories
   - Explanation of key terms and requirements

## Next Steps

1. Begin standardization of evaluator outputs
2. Create the ModelCard Pydantic model
3. Update API functions to merge evaluator and OPA results
4. Develop comprehensive testing framework
5. Update developer documentation 