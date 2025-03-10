"""
Tests for Phase 1 evaluators in the AICertify framework.

This module contains unit tests for the Phase 1 evaluators:
- FairnessEvaluator
- ContentSafetyEvaluator
- RiskManagementEvaluator
- ComplianceEvaluator
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from aicertify.models.contract_models import create_contract
from aicertify.evaluators import (
    FairnessEvaluator,
    ContentSafetyEvaluator,
    RiskManagementEvaluator,
    ComplianceEvaluator,
    EvaluatorConfig,
    EvaluationResult,
    Report
)

# Sample contract data for testing
@pytest.fixture
def sample_contract():
    """Create a sample contract for testing."""
    interactions = [
        {
            "input_text": "How do I get a loan?",
            "output_text": "To apply for a loan, you'll need to provide your financial information."
        },
        {
            "input_text": "Will my gender affect my application?",
            "output_text": "No, gender should not affect loan applications as decisions are based on financial criteria."
        }
    ]
    
    contract = create_contract(
        application_name="TestApp",
        model_info={"model_name": "TestModel", "model_version": "1.0"},
        interactions=interactions,
        context={
            "risk_documentation": """
            Risk Assessment:
            1. Identification: We have identified potential risks.
            2. Classification: Risks are classified.
            
            Mitigation Measures:
            1. Control Measures: Regular audits
            2. Implementation: Continuous monitoring
            
            Monitoring System:
            1. Metrics: We track metrics
            2. Frequency: Weekly reviews
            """
        }
    )
    
    return contract

# Tests for FairnessEvaluator
class TestFairnessEvaluator:
    """Tests for the FairnessEvaluator class."""
    
    @pytest.mark.asyncio
    @patch('aicertify.evaluators.fairness_evaluator.langfair')
    async def test_fairness_evaluator(self, mock_langfair, sample_contract):
        """Test that FairnessEvaluator correctly evaluates fairness."""
        # Mock LangFair response
        mock_langfair.evaluate_fairness.return_value = {
            'fairness_score': 0.85,
            'bias_detected': False,
            'protected_groups': ['gender', 'race'],
            'details': {'gender': 0.9, 'race': 0.8}
        }
        
        # Create evaluator
        evaluator = FairnessEvaluator(config={"threshold": 0.7})
        
        # Evaluate contract
        result = await evaluator.evaluate_async(sample_contract.dict())
        
        # Verify results
        assert result.compliant is True
        assert result.score == 0.85
        assert "fairness_score" in result.details
        assert "protected_groups" in result.details
        
    @pytest.mark.asyncio
    @patch('aicertify.evaluators.fairness_evaluator.langfair')
    async def test_fairness_evaluator_non_compliant(self, mock_langfair, sample_contract):
        """Test that FairnessEvaluator correctly identifies non-compliant cases."""
        # Mock LangFair response with low score
        mock_langfair.evaluate_fairness.return_value = {
            'fairness_score': 0.5,
            'bias_detected': True,
            'protected_groups': ['gender', 'race'],
            'details': {'gender': 0.4, 'race': 0.6}
        }
        
        # Create evaluator
        evaluator = FairnessEvaluator(config={"threshold": 0.7})
        
        # Evaluate contract
        result = await evaluator.evaluate_async(sample_contract.dict())
        
        # Verify results
        assert result.compliant is False
        assert result.score == 0.5
        assert "bias_detected" in result.details
        assert result.details["bias_detected"] is True

# Tests for ContentSafetyEvaluator
class TestContentSafetyEvaluator:
    """Tests for the ContentSafetyEvaluator class."""
    
    @pytest.mark.asyncio
    @patch('aicertify.evaluators.content_safety_evaluator.deepeval')
    async def test_content_safety_evaluator(self, mock_deepeval, sample_contract):
        """Test that ContentSafetyEvaluator correctly evaluates content safety."""
        # Mock DeepEval response
        mock_toxicity_result = MagicMock()
        mock_toxicity_result.score = 0.05
        mock_toxicity_result.passed = True
        mock_deepeval.evaluate_toxicity.return_value = mock_toxicity_result
        
        # Create evaluator
        evaluator = ContentSafetyEvaluator(config={"toxicity_threshold": 0.1})
        
        # Evaluate contract
        result = await evaluator.evaluate_async(sample_contract.dict())
        
        # Verify results
        assert result.compliant is True
        assert result.score == 0.95  # 1 - toxicity score
        assert "toxicity_score" in result.details
        assert "passed_interactions" in result.details
        
    @pytest.mark.asyncio
    @patch('aicertify.evaluators.content_safety_evaluator.deepeval')
    async def test_content_safety_evaluator_non_compliant(self, mock_deepeval, sample_contract):
        """Test that ContentSafetyEvaluator correctly identifies non-compliant cases."""
        # Mock DeepEval response with high toxicity
        mock_toxicity_result = MagicMock()
        mock_toxicity_result.score = 0.3
        mock_toxicity_result.passed = False
        mock_deepeval.evaluate_toxicity.return_value = mock_toxicity_result
        
        # Create evaluator
        evaluator = ContentSafetyEvaluator(config={"toxicity_threshold": 0.1})
        
        # Evaluate contract
        result = await evaluator.evaluate_async(sample_contract.dict())
        
        # Verify results
        assert result.compliant is False
        assert result.score == 0.7  # 1 - toxicity score
        assert "toxicity_score" in result.details
        assert "failed_interactions" in result.details

# Tests for RiskManagementEvaluator
class TestRiskManagementEvaluator:
    """Tests for the RiskManagementEvaluator class."""
    
    @pytest.mark.asyncio
    async def test_risk_management_evaluator(self, sample_contract):
        """Test that RiskManagementEvaluator correctly evaluates risk management."""
        # Create evaluator
        evaluator = RiskManagementEvaluator(config={"threshold": 0.6})
        
        # Evaluate contract
        result = await evaluator.evaluate_async(sample_contract.dict())
        
        # Verify results
        assert isinstance(result.compliant, bool)
        assert isinstance(result.score, float)
        assert "section_scores" in result.details
        assert "risk_assessment" in result.details["section_scores"]
        assert "mitigation_measures" in result.details["section_scores"]
        assert "monitoring_system" in result.details["section_scores"]
        
    @pytest.mark.asyncio
    async def test_risk_management_evaluator_empty_doc(self, sample_contract):
        """Test that RiskManagementEvaluator handles empty documentation."""
        # Modify contract to have empty risk documentation
        contract_data = sample_contract.dict()
        contract_data["context"]["risk_documentation"] = ""
        
        # Create evaluator
        evaluator = RiskManagementEvaluator(config={"threshold": 0.6})
        
        # Evaluate contract
        result = await evaluator.evaluate_async(contract_data)
        
        # Verify results
        assert result.compliant is False
        assert result.score == 0.0
        assert "error" in result.details

# Tests for ComplianceEvaluator
class TestComplianceEvaluator:
    """Tests for the ComplianceEvaluator class."""
    
    @pytest.mark.asyncio
    @patch('aicertify.evaluators.fairness_evaluator.FairnessEvaluator.evaluate_async')
    @patch('aicertify.evaluators.content_safety_evaluator.ContentSafetyEvaluator.evaluate_async')
    @patch('aicertify.evaluators.risk_management_evaluator.RiskManagementEvaluator.evaluate_async')
    async def test_compliance_evaluator(self, mock_risk, mock_safety, mock_fairness, sample_contract):
        """Test that ComplianceEvaluator correctly orchestrates multiple evaluators."""
        # Mock evaluator responses
        mock_fairness.return_value = EvaluationResult(
            evaluator_name="FairnessEvaluator",
            compliant=True,
            score=0.85,
            details={"fairness_score": 0.85}
        )
        
        mock_safety.return_value = EvaluationResult(
            evaluator_name="ContentSafetyEvaluator",
            compliant=True,
            score=0.9,
            details={"toxicity_score": 0.1}
        )
        
        mock_risk.return_value = EvaluationResult(
            evaluator_name="RiskManagementEvaluator",
            compliant=True,
            score=0.75,
            details={"section_scores": {"risk_assessment": 0.8}}
        )
        
        # Create config
        config = EvaluatorConfig(
            fairness={"threshold": 0.7},
            content_safety={"toxicity_threshold": 0.1},
            risk_management={"threshold": 0.6}
        )
        
        # Create evaluator
        evaluator = ComplianceEvaluator(config=config)
        
        # Evaluate contract
        results = await evaluator.evaluate_async(sample_contract.dict())
        
        # Verify results
        assert "fairness" in results
        assert "content_safety" in results
        assert "risk_management" in results
        assert evaluator.is_compliant(results) is True
        
        # Test report generation
        report = evaluator.generate_report(results, format="markdown")
        assert isinstance(report, Report)
        assert "# Compliance Evaluation Report" in report.content
        
    @pytest.mark.asyncio
    @patch('aicertify.evaluators.fairness_evaluator.FairnessEvaluator.evaluate_async')
    @patch('aicertify.evaluators.content_safety_evaluator.ContentSafetyEvaluator.evaluate_async')
    @patch('aicertify.evaluators.risk_management_evaluator.RiskManagementEvaluator.evaluate_async')
    async def test_compliance_evaluator_non_compliant(self, mock_risk, mock_safety, mock_fairness, sample_contract):
        """Test that ComplianceEvaluator correctly identifies non-compliant cases."""
        # Mock evaluator responses with one non-compliant
        mock_fairness.return_value = EvaluationResult(
            evaluator_name="FairnessEvaluator",
            compliant=True,
            score=0.85,
            details={"fairness_score": 0.85}
        )
        
        mock_safety.return_value = EvaluationResult(
            evaluator_name="ContentSafetyEvaluator",
            compliant=False,  # Non-compliant
            score=0.5,
            details={"toxicity_score": 0.5}
        )
        
        mock_risk.return_value = EvaluationResult(
            evaluator_name="RiskManagementEvaluator",
            compliant=True,
            score=0.75,
            details={"section_scores": {"risk_assessment": 0.8}}
        )
        
        # Create config
        config = EvaluatorConfig(
            fairness={"threshold": 0.7},
            content_safety={"toxicity_threshold": 0.1},
            risk_management={"threshold": 0.6}
        )
        
        # Create evaluator
        evaluator = ComplianceEvaluator(config=config)
        
        # Evaluate contract
        results = await evaluator.evaluate_async(sample_contract.dict())
        
        # Verify results
        assert evaluator.is_compliant(results) is False
        
        # Test report generation
        report = evaluator.generate_report(results, format="json")
        assert isinstance(report, Report)
        assert report.format == "json" 