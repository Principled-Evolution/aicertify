#!/usr/bin/env python3
"""
Test script to verify that the developer guide examples for EU AI Act compliance work as documented.
This script addresses test DX-01 in the EU AI Act Implementation Test Plan.
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("test_developer_guide_examples")

# Add the parent directory to the path so we can import from aicertify
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the required modules
try:
    from aicertify.models.model_card import create_model_card
    from aicertify.models.contract_models import create_contract_with_model_card
    from aicertify.api import evaluate_eu_ai_act_compliance
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    logger.error(f"Error importing required modules: {str(e)}")
    IMPORTS_SUCCESSFUL = False

def test_model_card_creation():
    """Test the model card creation example from the developer guide."""
    logger.info("Testing model card creation example")
    
    if not IMPORTS_SUCCESSFUL:
        logger.error("Cannot run test due to import errors")
        return False
    
    try:
        # Create a model card as shown in the developer guide
        model_card = create_model_card(
            model_name="HealthcareGPT",
            model_type="text-generation",
            organization="Health AI Inc.",
            primary_uses=["Medical diagnosis assistance", "Healthcare information"],
            description="Large language model fine-tuned for healthcare domain.",
            # Additional fields
            model_version="1.0.0",
            out_of_scope_uses=["Direct medical diagnosis without human review"],
            model_architecture="Transformer-based with 1B parameters",
            input_format="Natural language text queries",
            output_format="Natural language text responses",
            performance_metrics={
                "accuracy": 0.92,
                "f1_score": 0.89
            },
            ethical_considerations=[
                "Data privacy concerns",
                "Potential biases in medical training data"
            ],
            limitations=[
                "Limited knowledge cutoff",
                "Not a replacement for medical professionals"
            ],
            mitigation_strategies=[
                "Human oversight required for all diagnoses",
                "Clear confidence levels provided with responses"
            ],
            risk_category="high",
            relevant_articles=["Article 10", "Article 14"]
        )
        
        logger.info("Successfully created model card")
        logger.info(f"Model card risk category: {model_card.risk_category}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error creating model card: {str(e)}")
        return False

def test_contract_creation():
    """Test the contract creation example from the developer guide."""
    logger.info("Testing contract creation example")
    
    if not IMPORTS_SUCCESSFUL:
        logger.error("Cannot run test due to import errors")
        return False
    
    try:
        # Create a model card
        model_card = create_model_card(
            model_name="HealthcareGPT",
            model_type="text-generation",
            organization="Health AI Inc.",
            primary_uses=["Medical diagnosis assistance", "Healthcare information"],
            description="Large language model fine-tuned for healthcare domain.",
            risk_category="high",
            relevant_articles=["Article 10", "Article 14"]
        )
        
        # Create a contract with the model card
        contract = create_contract_with_model_card(
            application_name="Healthcare Assistant",
            model_card=model_card,
            interactions=[
                {
                    "input_text": "What are the symptoms of pneumonia?",
                    "output_text": "Pneumonia symptoms include chest pain, cough, fatigue, fever, and shortness of breath.",
                    "metadata": {"topic": "medical_information"}
                }
            ]
        )
        
        logger.info("Successfully created contract with model card")
        logger.info(f"Contract application name: {contract.application_name}")
        logger.info(f"Number of interactions: {len(contract.interactions)}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error creating contract: {str(e)}")
        return False

async def test_eu_ai_act_evaluation():
    """Test the EU AI Act compliance evaluation example from the developer guide."""
    logger.info("Testing EU AI Act compliance evaluation example")
    
    if not IMPORTS_SUCCESSFUL:
        logger.error("Cannot run test due to import errors")
        return False
    
    try:
        # Create a model card
        model_card = create_model_card(
            model_name="HealthcareGPT",
            model_type="text-generation",
            organization="Health AI Inc.",
            primary_uses=["Medical diagnosis assistance", "Healthcare information"],
            description="Large language model fine-tuned for healthcare domain.",
            risk_category="high",
            relevant_articles=["Article 10", "Article 14"]
        )
        
        # Create a contract with the model card
        contract = create_contract_with_model_card(
            application_name="Healthcare Assistant",
            model_card=model_card,
            interactions=[
                {
                    "input_text": "What are the symptoms of pneumonia?",
                    "output_text": "Pneumonia symptoms include chest pain, cough, fatigue, fever, and shortness of breath.",
                    "metadata": {"topic": "medical_information"}
                }
            ]
        )
        
        # Create output directory
        output_dir = Path("test_reports")
        os.makedirs(output_dir, exist_ok=True)
        
        # Evaluate EU AI Act compliance
        result = await evaluate_eu_ai_act_compliance(
            contract=contract,
            focus_areas=["prohibited_practices", "documentation"],
            generate_report=True,
            report_format="pdf",
            output_dir=str(output_dir)
        )
        
        logger.info("Successfully evaluated EU AI Act compliance")
        logger.info(f"Overall compliance: {result.get('overall_compliant', False)}")
        logger.info(f"Model card compliance level: {result.get('model_card_compliance_level', 'N/A')}")
        logger.info(f"Report path: {result.get('report_path', 'No report generated')}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error evaluating EU AI Act compliance: {str(e)}")
        return False

def run_all_tests():
    """Run all developer guide example tests and report results."""
    tests = [
        ("DX-01-1", test_model_card_creation),
        ("DX-01-2", test_contract_creation),
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
    
    # Run the async test separately
    logger.info("\n=== Running test DX-01-3 ===")
    try:
        result = asyncio.run(test_eu_ai_act_evaluation())
        results["DX-01-3"] = result
        if result:
            print("\n✅ PASS: DX-01-3")
        else:
            print("\n❌ FAIL: DX-01-3")
    except Exception as e:
        logger.error(f"Exception in test DX-01-3: {str(e)}")
        results["DX-01-3"] = False
        print("\n❌ FAIL: DX-01-3 (exception)")
    
    # Print summary
    print("\n=== Test Summary ===")
    for test_id, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_id}: {status}")
    
    return all(results.values())

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 