"""
Phase 1 Implementation Validation Tests

This module contains tests to validate the Phase 1 implementation of AICertify,
focusing on domain-specific context creation, contract enhancement, and evaluation.
"""

import os
import unittest
import tempfile

from aicertify.models.contract_models import (
    create_contract,
    validate_contract,
    save_contract,
)
from aicertify.context_helpers import (
    create_medical_context,
    create_financial_context,
    extract_demographics,
    extract_medical_history,
    extract_customer_demographics,
    extract_financial_profile,
)

# Import API module for evaluation if needed
try:
    # We don't actually use this import in the tests, but it's here to verify it's available
    from aicertify.api import evaluate_contract_comprehensive  # noqa: F401
except ImportError:
    pass


class TestPhase1Implementation(unittest.TestCase):
    """Test cases for Phase 1 implementation validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Sample patient case for medical tests
        self.patient_case = """**Patient Case Report**
        **Patient Information:**
        - Name: Test Patient
        - DoB: 01/01/1980
        - Sex: M
        - Weight: 180 lbs
        - Height: 5'11"

        **History of Present Illness:**
        A 45-year-old male with chest pain.

        **Past Medical History:**
        - Hypertension
        - Hyperlipidemia
        """

        # Sample customer data for financial tests
        self.customer_data = {
            "name": "Test Customer",
            "age": 35,
            "email": "test@example.com",
            "zip_code": 12345,
            "annual_income": 50000,
            "credit_score": 700,
            "assets": 100000,
            "current_debts": 20000,
            "employment_status": "Full-time",
            "length_credit_history": 10,
            "payment_history": "Good",
            "loan_amount_requested": 30000,
            "purpose": "Home improvement",
            "collateral": "Home",
        }

        # Sample interactions for both domains
        self.interactions = [
            {
                "input_text": "What is the diagnosis?",
                "output_text": "Based on the symptoms, the diagnosis is...",
                "metadata": {"agent": "Test"},
            }
        ]

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_extract_demographics(self):
        """Test extraction of patient demographics."""
        demographics = extract_demographics(self.patient_case)
        self.assertEqual(demographics.get("name"), "Test Patient")
        self.assertEqual(demographics.get("sex"), "M")
        self.assertEqual(demographics.get("date_of_birth"), "01/01/1980")
        self.assertEqual(demographics.get("age"), 45)

    def test_extract_medical_history(self):
        """Test extraction of medical history."""
        history = extract_medical_history(self.patient_case)
        self.assertIn("present_illness", history)
        self.assertIn("past_conditions", history)
        self.assertIn("Hypertension", history["past_conditions"])

    def test_extract_customer_demographics(self):
        """Test extraction of customer demographics."""
        demographics = extract_customer_demographics(self.customer_data)
        self.assertEqual(demographics.get("name"), "Test Customer")
        self.assertEqual(demographics.get("age"), 35)
        self.assertEqual(demographics.get("email"), "test@example.com")

    def test_extract_financial_profile(self):
        """Test extraction of financial profile."""
        profile = extract_financial_profile(self.customer_data)
        self.assertEqual(profile.get("annual_income"), 50000)
        self.assertEqual(profile.get("credit_score"), 700)
        self.assertEqual(profile.get("loan_amount_requested"), 30000)
        self.assertIn("debt_to_income_ratio", profile)

    def test_create_medical_context(self):
        """Test creation of medical context."""
        specialists = ["Cardiology", "Neurology"]
        context = create_medical_context(self.patient_case, specialists)

        # Verify domain and specialty
        self.assertEqual(context.get("domain"), "healthcare")
        self.assertEqual(context.get("specialty"), "multi-specialist-diagnosis")

        # Verify patient data
        self.assertIn("patient_data", context)
        self.assertIn("demographics", context["patient_data"])
        self.assertIn("medical_history", context["patient_data"])

        # Verify risk documentation
        self.assertIn("risk_documentation", context)
        self.assertIn("Cardiology, Neurology", context["risk_documentation"])

        # Verify governance info
        self.assertIn("governance_info", context)
        self.assertIn("specialist_qualifications", context["governance_info"])
        self.assertEqual(
            context["governance_info"]["specialist_qualifications"]["Cardiology"],
            "board_certified",
        )

    def test_create_financial_context(self):
        """Test creation of financial context."""
        context = create_financial_context(self.customer_data, "personal_loan")

        # Verify domain and specialty
        self.assertEqual(context.get("domain"), "finance")
        self.assertEqual(context.get("specialty"), "loan_evaluation")

        # Verify customer data
        self.assertIn("customer_data", context)
        self.assertIn("demographics", context["customer_data"])
        self.assertIn("financial_profile", context["customer_data"])

        # Verify risk documentation
        self.assertIn("risk_documentation", context)
        self.assertIn("personal_loan", context["risk_documentation"])

        # Verify governance info
        self.assertIn("governance_info", context)
        self.assertIn("lending_protocols", context["governance_info"])
        self.assertIn("regulatory_frameworks", context["governance_info"])

    def test_create_medical_contract(self):
        """Test creation of a contract with medical context."""
        specialists = ["Cardiology", "Neurology"]
        medical_context = create_medical_context(self.patient_case, specialists)

        compliance_context = {
            "jurisdictions": ["us", "eu"],
            "frameworks": ["hipaa", "eu_ai_act", "healthcare"],
        }

        contract = create_contract(
            application_name="Medical Test",
            model_info={"model_name": "test-model"},
            interactions=self.interactions,
            final_output="Final diagnosis",
            context=medical_context,
            compliance_context=compliance_context,
        )

        # Verify contract was created with the right context
        self.assertEqual(contract.application_name, "Medical Test")
        self.assertEqual(contract.context.get("domain"), "healthcare")
        self.assertEqual(contract.compliance_context.get("jurisdictions"), ["us", "eu"])

        # Validate the contract
        self.assertTrue(validate_contract(contract))

        # Save the contract
        file_path = save_contract(contract, self.temp_dir)
        self.assertTrue(os.path.exists(file_path))

    def test_create_financial_contract(self):
        """Test creation of a contract with financial context."""
        financial_context = create_financial_context(
            self.customer_data, "personal_loan"
        )

        compliance_context = {
            "jurisdictions": ["us", "eu"],
            "frameworks": ["fair_lending", "eu_ai_act", "financial"],
        }

        contract = create_contract(
            application_name="Financial Test",
            model_info={"model_name": "test-model"},
            interactions=self.interactions,
            final_output="Loan approved",
            context=financial_context,
            compliance_context=compliance_context,
        )

        # Verify contract was created with the right context
        self.assertEqual(contract.application_name, "Financial Test")
        self.assertEqual(contract.context.get("domain"), "finance")
        self.assertEqual(contract.compliance_context.get("jurisdictions"), ["us", "eu"])

        # Validate the contract
        self.assertTrue(validate_contract(contract))

        # Save the contract
        file_path = save_contract(contract, self.temp_dir)
        self.assertTrue(os.path.exists(file_path))

    def test_invalid_medical_contract(self):
        """Test validation of an invalid medical contract."""
        # Create an invalid medical context (missing risk_documentation)
        invalid_context = {
            "domain": "healthcare",
            "specialty": "multi-specialist-diagnosis",
            "patient_data": {"demographics": extract_demographics(self.patient_case)},
            # Missing risk_documentation
        }

        try:
            # This should raise a validation error
            create_contract(
                application_name="Invalid Medical Test",
                model_info={"model_name": "test-model"},
                interactions=self.interactions,
                context=invalid_context,
            )
            # If we get here, validation didn't fail as expected
            self.fail("Expected validation to fail for invalid medical contract")
        except ValueError as e:
            # Validation failed as expected
            self.assertIn("risk documentation", str(e).lower())

    def test_invalid_financial_contract(self):
        """Test validation of an invalid financial contract."""
        # Create an invalid financial context (missing customer_data)
        invalid_context = {
            "domain": "finance",
            "specialty": "loan_evaluation",
            "risk_documentation": "Risk documentation",
            # Missing customer_data
        }

        try:
            # This should raise a validation error
            create_contract(
                application_name="Invalid Financial Test",
                model_info={"model_name": "test-model"},
                interactions=self.interactions,
                context=invalid_context,
            )
            # If we get here, validation didn't fail as expected
            self.fail("Expected validation to fail for invalid financial contract")
        except ValueError as e:
            # Validation failed as expected
            self.assertIn("customer data", str(e).lower())


if __name__ == "__main__":
    unittest.main()
