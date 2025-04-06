"""
AICertify Base Evaluator Interface

This module defines the BaseEvaluator abstract class that all evaluators must implement.
It provides a standard interface for all evaluation components in the AICertify framework.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class EvaluationResult(BaseModel):
    """Model representing an evaluation result."""
    
    evaluator_name: str
    compliant: bool
    score: float
    threshold: Optional[float] = None
    reason: str
    details: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def to_json(self) -> Dict[str, Any]:
        """Convert the result to a JSON-serializable dictionary."""
        return {
            "evaluator_name": self.evaluator_name,
            "compliant": self.compliant,
            "score": self.score,
            "threshold": self.threshold,
            "reason": self.reason,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
    
    class Config:
        """Pydantic configuration."""
        
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class Report(BaseModel):
    """Model representing an evaluation report."""
    
    content: str
    format: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class EvaluatorConfig:
    """Configuration class for evaluators."""
    
    def __init__(self, config_dict: Optional[Dict] = None):
        """
        Initialize the configuration with a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration parameters
        """
        self._config = config_dict or {}
        
    def get(self, key, default=None):
        """
        Get a configuration value by key.
        
        Args:
            key: The configuration key to retrieve
            default: Default value to return if key is not found
            
        Returns:
            The configuration value or default if not found
        """
        return self._config.get(key, default)
    
    def __getattr__(self, name):
        """
        Allow attribute-style access to configuration values.
        
        Args:
            name: The attribute name to access
            
        Returns:
            The configuration value or None if not found
        """
        return self._config.get(name)

class BaseEvaluator(ABC):
    """Base abstract class for all compliance evaluators in AICertify."""
    
    SUPPORTED_METRICS = []  # Default empty list of supported metrics
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the evaluator with optional configuration.
        
        Args:
            config: Configuration dictionary controlling evaluator behavior
        """
        self.config = EvaluatorConfig(config or {})
        self.threshold = self.config.get("threshold", 0.7)
        self._initialize()
    
    @classmethod
    def get_supported_metrics(cls) -> List[str]:
        """
        Get the list of metrics supported by this evaluator.
        
        Returns:
            List of metric names supported by the evaluator
        """
        return cls.SUPPORTED_METRICS
    
    @abstractmethod
    def _initialize(self) -> None:
        """Initialize the evaluator with configuration parameters."""
        pass
        
    @abstractmethod
    def evaluate(self, data: Dict) -> EvaluationResult:
        """
        Evaluate compliance based on input data.
        
        Args:
            data: Dictionary containing the data to evaluate
            
        Returns:
            EvaluationResult object containing evaluation results
        """
        pass
    
    @abstractmethod
    async def evaluate_async(self, data: Dict) -> EvaluationResult:
        """
        Asynchronously evaluate compliance based on input data.
        
        Args:
            data: Dictionary containing the data to evaluate
            
        Returns:
            EvaluationResult object containing evaluation results
        """
        pass
    
    def generate_report(self, results: List[EvaluationResult], 
                        format: str = "json") -> Report:
        """
        Generate standardized compliance report.
        
        Args:
            results: List of EvaluationResult objects
            format: Output format (json, markdown, pdf)
            
        Returns:
            Report object containing formatted report
        """
        if format == "json":
            import json
            content = json.dumps([result.dict() for result in results], indent=2)
        elif format == "markdown":
            content = self._generate_markdown_report(results)
        elif format == "pdf":
            content = self._generate_pdf_report(results)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return Report(content=content, format=format)
    
    def _generate_markdown_report(self, results: List[EvaluationResult]) -> str:
        """Generate a markdown format report."""
        lines = ["# Compliance Evaluation Report", ""]
        
        for result in results:
            lines.extend([
                f"## {result.evaluator_name}",
                "",
                f"- **Compliant**: {'Yes' if result.compliant else 'No'}",
                f"- **Score**: {result.score:.2f} (Threshold: {result.threshold:.2f})",
                f"- **Reason**: {result.reason}",
                f"- **Timestamp**: {result.timestamp.isoformat()}",
                "",
                "### Details",
                "```json",
                json.dumps(result.details, indent=2),
                "```",
                ""
            ])
        
        return "\n".join(lines)
    
    def _generate_pdf_report(self, results: List[EvaluationResult]) -> str:
        """Generate a PDF format report."""
        # This is a placeholder for PDF generation
        # In a real implementation, this would create a PDF and return its content
        return f"PDF Report containing {len(results)} evaluation results" 