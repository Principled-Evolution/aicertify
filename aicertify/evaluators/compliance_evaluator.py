"""
AICertify Compliance Evaluator

This module provides the ComplianceEvaluator class that combines multiple evaluators
to perform comprehensive compliance evaluations.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple, Set
import importlib.util

from aicertify.evaluators.base_evaluator import BaseEvaluator, EvaluationResult, Report
from aicertify.evaluators.fairness_evaluator import FairnessEvaluator
from aicertify.evaluators.content_safety_evaluator import ContentSafetyEvaluator
from aicertify.evaluators.risk_management_evaluator import RiskManagementEvaluator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class EvaluatorConfig:
    """Configuration container for evaluators."""
    
    def __init__(self, **kwargs):
        """Initialize configuration with optional evaluator-specific configs."""
        self.fairness = kwargs.get("fairness", {})
        self.content_safety = kwargs.get("content_safety", {})
        self.risk_management = kwargs.get("risk_management", {})
        self.general = kwargs.get("general", {})

class ComplianceEvaluator:
    """
    Main evaluator that combines multiple specialized evaluators.
    
    This class orchestrates the evaluation process across multiple domains:
    1. Fairness (via LangFair)
    2. Content Safety (via DeepEval)
    3. Risk Management
    
    It provides a unified interface for comprehensive compliance evaluation.
    """
    
    def __init__(
        self,
        evaluators: Optional[List[str]] = None,
        config: Optional[EvaluatorConfig] = None
    ):
        """
        Initialize the compliance evaluator with selected evaluators.
        
        Args:
            evaluators: List of evaluator names to use, or None for all available
            config: Configuration for the evaluators
        """
        self.config = config or EvaluatorConfig()
        self.all_evaluators = {
            "fairness": FairnessEvaluator(config=self.config.fairness),
            "content_safety": ContentSafetyEvaluator(config=self.config.content_safety),
            "risk_management": RiskManagementEvaluator(config=self.config.risk_management)
        }
        
        # Select which evaluators to use
        if evaluators is None:
            # Use all available evaluators
            self.active_evaluators = self.all_evaluators
        else:
            # Use only the specified evaluators
            self.active_evaluators = {
                name: evaluator for name, evaluator in self.all_evaluators.items()
                if name in evaluators
            }
        
        logger.info(f"Compliance evaluator initialized with {len(self.active_evaluators)} active evaluators")
        
    def evaluate(self, data: Dict) -> Dict[str, EvaluationResult]:
        """
        Evaluate compliance using all active evaluators.
        
        Args:
            data: Dictionary containing the contract data to evaluate
                Should include 'interactions' with a list of input/output pairs
                
        Returns:
            Dictionary mapping evaluator names to EvaluationResult objects
        """
        results = {}
        
        for name, evaluator in self.active_evaluators.items():
            logger.info(f"Running {name} evaluator")
            try:
                result = evaluator.evaluate(data)
                results[name] = result
                logger.info(f"{name} evaluation complete: compliant={result.compliant}, score={result.score:.2f}")
            except Exception as e:
                logger.error(f"Error in {name} evaluator: {str(e)}")
                # Create an error result
                results[name] = EvaluationResult(
                    evaluator_name=name.replace("_", " ").title() + " Evaluator",
                    compliant=False,
                    score=0.0,
                    threshold=0.7,  # Default threshold
                    reason=f"Evaluation error: {str(e)}",
                    details={"error": str(e)}
                )
        
        return results
    
    async def evaluate_async(self, data: Dict) -> Dict[str, EvaluationResult]:
        """
        Asynchronously evaluate compliance using all active evaluators.
        
        Args:
            data: Dictionary containing the contract data to evaluate
                
        Returns:
            Dictionary mapping evaluator names to EvaluationResult objects
        """
        results = {}
        tasks = []
        
        # Create tasks for all evaluators
        for name, evaluator in self.active_evaluators.items():
            tasks.append(self._run_evaluator_async(name, evaluator, data))
        
        # Run all evaluators concurrently
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for name, result in completed_results:
            results[name] = result
        
        return results
    
    async def _run_evaluator_async(
        self, name: str, evaluator: BaseEvaluator, data: Dict
    ) -> Tuple[str, EvaluationResult]:
        """
        Run an evaluator asynchronously and handle exceptions.
        
        Args:
            name: Name of the evaluator
            evaluator: Evaluator instance
            data: Data to evaluate
            
        Returns:
            Tuple of (evaluator_name, evaluation_result)
        """
        logger.info(f"Running {name} evaluator asynchronously")
        try:
            result = await evaluator.evaluate_async(data)
            logger.info(f"{name} evaluation complete: compliant={result.compliant}, score={result.score:.2f}")
            return name, result
        except Exception as e:
            logger.error(f"Error in {name} evaluator: {str(e)}")
            # Create an error result
            error_result = EvaluationResult(
                evaluator_name=name.replace("_", " ").title() + " Evaluator",
                compliant=False,
                score=0.0,
                threshold=0.7,  # Default threshold
                reason=f"Evaluation error: {str(e)}",
                details={"error": str(e)}
            )
            return name, error_result
    
    def is_compliant(self, results: Dict[str, EvaluationResult]) -> bool:
        """
        Determine overall compliance based on individual evaluator results.
        
        Args:
            results: Dictionary mapping evaluator names to EvaluationResult objects
            
        Returns:
            Boolean indicating overall compliance
        """
        if not results:
            return False
        
        # Check if all evaluators report compliance
        return all(result.compliant for result in results.values())
    
    def generate_report(
        self, 
        results: Dict[str, EvaluationResult],
        format: str = "markdown"
    ) -> Report:
        """
        Generate a comprehensive compliance report.
        
        Args:
            results: Dictionary mapping evaluator names to EvaluationResult objects
            format: Output format (json, markdown, pdf)
            
        Returns:
            Report object containing formatted report
        """
        if format == "json":
            import json
            content = json.dumps({
                name: result.dict() for name, result in results.items()
            }, indent=2)
        elif format == "markdown":
            content = self._generate_markdown_report(results)
        elif format == "pdf":
            content = self._generate_pdf_report(results)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return Report(content=content, format=format)
    
    def _generate_markdown_report(self, results: Dict[str, EvaluationResult]) -> str:
        """Generate a markdown format report."""
        overall_compliant = self.is_compliant(results)
        
        lines = [
            "# AI Compliance Evaluation Report",
            "",
            f"## Overall Compliance: {'PASS' if overall_compliant else 'FAIL'}",
            "",
            "| Evaluator | Compliance | Score | Threshold |",
            "|-----------|------------|-------|-----------|"
        ]
        
        for name, result in results.items():
            compliant_text = "✅ PASS" if result.compliant else "❌ FAIL"
            lines.append(
                f"| {result.evaluator_name} | {compliant_text} | {result.score:.2f} | {result.threshold:.2f} |"
            )
        
        lines.extend(["", "## Detailed Results", ""])
        
        for name, result in results.items():
            lines.extend([
                f"### {result.evaluator_name}",
                "",
                f"**Compliance:** {'PASS' if result.compliant else 'FAIL'}",
                f"**Score:** {result.score:.2f} (Threshold: {result.threshold:.2f})",
                f"**Reason:** {result.reason}",
                "",
                "#### Details",
                "```json",
                json.dumps(result.details, indent=2),
                "```",
                ""
            ])
        
        return "\n".join(lines)
    
    def _generate_pdf_report(self, results: Dict[str, EvaluationResult]) -> str:
        """Generate a PDF format report."""
        # This is a placeholder for PDF generation
        # In a real implementation, this would create a PDF and return its content
        return f"PDF Report containing evaluation results for {len(results)} evaluators" 