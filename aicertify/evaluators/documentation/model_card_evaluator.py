"""
Model Card Evaluator for EU AI Act Documentation Requirements.

This evaluator assesses whether the model card documentation is compliant with
EU AI Act requirements for high-risk AI systems documentation.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from aicertify.evaluators.base_evaluator import BaseEvaluator, EvaluationResult

logger = logging.getLogger(__name__)


class ModelCardEvaluator(BaseEvaluator):
    """
    Evaluator for assessing technical documentation compliance using HuggingFace Model Card standards.
    
    This evaluator checks if the provided model documentation meets the requirements
    specified in EU AI Act Articles 11, 12, and 53 by evaluating the completeness
    and quality of the documentation against HuggingFace Model Card standards.
    """
    
    # Define the metrics supported by this evaluator
    SUPPORTED_METRICS: Tuple[str, ...] = (
        "model_card.score",
        "model_card.completeness",
        "model_card.quality",
        "model_card.section_scores",
        "model_card.compliance_level",
        "metrics.model_card.score",
        "metrics.model_card.completeness",
        "metrics.model_card.quality"
    )
    
    # Required sections based on HuggingFace Model Card standards and EU AI Act requirements
    REQUIRED_SECTIONS = {
        "model_details": {
            "name": "Model Details",
            "description": "Basic information about the model",
            "subsections": ["model_name", "model_type", "version", "organization"],
            "weight": 0.15,
            "eu_ai_act_reference": "Article 11(1)(a) - General description of the AI system",
        },
        "intended_use": {
            "name": "Intended Use",
            "description": "The intended use cases and users of the model",
            "subsections": ["primary_uses", "out_of_scope_uses"],
            "weight": 0.15,
            "eu_ai_act_reference": "Article 11(1)(b) - Description of the intended purpose of the AI system",
        },
        "factors": {
            "name": "Factors",
            "description": "Factors that may influence model performance",
            "subsections": ["relevant_factors", "evaluation_factors"],
            "weight": 0.10,
            "eu_ai_act_reference": "Article 11(1)(c) - Description of the elements of the AI system and the process for its development",
        },
        "metrics": {
            "name": "Metrics",
            "description": "Metrics used to evaluate the model",
            "subsections": ["performance_metrics", "decision_thresholds"],
            "weight": 0.10,
            "eu_ai_act_reference": "Article 11(1)(d) - Description of the key design choices and assumptions made",
        },
        "evaluation_data": {
            "name": "Evaluation Data",
            "description": "Data used to evaluate the model",
            "subsections": ["datasets", "motivation", "preprocessing"],
            "weight": 0.10,
            "eu_ai_act_reference": "Article 11(1)(e) - Description of the methods used to evaluate the AI system",
        },
        "training_data": {
            "name": "Training Data",
            "description": "Data used to train the model",
            "subsections": ["datasets", "motivation", "preprocessing"],
            "weight": 0.10,
            "eu_ai_act_reference": "Article 11(1)(f) - Description of the data used to train and test the AI system",
        },
        "quantitative_analyses": {
            "name": "Quantitative Analyses",
            "description": "Quantitative analyses of model performance",
            "subsections": ["unitary_results", "intersectional_results"],
            "weight": 0.05,
            "eu_ai_act_reference": "Article 11(1)(g) - Description of the performance metrics used to measure accuracy, robustness, and cybersecurity",
        },
        "ethical_considerations": {
            "name": "Ethical Considerations",
            "description": "Ethical considerations related to model use",
            "subsections": ["data_bias", "mitigations", "risks"],
            "weight": 0.15,
            "eu_ai_act_reference": "Article 11(1)(h) - Description of the risks to fundamental rights",
        },
        "caveats_recommendations": {
            "name": "Caveats and Recommendations",
            "description": "Caveats and recommendations for model use",
            "subsections": ["limitations", "recommendations"],
            "weight": 0.10,
            "eu_ai_act_reference": "Article 11(1)(i) - Description of the risk management measures",
        },
    }
    
    # Quality levels for content assessment
    QUALITY_LEVELS = {
        "missing": {
            "score": 0.0,
            "description": "Content is missing entirely"
        },
        "minimal": {
            "score": 0.3,
            "description": "Content is present but minimal or superficial"
        },
        "partial": {
            "score": 0.7,
            "description": "Content is present and provides some useful information"
        },
        "comprehensive": {
            "score": 1.0,
            "description": "Content is comprehensive and detailed"
        }
    }
    
    def __init__(
        self,
        compliance_threshold: float = 0.7,
        section_weights: Optional[Dict[str, float]] = None,
        content_quality_thresholds: Optional[Dict[str, int]] = None,
        **kwargs
    ):
        """
        Initialize the ModelCardEvaluator.
        
        Args:
            compliance_threshold: Overall threshold for compliance determination
            section_weights: Optional custom weights for different sections
            content_quality_thresholds: Optional character count thresholds for quality levels
            **kwargs: Additional configuration parameters
        """
        self.compliance_threshold = compliance_threshold
        self.section_weights = section_weights or {
            section_id: section_info["weight"]
            for section_id, section_info in self.REQUIRED_SECTIONS.items()
        }
        self.content_quality_thresholds = content_quality_thresholds or {
            "minimal": 50,
            "partial": 200,
            "comprehensive": 500
        }
        super().__init__(kwargs)
    
    def _initialize(self) -> None:
        """Initialize the evaluator with the configuration parameters."""
        # No additional initialization needed beyond what's in __init__
        pass
    
    async def evaluate_async(self, documentation: Dict[str, Any]) -> EvaluationResult:
        """
        Asynchronously evaluate model documentation for compliance with EU AI Act requirements.
        
        Args:
            documentation: Dictionary containing model documentation information
            
        Returns:
            EvaluationResult object containing evaluation results
        """
        # For now, just call the synchronous method
        return self.evaluate(documentation)
    
    def evaluate(self, documentation: Dict[str, Any]) -> EvaluationResult:
        """
        Evaluate model documentation for compliance with EU AI Act requirements.
        
        Args:
            documentation: A dictionary containing the model documentation
            
        Returns:
            EvaluationResult: The evaluation result
        """
        try:
            # Extract model card content
            model_card_content = documentation.get("model_card", {})
            
            # Evaluate each required section
            section_scores = {}
            section_feedback = {}
            section_quality = {}
            missing_sections = []
            incomplete_sections = []
            
            for section_id, section_info in self.REQUIRED_SECTIONS.items():
                section_content = model_card_content.get(section_id, {})
                section_score, section_feedback_items, quality_level = self._evaluate_section(
                    section_id, section_info, section_content
                )
                section_scores[section_id] = section_score
                section_feedback[section_id] = section_feedback_items
                section_quality[section_id] = quality_level
                
                if section_score == 0.0:
                    missing_sections.append(section_info["name"])
                elif section_score < 0.7:
                    incomplete_sections.append(section_info["name"])
            
            # Calculate overall compliance score
            overall_score = self._calculate_overall_score(section_scores)
            is_compliant = overall_score >= self.compliance_threshold
            
            # Generate detailed results
            detailed_results = {
                "overall_score": overall_score,
                "section_scores": section_scores,
                "section_feedback": section_feedback,
                "section_quality": section_quality,
                "compliance_threshold": self.compliance_threshold,
                "missing_sections": missing_sections,
                "incomplete_sections": incomplete_sections,
                "eu_ai_act_references": {
                    section_id: info["eu_ai_act_reference"] 
                    for section_id, info in self.REQUIRED_SECTIONS.items()
                }
            }
            
            # Generate recommendations
            recommendations = self._generate_recommendations(section_scores, section_feedback, section_quality)
            
            return EvaluationResult(
                evaluator_name="ModelCardEvaluator",
                compliant=is_compliant,
                score=overall_score,
                threshold=self.compliance_threshold,
                reason=self._generate_reason(is_compliant, overall_score, section_scores, missing_sections, incomplete_sections),
                details=detailed_results
            )
            
        except Exception as e:
            logger.error(f"Error in ModelCardEvaluator: {str(e)}")
            return EvaluationResult(
                evaluator_name="ModelCardEvaluator",
                compliant=False,
                score=0.0,
                threshold=self.compliance_threshold,
                reason="An error occurred during evaluation. Please check the error and try again.",
                details={"error": str(e)}
            )
    
    def _evaluate_section(
        self, section_id: str, section_info: Dict[str, Any], section_content: Dict[str, Any]
    ) -> Tuple[float, List[str], str]:
        """
        Evaluate a single section of the model card.
        
        Args:
            section_id: The ID of the section
            section_info: Information about the section
            section_content: The content of the section
            
        Returns:
            Tuple[float, List[str], str]: The section score, feedback, and quality level
        """
        if not section_content:
            return 0.0, [f"Missing section: {section_info['name']}"], "missing"
        
        feedback = []
        subsection_scores = []
        subsection_quality = []
        
        # Check for required subsections
        for subsection in section_info["subsections"]:
            if subsection not in section_content or not section_content[subsection]:
                feedback.append(f"Missing subsection: {subsection}")
                subsection_scores.append(0.0)
                subsection_quality.append("missing")
            else:
                content = section_content[subsection]
                quality_level, quality_score = self._assess_content_quality(content)
                subsection_scores.append(quality_score)
                subsection_quality.append(quality_level)
                
                if quality_level != "comprehensive":
                    feedback.append(f"Subsection {subsection} has {quality_level} content")
        
        # Calculate section score as average of subsection scores
        section_score = sum(subsection_scores) / len(section_info["subsections"]) if section_info["subsections"] else 0.0
        
        # Determine overall quality level for the section
        if section_score == 0.0:
            quality_level = "missing"
        elif section_score < 0.3:
            quality_level = "minimal"
        elif section_score < 0.7:
            quality_level = "partial"
        else:
            quality_level = "comprehensive"
        
        return section_score, feedback, quality_level
    
    def _assess_content_quality(self, content: Any) -> Tuple[str, float]:
        """
        Assess the quality of content based on length and structure.
        
        Args:
            content: The content to assess
            
        Returns:
            Tuple[str, float]: The quality level and score
        """
        if content is None:
            return "missing", 0.0
        
        # Convert content to string if it's not already
        if not isinstance(content, str):
            try:
                content = str(content)
            except:
                return "minimal", 0.3
        
        # Assess quality based on length
        content_length = len(content)
        
        if content_length == 0:
            return "missing", 0.0
        elif content_length < self.content_quality_thresholds["minimal"]:
            return "minimal", 0.3
        elif content_length < self.content_quality_thresholds["partial"]:
            return "partial", 0.7
        else:
            return "comprehensive", 1.0
    
    def _calculate_overall_score(self, section_scores: Dict[str, float]) -> float:
        """
        Calculate the overall compliance score.
        
        Args:
            section_scores: Scores for each section
            
        Returns:
            float: The overall compliance score
        """
        overall_score = 0.0
        
        for section_id, score in section_scores.items():
            weight = self.section_weights.get(section_id, 0.0)
            overall_score += score * weight
        
        return overall_score
    
    def _generate_reason(
        self, 
        is_compliant: bool, 
        overall_score: float, 
        section_scores: Dict[str, float],
        missing_sections: List[str],
        incomplete_sections: List[str]
    ) -> str:
        """
        Generate a reason string based on evaluation results.
        
        Args:
            is_compliant: Whether the documentation is compliant
            overall_score: The overall compliance score
            section_scores: Scores for each section
            missing_sections: List of missing sections
            incomplete_sections: List of incomplete sections
            
        Returns:
            str: The reason string
        """
        if is_compliant:
            return (
                f"The model documentation meets EU AI Act requirements with an overall "
                f"compliance score of {overall_score:.2f} (threshold: {self.compliance_threshold})."
            )
        
        # Generate reason for non-compliance
        reason = (
            f"The model documentation does not meet EU AI Act requirements. "
            f"Overall compliance score: {overall_score:.2f} (threshold: {self.compliance_threshold})."
        )
        
        if missing_sections:
            reason += f" Missing sections: {', '.join(missing_sections)}."
        
        if incomplete_sections:
            reason += f" Incomplete sections: {', '.join(incomplete_sections)}."
        
        return reason
    
    def _generate_recommendations(
        self, 
        section_scores: Dict[str, float],
        section_feedback: Dict[str, List[str]],
        section_quality: Dict[str, str]
    ) -> List[str]:
        """
        Generate recommendations based on evaluation results.
        
        Args:
            section_scores: Scores for each section
            section_feedback: Feedback for each section
            section_quality: Quality level for each section
            
        Returns:
            List[str]: List of recommendations
        """
        recommendations = []
        
        # Add general recommendation
        recommendations.append(
            "Ensure model documentation complies with EU AI Act Articles 11, 12, and 53 requirements."
        )
        
        # Add recommendations for missing or incomplete sections
        for section_id, score in section_scores.items():
            section_info = self.REQUIRED_SECTIONS[section_id]
            
            if score == 0.0:
                recommendations.append(
                    f"Add the missing '{section_info['name']}' section to comply with {section_info['eu_ai_act_reference']}."
                )
            elif score < 0.7:
                recommendations.append(
                    f"Improve the '{section_info['name']}' section to better comply with {section_info['eu_ai_act_reference']}."
                )
                
                # Add specific feedback for the section
                for feedback_item in section_feedback.get(section_id, []):
                    recommendations.append(f"  - {feedback_item}")
        
        # Add recommendation for documentation completeness
        recommendations.append(
            "Use the HuggingFace Model Card format to ensure comprehensive documentation."
        )
        
        return recommendations 