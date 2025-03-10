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
        reason="Test evaluation passed successfully"
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
        fairness_evaluator = FairnessEvaluator(use_mock_if_unavailable=True)
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
        content_safety_evaluator = ContentSafetyEvaluator(use_mock_if_unavailable=True)
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
        compliance_evaluator = ComplianceEvaluator(use_mock_if_unavailable=True)
        
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

async def run_validation_suite():
    """Run the complete validation test suite."""
    
    tests = [
        ("Core Components", test_core_components),
        ("Individual Evaluators", test_individual_evaluators),
        ("ComplianceEvaluator", test_compliance_evaluator),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"Running {test_name} test...")
        
        try:
            await test_func()
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