"""
Domain-Specific Context Helpers for AICertify

This module provides helper functions for creating domain-specific context
for different application domains like healthcare and finance.
"""

import logging
from typing import Dict, Any, List, Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def extract_demographics(patient_case: str) -> Dict[str, Any]:
    """
    Extract patient demographics from case description.
    
    Args:
        patient_case: String containing patient case information
        
    Returns:
        Dictionary containing extracted demographics
    """
    demographics = {}
    
    # Extract information using regex patterns
    name_match = re.search(r"Name:\s*([^\n]+)", patient_case)
    if name_match:
        demographics["name"] = name_match.group(1).strip()
    
    dob_match = re.search(r"DoB:\s*([^\n]+)", patient_case)
    if dob_match:
        demographics["date_of_birth"] = dob_match.group(1).strip()
    
    sex_match = re.search(r"Sex:\s*([^\n]+)", patient_case)
    if sex_match:
        demographics["sex"] = sex_match.group(1).strip()
    
    age_match = re.search(r"(\d+)-year-old", patient_case)
    if age_match:
        demographics["age"] = int(age_match.group(1))
    
    weight_match = re.search(r"Weight:\s*([^\n]+)", patient_case)
    if weight_match:
        demographics["weight"] = weight_match.group(1).strip()
    
    height_match = re.search(r"Height:\s*([^\n]+)", patient_case)
    if height_match:
        demographics["height"] = height_match.group(1).strip()
    
    return demographics

def extract_medical_history(patient_case: str) -> Dict[str, Any]:
    """
    Extract medical history from case description.
    
    Args:
        patient_case: String containing patient case information
        
    Returns:
        Dictionary containing extracted medical history
    """
    history = {}
    
    # Extract present illness
    present_illness_match = re.search(
        r"History of Present Illness:(.+?)(?=\*\*|\Z)", 
        patient_case, 
        re.DOTALL
    )
    if present_illness_match:
        history["present_illness"] = present_illness_match.group(1).strip()
    
    # Extract past medical history
    past_history_match = re.search(
        r"Past Medical History:(.+?)(?=\*\*|\Z)", 
        patient_case, 
        re.DOTALL
    )
    if past_history_match:
        past_history_text = past_history_match.group(1).strip()
        # Extract individual conditions
        conditions = []
        for line in past_history_text.split("\n"):
            line = line.strip()
            if line.startswith("-"):
                conditions.append(line[1:].strip())
        
        history["past_conditions"] = conditions
        history["past_history_text"] = past_history_text
    
    return history

def generate_medical_risk_documentation(
    patient_case: str, 
    specialists_involved: List[str]
) -> str:
    """
    Generate risk documentation for medical applications.
    
    Args:
        patient_case: Patient case information
        specialists_involved: List of medical specialists involved
        
    Returns:
        String containing risk documentation
    """
    # Extract demographics for risk assessment
    demographics = extract_demographics(patient_case)
    
    # Generate appropriate risk documentation
    risk_doc = f"""
Risk Assessment:
- Patient Demographics: {demographics.get('age', 'Unknown age')} year-old {demographics.get('sex', 'Unknown gender')}
- Medical Complexity: Multiple specialists involved ({', '.join(specialists_involved)})
- Decision Complexity: High - requires integration of multiple specialist perspectives

Mitigation Measures:
- Multi-specialist consensus required for final diagnosis
- All specialist recommendations documented and reviewed
- Patient-specific factors considered in diagnostic process
- Diagnosis includes confidence level assessment

Monitoring System:
- Comprehensive logging of specialist interactions
- Fairness evaluation across demographic groups
- Content safety checks for medical appropriateness
- Risk management assessment for diagnostic protocol
"""
    
    return risk_doc.strip()

def create_medical_context(
    patient_case: str, 
    specialists_involved: List[str],
    specialty: str = "multi-specialist-diagnosis"
) -> Dict[str, Any]:
    """
    Create domain-specific context for medical applications.
    
    Args:
        patient_case: Patient case information
        specialists_involved: List of medical specialists involved
        specialty: Specific medical specialty area
        
    Returns:
        Dictionary containing domain-specific context
    """
    return {
        "domain": "healthcare",
        "specialty": specialty,
        "patient_data": {
            "demographics": extract_demographics(patient_case),
            "medical_history": extract_medical_history(patient_case)
        },
        "risk_documentation": generate_medical_risk_documentation(patient_case, specialists_involved),
        "governance_info": {
            "specialist_qualifications": {specialist: "board_certified" for specialist in specialists_involved},
            "diagnostic_protocols": {"protocol": "multi-specialist-consensus", "version": "1.0"},
            "medical_guidelines_followed": ["standard_of_care", "evidence_based_practice"]
        }
    }

def extract_customer_demographics(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract customer demographics from customer data.
    
    Args:
        customer_data: Dictionary containing customer information
        
    Returns:
        Dictionary containing extracted demographics
    """
    demographics = {}
    
    # Extract relevant fields
    if hasattr(customer_data, "name"):
        demographics["name"] = customer_data.name
    elif "name" in customer_data:
        demographics["name"] = customer_data["name"]
    
    if hasattr(customer_data, "age"):
        demographics["age"] = customer_data.age
    elif "age" in customer_data:
        demographics["age"] = customer_data["age"]
    
    if hasattr(customer_data, "zip_code"):
        demographics["zip_code"] = customer_data.zip_code
    elif "zip_code" in customer_data:
        demographics["zip_code"] = customer_data["zip_code"]
    
    if hasattr(customer_data, "email"):
        demographics["email"] = customer_data.email
    elif "email" in customer_data:
        demographics["email"] = customer_data["email"]
        
    return demographics

def extract_financial_profile(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract financial profile from customer data.
    
    Args:
        customer_data: Dictionary containing customer information
        
    Returns:
        Dictionary containing extracted financial profile
    """
    profile = {}
    
    # Extract financial fields
    for field in ["annual_income", "credit_score", "assets", "current_debts", 
                 "employment_status", "length_credit_history", "payment_history"]:
        if hasattr(customer_data, field):
            profile[field] = getattr(customer_data, field)
        elif field in customer_data:
            profile[field] = customer_data[field]
    
    # Calculate debt-to-income ratio if possible
    if "annual_income" in profile and "current_debts" in profile and profile["annual_income"] > 0:
        profile["debt_to_income_ratio"] = profile["current_debts"] / profile["annual_income"]
    
    # Extract loan request details
    for field in ["loan_amount_requested", "purpose", "collateral"]:
        if hasattr(customer_data, field):
            profile[field] = getattr(customer_data, field)
        elif field in customer_data:
            profile[field] = customer_data[field]
    
    return profile

def generate_financial_risk_documentation(
    customer_data: Dict[str, Any], 
    loan_type: str
) -> str:
    """
    Generate risk documentation for financial applications.
    
    Args:
        customer_data: Customer information
        loan_type: Type of loan being processed
        
    Returns:
        String containing risk documentation
    """
    # Extract financial profile for risk assessment
    financial_profile = extract_financial_profile(customer_data)
    
    # Generate appropriate risk documentation
    risk_doc = f"""
Risk Assessment:
- Customer Financial Profile: Credit Score {financial_profile.get('credit_score', 'Unknown')}
- Loan Type: {loan_type}
- Decision Complexity: Medium - requires verification of multiple financial factors

Mitigation Measures:
- Standardized loan evaluation criteria applied
- Customer-specific factors considered in loan decision
- Decision includes confidence level assessment
- Multiple data points verified for accuracy

Monitoring System:
- Comprehensive logging of evaluation process
- Fairness evaluation across demographic groups
- Content safety checks for financial advice appropriateness
- Risk management assessment for lending protocol
"""
    
    return risk_doc.strip()

def create_financial_context(
    customer_data: Dict[str, Any],
    loan_type: str,
    specialty: str = "loan_evaluation"
) -> Dict[str, Any]:
    """
    Create domain-specific context for financial applications.
    
    Args:
        customer_data: Customer information
        loan_type: Type of loan being processed
        specialty: Specific financial specialty area
        
    Returns:
        Dictionary containing domain-specific context
    """
    return {
        "domain": "finance",
        "specialty": specialty,
        "customer_data": {
            "demographics": extract_customer_demographics(customer_data),
            "financial_profile": extract_financial_profile(customer_data)
        },
        "risk_documentation": generate_financial_risk_documentation(customer_data, loan_type),
        "governance_info": {
            "loan_officer_qualification": "certified",
            "lending_protocols": {"protocol": "standard_evaluation", "version": "2.1"},
            "regulatory_frameworks": ["fair_lending", "responsible_banking"],
            "audit_trail": True
        }
    } 