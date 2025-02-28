"""
AICertify Risk Management Evaluator

This module provides the RiskManagementEvaluator class for assessing the 
completeness and quality of risk management documentation and practices.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union, Tuple
import re

from aicertify.evaluators.base_evaluator import BaseEvaluator, EvaluationResult

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class RiskManagementEvaluator(BaseEvaluator):
    """
    Evaluator for assessing risk management documentation and practices.
    
    This evaluator performs static analysis of risk documentation to ensure:
    1. Risk assessment completeness
    2. Mitigation measures documentation
    3. Monitoring systems implementation
    """
    
    def _initialize(self) -> None:
        """Initialize the risk management evaluator."""
        # Risk documentation requirements
        self.risk_assessment_keywords = [
            "risk assessment", "risk analysis", "identified risks", "risk factors",
            "probability", "likelihood", "impact", "severity", "risk matrix"
        ]
        
        self.mitigation_keywords = [
            "mitigation", "control measure", "risk reduction", "safeguard",
            "prevention", "contingency", "remediation", "risk response"
        ]
        
        self.monitoring_keywords = [
            "monitoring", "oversight", "surveillance", "tracking", "follow-up",
            "continuous assessment", "audit", "review process", "verification"
        ]
        
        # Required sections and weights
        self.required_sections = {
            "risk_assessment": {
                "weight": 0.4,
                "keywords": self.risk_assessment_keywords,
                "required_elements": [
                    "identification", "classification", "severity", "probability"
                ]
            },
            "mitigation_measures": {
                "weight": 0.3,
                "keywords": self.mitigation_keywords,
                "required_elements": [
                    "control measures", "implementation", "responsibility", "timeline"
                ]
            },
            "monitoring_system": {
                "weight": 0.3,
                "keywords": self.monitoring_keywords,
                "required_elements": [
                    "metrics", "indicators", "frequency", "reporting"
                ]
            }
        }
        
        logger.info("Risk management evaluator initialized")
    
    def evaluate(self, data: Dict) -> EvaluationResult:
        """
        Evaluate risk management based on input data.
        
        Args:
            data: Dictionary containing contract data and context
                Should include 'context.risk_documentation' with risk management text
                
        Returns:
            EvaluationResult object containing risk management evaluation results
        """
        # Extract risk documentation from context
        context = data.get('context', {})
        risk_documentation = context.get('risk_documentation', '')
        
        if not risk_documentation:
            # Try to infer risk documentation from interaction outputs
            risk_documentation = self._extract_risk_info_from_interactions(data.get('interactions', []))
        
        if not risk_documentation:
            return self._create_empty_result("No risk documentation found in contract data")
        
        # Evaluate each section
        section_results = {}
        overall_score = 0.0
        
        for section_name, section_config in self.required_sections.items():
            section_score, section_details = self._evaluate_section(
                risk_documentation, 
                section_config["keywords"],
                section_config["required_elements"]
            )
            
            # Apply section weight to overall score
            overall_score += section_score * section_config["weight"]
            
            section_results[section_name] = {
                "score": section_score,
                "weight": section_config["weight"],
                "details": section_details
            }
        
        # Determine compliance
        compliant = overall_score >= self.threshold
        
        # Generate reason
        if compliant:
            reason = f"Risk management documentation passes with score {overall_score:.2f} (threshold: {self.threshold:.2f})"
        else:
            reason = f"Risk management documentation fails with score {overall_score:.2f} (threshold: {self.threshold:.2f})"
            
            # Add specific issues
            issues = []
            for section_name, result in section_results.items():
                section_score = result["score"]
                if section_score < 0.7:  # Arbitrary threshold for highlighting issues
                    display_name = section_name.replace("_", " ").title()
                    issues.append(f"{display_name} score is low ({section_score:.2f})")
            
            if issues:
                reason += ". Issues: " + "; ".join(issues)
        
        # Create detailed results
        details = {
            "overall_score": overall_score,
            "section_results": section_results,
            "documentation_length": len(risk_documentation),
            "threshold": self.threshold
        }
        
        return EvaluationResult(
            evaluator_name="Risk Management Evaluator",
            compliant=compliant,
            score=overall_score,
            threshold=self.threshold,
            reason=reason,
            details=details
        )
    
    async def evaluate_async(self, data: Dict) -> EvaluationResult:
        """
        Asynchronously evaluate risk management.
        
        This is simply a wrapper around the synchronous evaluate method.
        
        Args:
            data: Dictionary containing the data to evaluate
            
        Returns:
            EvaluationResult object containing risk management evaluation results
        """
        return self.evaluate(data)
    
    def _evaluate_section(
        self, 
        documentation: str, 
        keywords: List[str],
        required_elements: List[str]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate a section of risk management documentation.
        
        Args:
            documentation: The full risk documentation text
            keywords: List of keywords to identify the section
            required_elements: List of required elements in the section
            
        Returns:
            Tuple of (score, details) where score is 0.0-1.0 and details are
            the evaluation details
        """
        # Count keyword occurrences (case insensitive)
        keyword_counts = {}
        for keyword in keywords:
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            count = len(pattern.findall(documentation))
            keyword_counts[keyword] = count
        
        # Check for presence of required elements
        element_presence = {}
        for element in required_elements:
            pattern = re.compile(r'\b' + re.escape(element) + r'\b', re.IGNORECASE)
            present = bool(pattern.search(documentation))
            element_presence[element] = present
        
        # Calculate keyword coverage score
        total_keywords = len(keywords)
        keywords_present = sum(1 for count in keyword_counts.values() if count > 0)
        keyword_coverage = keywords_present / total_keywords if total_keywords > 0 else 0
        
        # Calculate element coverage score
        total_elements = len(required_elements)
        elements_present = sum(1 for present in element_presence.values() if present)
        element_coverage = elements_present / total_elements if total_elements > 0 else 0
        
        # Combined score with 60% weight on elements and 40% on keywords
        score = (element_coverage * 0.6) + (keyword_coverage * 0.4)
        
        return score, {
            "keyword_counts": keyword_counts,
            "keyword_coverage": keyword_coverage,
            "element_presence": element_presence,
            "element_coverage": element_coverage,
            "keywords_present": keywords_present,
            "total_keywords": total_keywords,
            "elements_present": elements_present,
            "total_elements": total_elements
        }
    
    def _extract_risk_info_from_interactions(self, interactions: List[Dict]) -> str:
        """
        Attempt to extract risk management information from interactions.
        
        Args:
            interactions: List of interaction dictionaries
            
        Returns:
            String containing extracted risk-related content
        """
        if not interactions:
            return ""
        
        # Create a combined string of all responses
        all_text = " ".join([
            interaction.get("output_text", "") for interaction in interactions
        ])
        
        # Find paragraphs or sections that mention risk
        risk_pattern = re.compile(
            r'(?i)(?:[^\n.!?]*(?:risk|hazard|danger|safety|mitigation|monitoring)[^\n.!?]*[.!?])',
            re.MULTILINE
        )
        
        risk_statements = risk_pattern.findall(all_text)
        
        if not risk_statements:
            return ""
            
        return "\n".join(risk_statements)
    
    def _create_empty_result(self, message: str) -> EvaluationResult:
        """Create a result when input data is invalid."""
        return EvaluationResult(
            evaluator_name="Risk Management Evaluator",
            compliant=False,
            score=0.0,
            threshold=self.threshold,
            reason=message,
            details={"error": message}
        ) 