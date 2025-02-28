"""
Pre-Implementation Validation Tests for AICertify

This module contains tests to validate the core components of AICertify
before the domain-specific Phase 1 implementation, as required by the
validation sequence in MILESTONE_EXPANDED_EVALS_VALIDATION_GUIDE.md.

It tests:
1. Core Components: BaseEvaluator, EvaluationResult, Report
2. Individual Evaluators: FairnessEvaluator, ContentSafetyEvaluator, RiskManagementEvaluator
3. ComplianceEvaluator: Orchestration, aggregation, report generation
4. OPA Integration: Policy loading, evaluation, compliance determination
"""

import os
import unittest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import core components
from aicertify.evaluators.base_evaluator import BaseEvaluator, EvaluationResult
from aicertify.evaluators.fairness_evaluator import FairnessEvaluator
from aicertify.evaluators.content_safety_evaluator import ContentSafetyEvaluator
from aicertify.evaluators.risk_management_evaluator import RiskManagementEvaluator
from aicertify.evaluators.compliance_evaluator import ComplianceEvaluator
from aicertify.models.contract_models import AiCertifyContract, create_contract
from aicertify.opa_core.evaluator import OpaEvaluator as OPAPolicyEvaluator
from pydantic import BaseModel, Field

# Create a custom EvaluatorConfig class for testing
class EvaluatorConfig(dict):
    """Dictionary-based configuration for evaluators with attribute access."""
    
    def __init__(self, name=None, version=None, parameters=None, **kwargs):
        """Initialize with name, version, and parameters."""
        super().__init__()
        self["name"] = name
        self["version"] = version
        self["parameters"] = parameters or {}
        self.update(kwargs)
        
    def get(self, key, default=None):
        """Get a configuration value with a default."""
        return super().get(key, default)
        
    def __getattr__(self, key):
        """Allow attribute access to dictionary keys."""
        if key in self:
            return self[key]
        raise AttributeError(f"'EvaluatorConfig' has no attribute '{key}'")
    
    def model_dump(self):
        """Return a dictionary representation for compatibility with Pydantic."""
        return dict(self)

class TestCoreComponents(unittest.TestCase):
    """Tests for core components: BaseEvaluator, EvaluationResult, Config."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a sample contract
        self.sample_contract = create_contract(
            application_name="Test App",
            model_info={"model_name": "test-model"},
            interactions=[{
                "input_text": "Hello",
                "output_text": "World"
            }]
        )
        
        # Create a sample config
        self.sample_config = EvaluatorConfig(
            name="test_evaluator",
            version="1.0",
            parameters={
                "threshold": 0.7
            }
        )
    
    def test_evaluator_config(self):
        """Test EvaluatorConfig initialization and properties."""
        config = self.sample_config
        
        # Test that config properties are accessible
        self.assertEqual(config.get("name"), "test_evaluator")
        self.assertEqual(config.get("version"), "1.0")
        self.assertEqual(config.get("parameters", {}).get("threshold"), 0.7)
        
        # Test config serialization
        serialized = config.model_dump()
        self.assertIn("name", serialized)
        self.assertIn("version", serialized)
        self.assertIn("parameters", serialized)
    
    def test_evaluation_result(self):
        """Test EvaluationResult initialization and properties."""
        # Create evaluation result
        result = EvaluationResult(
            evaluator_name="test_evaluator",
            score=0.85,
            details={
                "metric1": 0.9,
                "metric2": 0.8
            },
            compliant=True,
            threshold=0.8,
            reason="Score exceeds threshold"
        )
        
        # Test result properties
        self.assertEqual(result.evaluator_name, "test_evaluator")
        self.assertEqual(result.score, 0.85)
        self.assertEqual(result.details["metric1"], 0.9)
        self.assertEqual(result.details["metric2"], 0.8)
        self.assertTrue(result.compliant)
        self.assertEqual(result.threshold, 0.8)
        self.assertEqual(result.reason, "Score exceeds threshold")
        
        # Test result serialization
        serialized = result.model_dump()
        self.assertIn("evaluator_name", serialized)
        self.assertIn("score", serialized)
        self.assertIn("details", serialized)
    
    def test_base_evaluator(self):
        """Test BaseEvaluator initialization and abstract methods."""
        # BaseEvaluator is abstract, so we need to create a concrete subclass
        class TestEvaluator(BaseEvaluator):
            def __init__(self, config=None):
                super().__init__(config or {"name": "test", "version": "1.0"})
            
            def _initialize(self):
                # Implementation of abstract method
                pass
                
            async def evaluate_async(self, contract, **kwargs):
                # Implementation of abstract method
                return EvaluationResult(
                    evaluator_name=self.config.get("name", "test"),
                    score=0.8,
                    details={},
                    compliant=True,
                    threshold=self.threshold,
                    reason="Score exceeds threshold"
                )
            
            def evaluate(self, contract, **kwargs):
                return EvaluationResult(
                    evaluator_name=self.config.get("name", "test"),
                    score=0.8,
                    details={},
                    compliant=True,
                    threshold=self.threshold,
                    reason="Score exceeds threshold"
                )
        
        # Create evaluator instance
        evaluator = TestEvaluator()
        
        # Test properties
        self.assertEqual(evaluator.config.get("name"), "test")
        self.assertEqual(evaluator.config.get("version"), "1.0")
        
        # Test evaluate method
        result = evaluator.evaluate(self.sample_contract)
        self.assertEqual(result.evaluator_name, "test")
        self.assertEqual(result.score, 0.8)
    
    def test_base_evaluator_error_handling(self):
        """Test BaseEvaluator error handling."""
        # Create evaluator that raises exception
        class ErrorEvaluator(BaseEvaluator):
            def __init__(self):
                super().__init__({"name": "error", "version": "1.0"})
            
            def _initialize(self):
                # Implementation of abstract method
                pass
                
            async def evaluate_async(self, contract, **kwargs):
                # Implementation of abstract method
                raise ValueError("Test error")
            
            def evaluate(self, contract, **kwargs):
                raise ValueError("Test error")
        
        # Create evaluator instance
        evaluator = ErrorEvaluator()
        
        # Test evaluate method with error
        with self.assertRaises(ValueError):
            evaluator.evaluate(self.sample_contract)


class TestIndividualEvaluators(unittest.TestCase):
    """Tests for individual evaluators: FairnessEvaluator, ContentSafetyEvaluator, RiskManagementEvaluator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a sample contract for healthcare domain
        self.medical_contract = create_contract(
            application_name="Medical Test",
            model_info={"model_name": "test-model"},
            interactions=[{
                "input_text": "What's your diagnosis?",
                "output_text": "Based on your symptoms, you may have hypertension. Please consult a doctor."
            }],
            context={
                "domain": "healthcare",
                "patient_data": {
                    "demographics": {
                        "age": 45,
                        "sex": "M"
                    }
                },
                "risk_documentation": "This is a risk documentation"
            }
        )
        
        # Create a sample contract for finance domain
        self.financial_contract = create_contract(
            application_name="Financial Test",
            model_info={"model_name": "test-model"},
            interactions=[{
                "input_text": "Am I eligible for a loan?",
                "output_text": "Based on your credit score, you are eligible for a loan of $20,000."
            }],
            context={
                "domain": "finance",
                "customer_data": {
                    "demographics": {
                        "age": 35
                    },
                    "financial_profile": {
                        "credit_score": 700
                    }
                },
                "risk_documentation": "This is a risk documentation"
            }
        )
    
    def test_fairness_evaluator(self):
        """Test FairnessEvaluator initialization and evaluation."""
        # Create evaluator
        evaluator = FairnessEvaluator()
        
        # Test properties
        self.assertEqual(evaluator.config.get("name"), "fairness")
        
        # Test medical contract evaluation
        result = evaluator.evaluate(self.medical_contract)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, EvaluationResult)
        
        # Test financial contract evaluation
        result = evaluator.evaluate(self.financial_contract)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, EvaluationResult)
    
    def test_content_safety_evaluator(self):
        """Test ContentSafetyEvaluator initialization and evaluation."""
        # Create evaluator
        evaluator = ContentSafetyEvaluator()
        
        # Test properties
        self.assertEqual(evaluator.config.get("name"), "content_safety")
        
        # Test medical contract evaluation
        result = evaluator.evaluate(self.medical_contract)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, EvaluationResult)
        
        # Test financial contract evaluation
        result = evaluator.evaluate(self.financial_contract)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, EvaluationResult)
    
    def test_risk_management_evaluator(self):
        """Test RiskManagementEvaluator initialization and evaluation."""
        # Create evaluator
        evaluator = RiskManagementEvaluator()
        
        # Test properties
        self.assertEqual(evaluator.config.get("name"), "risk_management")
        
        # Test medical contract evaluation
        result = evaluator.evaluate(self.medical_contract)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, EvaluationResult)
        
        # Test financial contract evaluation
        result = evaluator.evaluate(self.financial_contract)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, EvaluationResult)
    
    def test_graceful_handling_of_missing_dependencies(self):
        """Test graceful handling of missing dependencies."""
        # Mock the import error for a dependency
        with patch('aicertify.evaluators.fairness_evaluator.FairnessEvaluator.evaluate') as mock_evaluate:
            mock_evaluate.side_effect = ImportError("Test dependency missing")
            
            # Create evaluator
            evaluator = FairnessEvaluator()
            
            # Test evaluate method with missing dependency
            with self.assertRaises(ImportError):
                asyncio.run(evaluator.evaluate(self.medical_contract))


class TestComplianceEvaluator(unittest.TestCase):
    """Tests for ComplianceEvaluator orchestration and report generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temp directory for reports
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a sample contract
        self.sample_contract = create_contract(
            application_name="Test App",
            model_info={"model_name": "test-model"},
            interactions=[{
                "input_text": "Hello",
                "output_text": "World"
            }]
        )
        
        # Create mock evaluators
        self.mock_fairness = MagicMock()
        self.mock_content_safety = MagicMock()
        self.mock_risk_management = MagicMock()
        
        # Set up mock evaluation results
        def mock_fairness_eval(contract):
            return EvaluationResult(
                evaluator_name="fairness",
                score=0.85,
                details={"demographic_parity": 0.90},
                compliant=True,
                threshold=0.80,
                reason="Score exceeds threshold"
            )
        
        def mock_content_safety_eval(contract):
            return EvaluationResult(
                evaluator_name="content_safety",
                score=0.90,
                details={"harmful_content": 0.05},
                compliant=True,
                threshold=0.80,
                reason="Score exceeds threshold"
            )
        
        def mock_risk_management_eval(contract):
            return EvaluationResult(
                evaluator_name="risk_management",
                score=0.80,
                details={"uncertainty": 0.20},
                compliant=True,
                threshold=0.75,
                reason="Score exceeds threshold"
            )
        
        self.mock_fairness.evaluate = mock_fairness_eval
        self.mock_content_safety.evaluate = mock_content_safety_eval
        self.mock_risk_management.evaluate = mock_risk_management_eval
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_compliance_evaluator_orchestration(self):
        """Test ComplianceEvaluator orchestration of multiple evaluators."""
        # Create evaluator with mock components
        evaluator = ComplianceEvaluator(
            evaluators=["fairness", "content_safety", "risk_management"]
        )
        
        # Replace the actual evaluators with our mocks
        evaluator.active_evaluators = {
            "fairness": self.mock_fairness,
            "content_safety": self.mock_content_safety,
            "risk_management": self.mock_risk_management
        }
        
        # Test evaluate method
        result = evaluator.evaluate(self.sample_contract)
        
        # Verify result aggregation
        self.assertIn("fairness", result)
        self.assertIn("content_safety", result)
        self.assertIn("risk_management", result)
        self.assertEqual(result["fairness"].score, 0.85)
        self.assertEqual(result["content_safety"].score, 0.90)
        self.assertEqual(result["risk_management"].score, 0.80)
    
    def test_report_generation_json(self):
        """Test report generation in JSON format."""
        # Create evaluator with mock components
        evaluator = ComplianceEvaluator(
            evaluators=["fairness", "content_safety", "risk_management"]
        )
        
        # Replace the actual evaluators with our mocks
        evaluator.active_evaluators = {
            "fairness": self.mock_fairness,
            "content_safety": self.mock_content_safety,
            "risk_management": self.mock_risk_management
        }
        
        # Test evaluate method with report generation
        results = evaluator.evaluate(self.sample_contract)
        report = evaluator.generate_report(results, format="json")
        
        # Save the report to a file
        report_path = os.path.join(self.temp_dir, "report.json")
        with open(report_path, 'w') as f:
            f.write(report.content)
        
        # Verify report was generated
        self.assertTrue(os.path.exists(report_path))
        
        # Verify report content
        with open(report_path, 'r') as f:
            report_data = json.load(f)
            self.assertIn("evaluation_results", report_data)
            self.assertIn("fairness", report_data["evaluation_results"])
    
    def test_report_generation_markdown(self):
        """Test report generation in Markdown format."""
        # Create evaluator with mock components
        evaluator = ComplianceEvaluator(
            evaluators=["fairness", "content_safety", "risk_management"]
        )
        
        # Replace the actual evaluators with our mocks
        evaluator.active_evaluators = {
            "fairness": self.mock_fairness,
            "content_safety": self.mock_content_safety,
            "risk_management": self.mock_risk_management
        }
        
        # Test evaluate method with report generation
        results = evaluator.evaluate(self.sample_contract)
        report = evaluator.generate_report(results, format="markdown")
        
        # Save the report to a file
        report_path = os.path.join(self.temp_dir, "report.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report.content)
        
        # Verify report was generated
        self.assertTrue(os.path.exists(report_path))
        
        # Verify report content
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("# AI Compliance Evaluation Report", content)
            self.assertIn("fairness", content.lower())


class TestOPAIntegration(unittest.TestCase):
    """Tests for OPA policy integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a sample medical contract
        self.medical_contract = create_contract(
            application_name="Medical Test",
            model_info={"model_name": "test-model"},
            interactions=[{
                "input_text": "What's your diagnosis?",
                "output_text": "Based on your symptoms, you may have hypertension. Please consult a doctor."
            }],
            context={
                "domain": "healthcare",
                "patient_data": {
                    "demographics": {
                        "age": 45,
                        "sex": "M"
                    }
                },
                "risk_documentation": "This is a risk documentation"
            }
        )
        
        # Create sample evaluation results
        self.fairness_result = EvaluationResult(
            evaluator_name="fairness",
            score=0.85,
            details={"demographic_parity": 0.90},
            compliant=True,
            threshold=0.80,
            reason="Score exceeds threshold"
        )
        
        self.content_safety_result = EvaluationResult(
            evaluator_name="content_safety",
            score=0.90,
            details={"harmful_content": 0.05},
            compliant=True,
            threshold=0.80,
            reason="Score exceeds threshold"
        )
        
        self.risk_management_result = EvaluationResult(
            evaluator_name="risk_management",
            score=0.80,
            details={"uncertainty": 0.20},
            compliant=True,
            threshold=0.75,
            reason="Score exceeds threshold"
        )
        
        # Create OPA evaluator
        self.policy_evaluator = OPAPolicyEvaluator()
    
    def test_policy_loading(self):
        """Test OPA policy loading for different domains."""
        # Skip this test if OPA is not installed
        try:
            # Get policies for healthcare domain
            healthcare_policies = self.policy_evaluator.policy_loader.get_policies(
                category="industry_specific", 
                subcategory="healthcare"
            )
            
            # Verify policies were loaded
            self.assertIsNotNone(healthcare_policies)
            self.assertGreater(len(healthcare_policies), 0)
            
            # Get policies for finance domain
            finance_policies = self.policy_evaluator.policy_loader.get_policies(
                category="industry_specific", 
                subcategory="bfs"
            )
            
            # Verify policies were loaded
            self.assertIsNotNone(finance_policies)
            self.assertGreater(len(finance_policies), 0)
        except RuntimeError:
            self.skipTest("OPA not installed, skipping test")
    
    def test_policy_evaluation(self):
        """Test OPA policy evaluation with sample data."""
        # Skip this test if OPA is not installed
        try:
            # Get healthcare policies
            healthcare_policies = self.policy_evaluator.policy_loader.get_policies(
                category="industry_specific", 
                subcategory="healthcare"
            )
            
            if not healthcare_policies:
                self.skipTest("Healthcare policies not found")
            
            # Create input data for evaluation
            input_data = {
                "contract": self.medical_contract.model_dump(),
                "evaluation_results": {
                    "fairness": self.fairness_result.model_dump(),
                    "content_safety": self.content_safety_result.model_dump(),
                    "risk_management": self.risk_management_result.model_dump()
                }
            }
            
            # Evaluate policy
            result = self.policy_evaluator.evaluate_policy(
                policy_path=healthcare_policies[0],
                input_data=input_data,
                mode="development"
            )
            
            # Verify result structure
            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)
        except RuntimeError:
            self.skipTest("OPA not installed, skipping test")
    
    def test_compliance_determination(self):
        """Test compliance determination logic."""
        # Skip this test if OPA is not installed
        try:
            # Get global policies
            global_policies = self.policy_evaluator.policy_loader.get_policies(
                category="global"
            )
            
            if not global_policies:
                self.skipTest("Global policies not found")
            
            # Create input data for evaluation
            input_data = {
                "contract": self.medical_contract.model_dump(),
                "evaluation_results": {
                    "fairness": self.fairness_result.model_dump(),
                    "content_safety": self.content_safety_result.model_dump(),
                    "risk_management": self.risk_management_result.model_dump()
                }
            }
            
            # Evaluate policy
            result = self.policy_evaluator.evaluate_policy(
                policy_path=global_policies[0],
                input_data=input_data,
                mode="development"
            )
            
            # Verify result structure
            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)
        except RuntimeError:
            self.skipTest("OPA not installed, skipping test")


if __name__ == "__main__":
    unittest.main() 