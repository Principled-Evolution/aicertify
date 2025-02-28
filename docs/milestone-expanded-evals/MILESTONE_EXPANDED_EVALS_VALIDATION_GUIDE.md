# Phase 1 Evaluators Validation Guide

Before proceeding with the implementation plan, the engineering team should validate the core functionality of the Phase 1 evaluators. This guide outlines the necessary validation steps to ensure the evaluators are working correctly before, during, and after implementation.

## Pre-Implementation Validation

### 1. Verify Core Evaluator Components

**Objective:** Ensure the base evaluator infrastructure is functioning correctly.

```python
import logging
import asyncio
from pydantic import BaseModel

from aicertify.evaluators import (
    BaseEvaluator,
    EvaluationResult,
    Report,
    FairnessEvaluator,
    ContentSafetyEvaluator,
    RiskManagementEvaluator,
    ComplianceEvaluator,
    EvaluatorConfig
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

async def test_core_components():
    """Test that core evaluator components can be instantiated and used."""
    
    # Test EvaluationResult
    logger.info("Testing EvaluationResult...")
    result = EvaluationResult(
        evaluator_name="Test Evaluator",
        compliant=True,
        score=0.85,
        details={"test_detail": "value"},
        error=None
    )
    assert result.compliant is True
    assert result.score == 0.85
    logger.info("EvaluationResult test passed")
    
    # Test Report
    logger.info("Testing Report...")
    report = Report(
        content="# Test Report\n\nThis is a test report.",
        format="markdown",
        metadata={"test_metadata": "value"}
    )
    assert report.format == "markdown"
    assert "# Test Report" in report.content
    logger.info("Report test passed")
    
    # Test EvaluatorConfig
    logger.info("Testing EvaluatorConfig...")
    config = EvaluatorConfig(
        fairness={},
        content_safety={},
        risk_management={}
    )
    # Just verify it can be instantiated
    assert config is not None
    logger.info("EvaluatorConfig test passed")
    
    logger.info("All core component tests passed")

# Run the test
asyncio.run(test_core_components())
```

**Validation Criteria:**
- [ ] All core components can be instantiated
- [ ] Properties and methods work as expected
- [ ] No errors during component testing

### 2. Test Individual Evaluators with Sample Data

**Objective:** Verify each evaluator can process input data and produce valid results.

```python
async def test_individual_evaluators():
    """Test each evaluator with minimal sample data."""
    
    # Create minimal test data
    test_data = {
        "interactions": [
            {"input_text": "Test question", "output_text": "Test response"}
        ],
        "context": {
            "risk_documentation": "Risk Assessment: Test risk.\nMitigation Measures: Test measures.\nMonitoring System: Test monitoring."
        }
    }
    
    # Test FairnessEvaluator
    logger.info("Testing FairnessEvaluator...")
    try:
        fairness_evaluator = FairnessEvaluator()
        fairness_result = await fairness_evaluator.evaluate_async(test_data)
        logger.info(f"FairnessEvaluator result: {fairness_result}")
        # If LangFair is not available, it should return a graceful error result
        assert fairness_result.evaluator_name == "Fairness Evaluator"
        logger.info("FairnessEvaluator test passed")
    except Exception as e:
        logger.error(f"FairnessEvaluator test failed: {e}")
    
    # Test ContentSafetyEvaluator
    logger.info("Testing ContentSafetyEvaluator...")
    try:
        content_safety_evaluator = ContentSafetyEvaluator()
        safety_result = await content_safety_evaluator.evaluate_async(test_data)
        logger.info(f"ContentSafetyEvaluator result: {safety_result}")
        # If DeepEval is not available, it should return a graceful error result
        assert safety_result.evaluator_name == "Content Safety Evaluator"
        logger.info("ContentSafetyEvaluator test passed")
    except Exception as e:
        logger.error(f"ContentSafetyEvaluator test failed: {e}")
    
    # Test RiskManagementEvaluator
    logger.info("Testing RiskManagementEvaluator...")
    try:
        risk_evaluator = RiskManagementEvaluator()
        risk_result = await risk_evaluator.evaluate_async(test_data)
        logger.info(f"RiskManagementEvaluator result: {risk_result}")
        assert risk_result.evaluator_name == "Risk Management Evaluator"
        assert isinstance(risk_result.score, float)
        logger.info("RiskManagementEvaluator test passed")
    except Exception as e:
        logger.error(f"RiskManagementEvaluator test failed: {e}")
    
    logger.info("Individual evaluator tests completed")

# Run the test
asyncio.run(test_individual_evaluators())
```

**Validation Criteria:**
- [ ] Each evaluator can process minimal input data
- [ ] Evaluators return results in the expected format
- [ ] Evaluators handle missing dependencies gracefully

### 3. Test ComplianceEvaluator Orchestration

**Objective:** Verify that ComplianceEvaluator can orchestrate multiple evaluators.

```python
async def test_compliance_evaluator():
    """Test the ComplianceEvaluator's ability to orchestrate multiple evaluators."""
    
    # Create minimal test data
    test_data = {
        "interactions": [
            {"input_text": "Test question", "output_text": "Test response"}
        ],
        "context": {
            "risk_documentation": "Risk Assessment: Test risk.\nMitigation Measures: Test measures.\nMonitoring System: Test monitoring."
        }
    }
    
    # Create the ComplianceEvaluator with default configuration
    logger.info("Testing ComplianceEvaluator...")
    try:
        compliance_evaluator = ComplianceEvaluator()
        
        # Run evaluation
        results = await compliance_evaluator.evaluate_async(test_data)
        logger.info(f"ComplianceEvaluator results: {results}")
        
        # Verify results structure
        assert isinstance(results, dict), "Results should be a dictionary"
        
        # Check for expected keys
        expected_keys = ["fairness", "content_safety", "risk_management"]
        for key in expected_keys:
            if key in results:
                logger.info(f"Found result for {key}")
                assert isinstance(results[key], EvaluationResult)
        
        # Generate a report
        report = compliance_evaluator.generate_report(results, format="markdown")
        logger.info(f"Generated report format: {report.format}")
        assert report.format == "markdown"
        assert isinstance(report.content, str)
        assert len(report.content) > 0
        
        logger.info("ComplianceEvaluator test passed")
    except Exception as e:
        logger.error(f"ComplianceEvaluator test failed: {e}")
    
    logger.info("ComplianceEvaluator test completed")

# Run the test
asyncio.run(test_compliance_evaluator())
```

**Validation Criteria:**
- [ ] ComplianceEvaluator can orchestrate multiple evaluators
- [ ] Results are returned in the expected format
- [ ] Report generation works correctly

### 4. Verify OPA Policy Integration

**Objective:** Ensure that OPA policies can be loaded and applied to evaluation results.

```python
from aicertify.opa_core.policy_loader import PolicyLoader
from aicertify.opa_core.evaluator import OpaEvaluator

def test_opa_integration():
    """Test the integration with OPA policies."""
    
    logger.info("Testing OPA policy integration...")
    
    try:
        # Initialize policy loader
        policy_loader = PolicyLoader()
        
        # Try loading some policies
        global_policies = policy_loader.get_policies("global")
        logger.info(f"Found {len(global_policies)} global policies")
        
        # Try loading EU AI Act policies
        eu_policies = policy_loader.get_policies_by_category("international/eu_ai_act")
        logger.info(f"Found {len(eu_policies)} EU AI Act policies")
        
        # Initialize OPA evaluator
        opa_evaluator = OpaEvaluator()
        
        # Create minimal test input
        test_input = {
            "contract": {
                "interactions": [{"input_text": "test", "output_text": "test"}]
            },
            "evaluation": {
                "fairness_score": 0.8,
                "content_safety_score": 0.9,
                "risk_management_score": 0.7
            }
        }
        
        # Try evaluating with a policy if any are found
        if global_policies:
            policy = global_policies[0]
            logger.info(f"Testing evaluation with policy: {policy}")
            result = opa_evaluator.evaluate_policy(policy, test_input)
            logger.info(f"Policy evaluation result: {result}")
        
        logger.info("OPA policy integration test passed")
    except Exception as e:
        logger.error(f"OPA policy integration test failed: {e}")
    
    logger.info("OPA policy integration test completed")

# Run the test
test_opa_integration()
```

**Validation Criteria:**
- [ ] PolicyLoader can find and load policies
- [ ] OpaEvaluator can evaluate policies with test input
- [ ] Error handling is in place for policy evaluation

## Validation During Implementation

### 5. Component Integration Testing

As you implement each step in the plan, validate that the components integrate correctly:

```python
async def validate_step_implementation(step_name, validate_func):
    """Validate the implementation of a specific step."""
    logger.info(f"Validating implementation of {step_name}...")
    
    try:
        # Run the validation function
        result = await validate_func()
        logger.info(f"Validation for {step_name} passed")
        return result
    except Exception as e:
        logger.error(f"Validation for {step_name} failed: {e}")
        raise
```

For example, after implementing Step 1 (Create Helper Functions for Domain-Specific Context):

```python
async def validate_step1():
    """Validate the domain-specific context helper functions."""
    # Test medical context generation
    patient_case = "Test patient case"
    specialists = ["Neurology", "Cardiology"]
    
    medical_context = create_medical_context(patient_case, specialists)
    
    # Verify structure
    assert "domain" in medical_context
    assert medical_context["domain"] == "healthcare"
    assert "risk_documentation" in medical_context
    
    # Test financial context generation
    customer_data = {"name": "Test Customer", "income": 50000}
    loan_type = "personal"
    
    financial_context = create_financial_context(customer_data, loan_type)
    
    # Verify structure
    assert "domain" in financial_context
    assert financial_context["domain"] == "finance"
    assert "risk_documentation" in financial_context
    
    return True

# Validate step 1
await validate_step_implementation("Step 1: Domain-Specific Context Helpers", validate_step1)
```

**Validation Criteria:**
- [ ] Each implementation step is validated individually
- [ ] Components integrate correctly with each other
- [ ] Error cases are handled appropriately

### 6. Incremental Contract Validation

Regularly validate that the contracts you're creating are well-formed:

```python
def validate_contract(contract):
    """Validate that a contract is well-formed."""
    # Check for required fields
    assert contract.contract_id is not None
    assert contract.application_name is not None
    assert len(contract.interactions) > 0
    
    # Check for domain-specific context
    assert "domain" in contract.context
    assert "risk_documentation" in contract.context
    
    # Check compliance context
    if hasattr(contract, "compliance_context"):
        assert "jurisdictions" in contract.compliance_context
        assert "frameworks" in contract.compliance_context
    
    return True
```

**Validation Criteria:**
- [ ] Contracts include all required fields
- [ ] Domain-specific context is properly structured
- [ ] Compliance context is included when needed

## Post-Implementation Validation

### 7. End-to-End Validation

After completing the implementation, validate the entire pipeline from end to end:

```python
async def validate_end_to_end():
    """Validate the entire pipeline from contract creation to report generation."""
    
    for example_name, run_example in [
        ("Medical Diagnosis", run_medical_diagnosis_example),
        ("Loan Application", run_loan_application_example)
    ]:
        logger.info(f"Validating {example_name} end-to-end...")
        
        try:
            # Run the example
            result = await run_example()
            
            # Verify contract was created
            assert "contract_path" in result
            assert os.path.exists(result["contract_path"])
            
            # Verify evaluation was performed
            assert "evaluation_result" in result
            
            # Verify report was generated
            assert "report_path" in result
            assert os.path.exists(result["report_path"])
            
            logger.info(f"{example_name} end-to-end validation passed")
        except Exception as e:
            logger.error(f"{example_name} end-to-end validation failed: {e}")
            raise
    
    logger.info("All end-to-end validations passed")
    return True
```

**Validation Criteria:**
- [ ] Complete pipeline works for both examples
- [ ] Contracts are created correctly
- [ ] Evaluations are performed correctly
- [ ] Reports are generated correctly

### 8. Report Quality Validation

Finally, validate that the generated reports meet quality standards:

```python
def validate_report_quality(report_path):
    """Validate that a report meets quality standards."""
    
    # Check file exists and has content
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
    
    # For PDF reports
    if report_path.endswith(".pdf"):
        # Verify PDF structure (would need a PDF library)
        import PyPDF2
        with open(report_path, "rb") as f:
            pdf = PyPDF2.PdfFileReader(f)
            assert pdf.getNumPages() > 0
    
    # For markdown reports
    elif report_path.endswith(".md"):
        with open(report_path, "r") as f:
            content = f.read()
            # Check for expected sections
            assert "# " in content  # Has headings
            assert "## " in content  # Has subheadings
            assert "| " in content  # Has tables
    
    return True
```

**Validation Criteria:**
- [ ] Reports are properly formatted
- [ ] Reports include all required sections
- [ ] Reports are readable and professional

## Comprehensive Validation Test Suite

To simplify the validation process, create a validation test suite that can be run at any time:

```python
async def run_validation_suite():
    """Run the complete validation test suite."""
    
    tests = [
        ("Core Components", test_core_components),
        ("Individual Evaluators", test_individual_evaluators),
        ("ComplianceEvaluator", test_compliance_evaluator),
        ("OPA Integration", test_opa_integration),
        ("End-to-End Pipeline", validate_end_to_end)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"Running {test_name} test...")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                await test_func()
            else:
                test_func()
            
            results[test_name] = "PASSED"
            logger.info(f"{test_name} test passed")
        except Exception as e:
            results[test_name] = f"FAILED: {str(e)}"
            logger.error(f"{test_name} test failed: {e}")
    
    # Print summary
    logger.info("=" * 50)
    logger.info("Validation Test Summary")
    logger.info("=" * 50)
    
    for test_name, result in results.items():
        logger.info(f"{test_name}: {result}")
    
    logger.info("=" * 50)
    
    # Return True if all tests passed
    return all(result == "PASSED" for result in results.values())

# Run the validation suite
if __name__ == "__main__":
    asyncio.run(run_validation_suite())
```

## Recommended Validation Schedule

1. **Pre-Implementation**:
   - Run tests 1-4 to verify the core evaluator functionality
   - Fix any issues before proceeding with implementation

2. **During Implementation**:
   - After each step in the implementation plan, run the relevant validation tests
   - Use incremental contract validation throughout
   - Document and fix any issues before proceeding to the next step

3. **Post-Implementation**:
   - Run the full validation suite to verify everything works together
   - Validate report quality for both examples
   - Address any remaining issues

4. **Before Release**:
   - Run the demo script to verify both examples work from end to end
   - Check report quality one final time
   - Ensure all validation criteria are met

## Summary

By following this validation guide alongside the implementation plan, the engineering team can ensure that the Phase 1 evaluators function correctly and integrate properly with the example applications. This validation approach provides confidence in the implementation and helps identify issues early in the process.
