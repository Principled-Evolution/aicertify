"""
Accuracy Evaluator for assessing hallucination and factual accuracy.

This evaluator implements checks for EU AI Act accuracy requirements,
which require AI systems to provide accurate information and avoid hallucinations.
"""

import logging
from typing import Dict, Any, List

from deepeval.metrics import HallucinationMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from aicertify.evaluators.base_evaluator import BaseEvaluator, EvaluationResult

logger = logging.getLogger(__name__)


class AccuracyEvaluator(BaseEvaluator):
    """
    Evaluator that assesses hallucination and factual accuracy.

    This evaluator uses deepeval's HallucinationMetric and FaithfulnessMetric
    to measure the extent of hallucination and factual accuracy in LLM outputs.

    These metrics are critical for EU AI Act compliance, which requires
    AI systems to provide accurate and factual information.
    """

    SUPPORTED_METRICS = ["accuracy.score", "accuracy.precision", "accuracy.recall"]

    def __init__(
        self,
        hallucination_threshold: float = 0.7,
        factual_consistency_threshold: float = 0.7,
        model: str = "gpt-4o-mini",
        **kwargs,
    ):
        """
        Initialize the AccuracyEvaluator.

        Args:
            hallucination_threshold: Threshold for hallucination detection (0.0-1.0)
            factual_consistency_threshold: Threshold for factual consistency (0.0-1.0)
            model: The LLM model to use for evaluation
            **kwargs: Additional configuration parameters
        """
        self.hallucination_threshold = hallucination_threshold
        self.factual_consistency_threshold = factual_consistency_threshold
        self.model = model
        super().__init__(kwargs)

    def _initialize(self) -> None:
        """Initialize the evaluator with deepeval metrics."""
        # Initialize the metrics
        self.hallucination_metric = HallucinationMetric(
            threshold=self.hallucination_threshold, model=self.model
        )
        self.faithfulness_metric = FaithfulnessMetric(
            threshold=self.factual_consistency_threshold, model=self.model
        )

    def evaluate(self, interaction: Dict[str, Any]) -> EvaluationResult:
        """
        Evaluate an interaction for hallucination and factual accuracy.

        Args:
            interaction: The interaction to evaluate

        Returns:
            EvaluationResult: The evaluation result
        """
        try:
            input_text = interaction.get("input_text", "")
            output_text = interaction.get("output_text", "")
            context = interaction.get("context", None)

            # Ensure context is either None or a list of strings
            if context is not None:
                if isinstance(context, str):
                    context = [context]
                elif not isinstance(context, list):
                    logger.warning("Invalid context format. Setting context to None.")
                    context = None
                elif not all(isinstance(item, str) for item in context):
                    logger.warning(
                        "Context must be a list of strings. Setting context to None."
                    )
                    context = None

            # If no context provided, use an empty list instead of None
            if context is None:
                logger.warning(
                    "No context provided for accuracy evaluation. Using empty list for context."
                )
                context = []  # Use empty list instead of None

            # Create test case for evaluation
            test_case = LLMTestCase(
                input=input_text, actual_output=output_text, context=context
            )

            # Evaluate hallucination
            self.hallucination_metric.measure(test_case)
            hallucination_score = self.hallucination_metric.score
            hallucination_reason = self.hallucination_metric.reason

            # Evaluate factual consistency
            self.faithfulness_metric.measure(test_case)
            factual_consistency_score = self.faithfulness_metric.score
            factual_consistency_reason = self.faithfulness_metric.reason

            # Determine if the output contains hallucinations
            has_hallucination = hallucination_score < self.hallucination_threshold

            # Determine if the output is factually consistent
            is_factually_consistent = (
                factual_consistency_score >= self.factual_consistency_threshold
            )

            # Generate overall reason and recommendations
            reason = self._generate_reason(has_hallucination, is_factually_consistent)
            recommendations = self._generate_recommendations(
                has_hallucination,
                is_factually_consistent,
                hallucination_reason,
                factual_consistency_reason,
            )

            # Overall compliance is achieved only if both criteria are met
            compliant = not has_hallucination and is_factually_consistent

            # Create and return the evaluation result
            result = EvaluationResult(
                evaluator_name="AccuracyEvaluator",
                compliant=compliant,
                score=min(hallucination_score, factual_consistency_score),
                reason=reason,
                details={
                    "hallucination_score": hallucination_score,
                    "hallucination_reason": hallucination_reason,
                    "factual_consistency_score": factual_consistency_score,
                    "factual_consistency_reason": factual_consistency_reason,
                    "has_hallucination": has_hallucination,
                    "is_factually_consistent": is_factually_consistent,
                    "recommendations": recommendations,
                },
            )

            return result
        except Exception as e:
            logger.error(f"Error evaluating interaction: {e}")
            return EvaluationResult(
                evaluator_name="AccuracyEvaluator",
                compliant=False,
                score=0.0,
                reason="An error occurred while evaluating the interaction.",
                details={},
            )

    async def evaluate_async(self, interaction: Dict[str, Any]) -> EvaluationResult:
        """
        Asynchronously evaluate an interaction for hallucination and factual accuracy.

        Args:
            interaction: The interaction to evaluate

        Returns:
            EvaluationResult: The evaluation result
        """
        # For now, just call the synchronous method
        # In the future, this could be implemented to use async APIs if deepeval supports them
        return self.evaluate(interaction)

    def _generate_reason(
        self, has_hallucination: bool, is_factually_consistent: bool
    ) -> str:
        """Generate a human-readable reason for the compliance determination."""
        if not has_hallucination and is_factually_consistent:
            return "The output is factually accurate and contains no hallucinations."

        issues = []
        if has_hallucination:
            issues.append("contains hallucinations")
        if not is_factually_consistent:
            issues.append("is not factually consistent with the provided context")

        return f"The output {' and '.join(issues)}, which violates EU AI Act requirements for accuracy."

    def _generate_recommendations(
        self,
        has_hallucination: bool,
        is_factually_consistent: bool,
        hallucination_reason: str,
        factual_consistency_reason: str,
    ) -> List[str]:
        """Generate recommendations for improving the output."""
        recommendations = []

        if has_hallucination:
            recommendations.append(
                f"Address hallucinations in the output: {hallucination_reason}"
            )
            recommendations.append(
                "Implement stronger hallucination controls in your LLM integration"
            )

        if not is_factually_consistent:
            recommendations.append(
                f"Improve factual consistency: {factual_consistency_reason}"
            )
            recommendations.append(
                "Ensure the LLM is provided with comprehensive and accurate context"
            )

        if not recommendations:
            recommendations.append(
                "Continue to monitor outputs for factual accuracy and hallucinations"
            )

        return recommendations
