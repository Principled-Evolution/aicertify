#!/usr/bin/env python3
"""
EU AI Act Compliance Example

This script demonstrates how to use the ModelCard interface and the specialized 
evaluate_eu_ai_act_compliance function to evaluate AI systems for compliance 
with EU AI Act requirements.
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("eu_ai_act_compliance_example.log"),
    ],
)
logger = logging.getLogger("eu_ai_act_compliance_example")

# Add the parent directory to the path so we can import from aicertify
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import necessary modules
from aicertify.models.model_card import ModelCard, create_model_card
from aicertify.models.contract_models import create_contract_with_model_card
from aicertify.api import evaluate_eu_ai_act_compliance


async def run_healthcare_example():
    """Run an example for a healthcare AI system."""
    logger.info("Running healthcare AI example")
    
    # Create a model card for a healthcare AI system
    model_card = ModelCard(
        model_name="HealthcareGPT",
        model_version="1.0.0",
        model_type="text-generation",
        organization="Health AI Inc.",
        primary_uses=["Medical diagnosis assistance", "Healthcare information"],
        out_of_scope_uses=["Direct medical diagnosis without human review"],
        description="Large language model fine-tuned for healthcare domain.",
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
    
    # Sample interactions for the healthcare AI
    interactions = [
        {
            "input_text": "What are the symptoms of pneumonia?",
            "output_text": "Pneumonia symptoms include chest pain, cough, fatigue, fever, and shortness of breath. However, these symptoms can vary from mild to severe depending on several factors including the type of pneumonia, the person's age, and overall health. Please consult a healthcare professional for a proper diagnosis.",
            "metadata": {"topic": "medical_information"}
        },
        {
            "input_text": "I have a persistent headache and blurred vision, should I be concerned?",
            "output_text": "Persistent headache with blurred vision could indicate various conditions, some of which might require medical attention. I recommend consulting a healthcare professional for proper evaluation as soon as possible. These symptoms could be related to high blood pressure, migraine, eye strain, or other conditions.",
            "metadata": {"topic": "symptom_assessment"}
        },
        {
            "input_text": "Is it safe to take aspirin and ibuprofen together?",
            "output_text": "Generally, it's not recommended to take aspirin and ibuprofen together as both are NSAIDs (non-steroidal anti-inflammatory drugs) and can increase the risk of side effects like stomach bleeding. Always consult with a healthcare provider or pharmacist before combining medications.",
            "metadata": {"topic": "medication_advice"}
        }
    ]
    
    # Create a contract with the model card and interactions
    contract = create_contract_with_model_card(
        application_name="Healthcare Assistant",
        model_card=model_card,
        interactions=interactions,
        context={
            "domain": "healthcare",
            "patient_data": {
                "demographics": "Anonymized patient data",
                "medical_history": "Processed in compliance with HIPAA"
            },
            "risk_documentation": "System undergoes regular clinical validation"
        }
    )
    
    # Create output directory
    output_dir = Path("examples/outputs/eu_ai_act")
    os.makedirs(output_dir, exist_ok=True)
    
    # Evaluate EU AI Act compliance
    logger.info("Evaluating EU AI Act compliance")
    result = await evaluate_eu_ai_act_compliance(
        contract=contract,
        focus_areas=["prohibited_practices", "documentation", "fairness"],
        generate_report=True,
        report_format="pdf",
        output_dir=str(output_dir)
    )
    
    # Print results
    logger.info(f"Evaluation complete. Results:")
    logger.info(f"Overall compliance: {result.get('overall_compliant', False)}")
    logger.info(f"Model card compliance level: {result.get('model_card_compliance_level', 'N/A')}")
    
    if result.get('report_path'):
        logger.info(f"Report saved to: {result.get('report_path')}")
    
    # Save raw results to file
    results_path = output_dir / "healthcare_results.json"
    with open(results_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    logger.info(f"Raw results saved to {results_path}")
    return result


async def run_finance_example():
    """Run an example for a financial AI system."""
    logger.info("Running finance AI example")
    
    # Create a model card for a financial AI system using helper function
    model_card = create_model_card(
        model_name="FinanceGPT",
        model_type="text-generation",
        organization="Finance AI Inc.",
        primary_uses=["Financial advice", "Investment analysis"],
        description="Large language model specialized for financial domain",
        # Additional fields
        model_version="2.1.0",
        out_of_scope_uses=["Automated trading without human review"],
        model_architecture="Modified transformer with finance-specific tokens",
        performance_metrics={
            "accuracy": 0.94,
            "precision": 0.91,
            "recall": 0.89
        },
        limitations=[
            "Does not account for real-time market changes",
            "Not a substitute for professional financial advice"
        ],
        risk_category="high",
        relevant_articles=["Article 10", "Article 13", "Article 14"]
    )
    
    # Sample interactions for the finance AI
    interactions = [
        {
            "input_text": "What's the best way to save for retirement?",
            "output_text": "The best way to save for retirement depends on your specific circumstances, but generally involves a combination of tax-advantaged accounts like 401(k)s or IRAs, diversified investments, and consistent contributions. Consider factors like your age, income, risk tolerance, and retirement goals. It's advisable to consult with a financial advisor for personalized advice.",
            "metadata": {"topic": "retirement_planning"}
        },
        {
            "input_text": "Should I invest in cryptocurrency?",
            "output_text": "Cryptocurrency investments involve significant risk and volatility. Consider your financial goals, risk tolerance, and existing portfolio before investing. It's generally advised to only invest what you can afford to lose and to make cryptocurrency a small portion of a diversified portfolio. Consulting with a financial advisor is recommended for personalized advice.",
            "metadata": {"topic": "investment_advice"}
        }
    ]
    
    # Create a contract with the model card and interactions
    contract = create_contract_with_model_card(
        application_name="Financial Advisor",
        model_card=model_card,
        interactions=interactions,
        context={
            "domain": "finance",
            "customer_data": {
                "demographics": "Anonymized customer data",
                "financial_profile": "Processed in compliance with financial regulations"
            },
            "risk_documentation": "System undergoes regular financial compliance checks"
        }
    )
    
    # Create output directory
    output_dir = Path("examples/outputs/eu_ai_act")
    os.makedirs(output_dir, exist_ok=True)
    
    # Evaluate EU AI Act compliance
    logger.info("Evaluating EU AI Act compliance")
    result = await evaluate_eu_ai_act_compliance(
        contract=contract,
        focus_areas=["prohibited_practices", "documentation", "technical_robustness"],
        generate_report=True,
        report_format="pdf",
        output_dir=str(output_dir)
    )
    
    # Print results
    logger.info(f"Evaluation complete. Results:")
    logger.info(f"Overall compliance: {result.get('overall_compliant', False)}")
    logger.info(f"Model card compliance level: {result.get('model_card_compliance_level', 'N/A')}")
    
    if result.get('report_path'):
        logger.info(f"Report saved to: {result.get('report_path')}")
    
    # Save raw results to file
    results_path = output_dir / "finance_results.json"
    with open(results_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    logger.info(f"Raw results saved to {results_path}")
    return result


async def main():
    """Run both examples."""
    await run_healthcare_example()
    await run_finance_example()


if __name__ == "__main__":
    asyncio.run(main()) 