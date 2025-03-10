#!/usr/bin/env python3
"""
Test script for the ModelCard interface.
This script addresses tests MC-01 through MC-05 in the EU AI Act Implementation Test Plan.
"""

import os
import sys
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("test_model_card")

# Add the parent directory to the path so we can import from aicertify
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the ModelCard class and helper functions
try:
    from aicertify.models.model_card import ModelCard, create_model_card, get_compliance_level
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    logger.error(f"Error importing ModelCard: {str(e)}")
    IMPORTS_SUCCESSFUL = False

def test_minimal_model_card():
    """
    Test MC-01: Create minimal valid ModelCard.
    Verify that a ModelCard object can be created with just the required fields.
    """
    logger.info("Starting test for minimal valid ModelCard (MC-01)")
    
    if not IMPORTS_SUCCESSFUL:
        logger.error("Cannot run test due to import errors")
        return False
    
    try:
        # Create a minimal ModelCard with only required fields
        minimal_card = ModelCard(
            model_name="TestModel",
            model_type="text-generation",
            organization="Test Organization",
            primary_uses=["Testing"],
            description="A test model for validation"
        )
        
        logger.info("Successfully created minimal ModelCard")
        logger.info(f"ModelCard fields: {minimal_card.dict(exclude_none=True)}")
        
        # Verify that the required fields are set correctly
        assert minimal_card.model_name == "TestModel"
        assert minimal_card.model_type == "text-generation"
        assert minimal_card.organization == "Test Organization"
        assert minimal_card.primary_uses == ["Testing"]
        assert minimal_card.description == "A test model for validation"
        
        logger.info("All required fields are set correctly")
        return True
    
    except Exception as e:
        logger.error(f"Error creating minimal ModelCard: {str(e)}")
        return False

def test_comprehensive_model_card():
    """
    Test MC-02: Create comprehensive ModelCard with all fields.
    Verify that a ModelCard object can be created with all fields populated.
    """
    logger.info("Starting test for comprehensive ModelCard (MC-02)")
    
    if not IMPORTS_SUCCESSFUL:
        logger.error("Cannot run test due to import errors")
        return False
    
    try:
        # Create a comprehensive ModelCard with all fields
        comprehensive_card = ModelCard(
            # Basic Information
            model_name="ComprehensiveModel",
            model_version="1.0.0",
            model_type="text-generation",
            organization="Test Organization",
            
            # Intended Use
            primary_uses=["Medical diagnosis assistance", "Healthcare information"],
            out_of_scope_uses=["Direct medical diagnosis without human review"],
            
            # Model Details
            description="Large language model fine-tuned for healthcare domain.",
            model_architecture="Transformer-based with 1B parameters",
            input_format="Natural language text queries",
            output_format="Natural language text responses",
            
            # Performance
            performance_metrics={
                "accuracy": 0.92,
                "f1_score": 0.89
            },
            benchmark_results={
                "medical_qa": {"accuracy": 0.85},
                "clinical_notes": {"precision": 0.88}
            },
            decision_thresholds={
                "confidence": 0.75
            },
            
            # Data
            training_data={
                "source": "Medical journals and textbooks",
                "size": "10TB",
                "preprocessing": "Standard NLP preprocessing"
            },
            evaluation_data={
                "source": "Clinical validation set",
                "size": "1000 examples"
            },
            
            # Risk & Mitigation
            ethical_considerations=[
                "Data privacy concerns",
                "Potential biases in medical training data"
            ],
            limitations=[
                "Limited knowledge cutoff",
                "Not a replacement for medical professionals"
            ],
            bias_considerations={
                "gender_bias": "Mitigated through balanced training data",
                "age_bias": "Ongoing monitoring required"
            },
            mitigation_strategies=[
                "Human oversight required for all diagnoses",
                "Clear confidence levels provided with responses"
            ],
            
            # Usage Guidelines
            usage_guidelines=[
                "Use only as a support tool for healthcare professionals",
                "Verify outputs with medical literature"
            ],
            human_oversight_measures=[
                "All outputs reviewed by qualified medical professionals",
                "Confidence thresholds for automated responses"
            ],
            
            # EU AI Act Compliance
            risk_category="high",
            relevant_articles=["Article 10", "Article 14"],
            
            # Additional Information
            additional_info={
                "developer_contact": "contact@testorganization.com",
                "model_release_date": "2025-01-15"
            }
        )
        
        logger.info("Successfully created comprehensive ModelCard")
        
        # Verify that all fields are set correctly (checking a few key fields)
        assert comprehensive_card.model_name == "ComprehensiveModel"
        assert comprehensive_card.risk_category == "high"
        assert len(comprehensive_card.ethical_considerations) == 2
        assert comprehensive_card.performance_metrics["accuracy"] == 0.92
        
        logger.info("All fields are set correctly")
        return True
    
    except Exception as e:
        logger.error(f"Error creating comprehensive ModelCard: {str(e)}")
        return False

def test_model_card_validation():
    """
    Test MC-03: Verify ModelCard validation.
    Test that invalid values raise appropriate validation errors.
    """
    logger.info("Starting test for ModelCard validation (MC-03)")
    
    if not IMPORTS_SUCCESSFUL:
        logger.error("Cannot run test due to import errors")
        return False
    
    # Test missing required fields
    try:
        # Missing required fields
        invalid_card = ModelCard(
            model_name="InvalidModel",
            # Missing model_type
            organization="Test Organization",
            # Missing primary_uses
            description="A test model for validation"
        )
        logger.error("Created ModelCard with missing required fields, but should have failed")
        return False
    except Exception as e:
        logger.info(f"Correctly failed with missing required fields: {str(e)}")
    
    # Test invalid risk_category
    try:
        # Invalid risk_category
        invalid_card = ModelCard(
            model_name="InvalidModel",
            model_type="text-generation",
            organization="Test Organization",
            primary_uses=["Testing"],
            description="A test model for validation",
            risk_category="invalid_category"  # Not in allowed values
        )
        logger.error("Created ModelCard with invalid risk_category, but should have failed")
        return False
    except Exception as e:
        logger.info(f"Correctly failed with invalid risk_category: {str(e)}")
    
    logger.info("All validation tests passed")
    return True

def test_create_model_card_helper():
    """
    Test MC-04: Test helper function create_model_card.
    Verify that the helper function creates a valid ModelCard.
    """
    logger.info("Starting test for create_model_card helper function (MC-04)")
    
    if not IMPORTS_SUCCESSFUL:
        logger.error("Cannot run test due to import errors")
        return False
    
    try:
        # Use the helper function to create a ModelCard
        model_card = create_model_card(
            model_name="HelperModel",
            model_type="text-generation",
            organization="Helper Organization",
            primary_uses=["Testing helper function"],
            description="A test model created with the helper function",
            # Additional fields
            model_version="1.0.0",
            risk_category="limited",
            ethical_considerations=["Test consideration"]
        )
        
        logger.info("Successfully created ModelCard using helper function")
        
        # Verify that the fields are set correctly
        assert model_card.model_name == "HelperModel"
        assert model_card.model_type == "text-generation"
        assert model_card.model_version == "1.0.0"
        assert model_card.risk_category == "limited"
        assert model_card.ethical_considerations == ["Test consideration"]
        
        logger.info("All fields are set correctly")
        return True
    
    except Exception as e:
        logger.error(f"Error using create_model_card helper: {str(e)}")
        return False

def test_compliance_level():
    """
    Test MC-05: Test get_compliance_level for different ModelCard completeness levels.
    Verify that the function returns the appropriate level based on completeness.
    """
    logger.info("Starting test for get_compliance_level function (MC-05)")
    
    if not IMPORTS_SUCCESSFUL:
        logger.error("Cannot run test due to import errors")
        return False
    
    try:
        # Create a minimal ModelCard
        minimal_card = ModelCard(
            model_name="MinimalModel",
            model_type="text-generation",
            organization="Test Organization",
            primary_uses=["Testing"],
            description="A minimal test model"
        )
        
        # Create a partial ModelCard
        partial_card = ModelCard(
            model_name="PartialModel",
            model_type="text-generation",
            organization="Test Organization",
            primary_uses=["Testing"],
            description="A partial test model",
            model_version="1.0.0",
            out_of_scope_uses=["Not for production"],
            model_architecture="Transformer",
            input_format="Text",
            output_format="Text",
            performance_metrics={"accuracy": 0.9},
            ethical_considerations=["Test consideration"],
            limitations=["Test limitation"],
            risk_category="limited"
        )
        
        # Use the comprehensive card from test_comprehensive_model_card
        comprehensive_card = ModelCard(
            # Basic Information
            model_name="ComprehensiveModel",
            model_version="1.0.0",
            model_type="text-generation",
            organization="Test Organization",
            primary_uses=["Medical diagnosis assistance"],
            out_of_scope_uses=["Direct medical diagnosis"],
            description="Comprehensive test model",
            model_architecture="Transformer",
            input_format="Text",
            output_format="Text",
            performance_metrics={"accuracy": 0.9},
            benchmark_results={"test": {"score": 0.8}},
            decision_thresholds={"threshold": 0.7},
            training_data={"source": "Test"},
            evaluation_data={"source": "Test"},
            ethical_considerations=["Test"],
            limitations=["Test"],
            bias_considerations={"bias": "Test"},
            mitigation_strategies=["Test"],
            usage_guidelines=["Test"],
            human_oversight_measures=["Test"],
            risk_category="high",
            relevant_articles=["Article 10"],
            additional_info={"test": "value"}
        )
        
        # Check compliance levels
        minimal_level = get_compliance_level(minimal_card)
        partial_level = get_compliance_level(partial_card)
        comprehensive_level = get_compliance_level(comprehensive_card)
        
        logger.info(f"Minimal card compliance level: {minimal_level}")
        logger.info(f"Partial card compliance level: {partial_level}")
        logger.info(f"Comprehensive card compliance level: {comprehensive_level}")
        
        # Verify the compliance levels
        assert minimal_level == "minimal"
        assert partial_level == "partial"
        assert comprehensive_level == "comprehensive"
        
        logger.info("All compliance levels are correct")
        return True
    
    except Exception as e:
        logger.error(f"Error testing compliance levels: {str(e)}")
        return False

def run_all_tests():
    """Run all ModelCard tests and report results."""
    tests = [
        ("MC-01", test_minimal_model_card),
        ("MC-02", test_comprehensive_model_card),
        ("MC-03", test_model_card_validation),
        ("MC-04", test_create_model_card_helper),
        ("MC-05", test_compliance_level)
    ]
    
    results = {}
    
    for test_id, test_func in tests:
        logger.info(f"\n=== Running test {test_id} ===")
        try:
            result = test_func()
            results[test_id] = result
            if result:
                print(f"\n✅ PASS: {test_id}")
            else:
                print(f"\n❌ FAIL: {test_id}")
        except Exception as e:
            logger.error(f"Exception in test {test_id}: {str(e)}")
            results[test_id] = False
            print(f"\n❌ FAIL: {test_id} (exception)")
    
    # Print summary
    print("\n=== Test Summary ===")
    for test_id, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_id}: {status}")
    
    return all(results.values())

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 