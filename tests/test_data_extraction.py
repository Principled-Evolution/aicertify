import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch

from aicertify.report_generation.data_extraction import create_evaluation_report
from aicertify.models.report import PolicyResult, EvaluationReport


def find_sample_opa_results():
    """Find sample OPA results files for testing."""
    debug_dir = Path(os.getcwd()) / "debug_output"
    if not debug_dir.exists():
        return None
    
    result_files = list(debug_dir.glob("opa_results_*.json"))
    if not result_files:
        return None
    
    # Use the most recent file
    newest_file = sorted(result_files, key=lambda p: p.stat().st_mtime)[-1]
    
    with open(newest_file, 'r') as f:
        return json.load(f)


@pytest.mark.parametrize("empty_opa_results", [None, {}, {"empty": True}])
def test_create_evaluation_report_without_opa(empty_opa_results):
    """Test report creation with empty or missing OPA results."""
    # Sample evaluation result with metrics
    eval_result = {
        "app_name": "Test App",
        "metrics": {
            "toxicity": {
                "name": "Toxicity",
                "value": 0.1,
                "control_passed": True
            }
        }
    }
    
    # Create report
    report = create_evaluation_report(eval_result, empty_opa_results)
    
    # Verify report structure
    assert isinstance(report, EvaluationReport)
    assert report.app_details.name == "Test App"
    assert len(report.metric_groups) >= 1
    
    # We should have metrics in at least one group
    assert any(len(group.metrics) > 0 for group in report.metric_groups)


@patch('aicertify.report_generation.data_extraction.extract_policy_results')
def test_create_evaluation_report_with_opa(mock_extract):
    """Test report creation with OPA results using the extract_policy_results function."""
    # Sample evaluation result
    eval_result = {
        "app_name": "Test App"
    }
    
    # Sample OPA results
    opa_results = find_sample_opa_results() or {"result": {"policy": "Test"}}
    
    # Mock policy results
    mock_policy_results = [
        PolicyResult(
            name="Test Policy 1",
            result=True,
            metrics={
                "metric1": {
                    "name": "Metric 1",
                    "value": 0.5,
                    "control_passed": True
                }
            }
        ),
        PolicyResult(
            name="Test Policy 2",
            result=False,
            metrics={
                "metric2": {
                    "name": "Metric 2",
                    "value": 0.8,
                    "control_passed": False
                }
            }
        )
    ]
    
    # Configure mock
    mock_extract.return_value = mock_policy_results
    
    # Create report
    report = create_evaluation_report(eval_result, opa_results)
    
    # Verify extract_policy_results was called
    mock_extract.assert_called_once_with(opa_results)
    
    # Verify report structure
    assert isinstance(report, EvaluationReport)
    assert report.app_details.name == "Test App"
    assert len(report.policy_results) == 2  # Two mocked policies
    
    # Find policies by name
    policy1 = next((p for p in report.policy_results if p.name == "Test Policy 1"), None)
    policy2 = next((p for p in report.policy_results if p.name == "Test Policy 2"), None)
    
    assert policy1 is not None
    assert policy1.result is True
    assert policy1.metrics["metric1"]["control_passed"] is True
    
    assert policy2 is not None
    assert policy2.result is False
    assert policy2.metrics["metric2"]["control_passed"] is False


def test_integration_with_real_data():
    """Integration test with real OPA results data if available."""
    opa_results = find_sample_opa_results()
    if not opa_results:
        pytest.skip("No sample OPA results found for integration testing")
    
    # Sample evaluation result
    eval_result = {
        "app_name": "Integration Test App",
        # Add a test metric to ensure at least one metric group
        "metrics": {
            "test_metric": {
                "name": "Test Metric",
                "value": 1.0,
                "control_passed": True
            }
        }
    }
    
    # Create report using real OPA results
    report = create_evaluation_report(eval_result, opa_results)
    
    # Verify report structure
    assert isinstance(report, EvaluationReport)
    assert report.app_details.name == "Integration Test App"
    
    # Should have at least one metric group from the test metric
    assert len(report.metric_groups) > 0
    
    # Check policy results if they exist
    has_policies = (
        opa_results and 
        isinstance(opa_results.get("result"), dict) and 
        len(opa_results["result"]) > 0
    )
    
    if has_policies and len(report.policy_results) > 0:
        # Policy results were properly extracted
        policy = report.policy_results[0]
        assert policy.name
        assert isinstance(policy.result, bool)
        
        # Check metrics if available
        if policy.metrics:
            assert isinstance(policy.metrics, dict)
            assert len(policy.metrics) > 0
    else:
        # No policies were extracted, which is okay if the input doesn't have any
        print("No policy results were found or extracted from the test data") 