"""
AICertify Prohibited Practices Evaluators

This package provides evaluators for detecting prohibited practices as defined in the EU AI Act.
"""

from aicertify.evaluators.prohibited_practices.manipulation_evaluator import ManipulationEvaluator
from aicertify.evaluators.prohibited_practices.vulnerability_exploitation_evaluator import VulnerabilityExploitationEvaluator
from aicertify.evaluators.prohibited_practices.social_scoring_evaluator import SocialScoringEvaluator
from aicertify.evaluators.prohibited_practices.emotion_recognition_evaluator import EmotionRecognitionEvaluator

__all__ = [
    'ManipulationEvaluator',
    'VulnerabilityExploitationEvaluator',
    'SocialScoringEvaluator',
    'EmotionRecognitionEvaluator',
] 