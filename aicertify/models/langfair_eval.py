from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class AutoEvalInput(BaseModel):
    """Input data structure for LangFair AutoEval"""
    prompts: List[str] = Field(
        description="List of input prompts used to generate responses"
    )
    responses: List[str] = Field(
        description="List of AI-generated responses to evaluate"
    )

class ToxicityMetrics(BaseModel):
    """Toxicity evaluation metrics"""
    toxic_fraction: float = Field(default=0.0, description="Fraction of toxic responses")
    max_toxicity: float = Field(default=0.0, description="Maximum toxicity score")
    toxicity_probability: float = Field(default=0.0, description="Probability of toxic responses")
    detailed_scores: Optional[List[Dict[str, float]]] = Field(
        default_factory=list,
        description="Detailed toxicity scores per response"
    )

class StereotypeMetrics(BaseModel):
    """Stereotype evaluation metrics"""
    stereotype_scores: List[Dict[str, float]] = Field(
        default_factory=list,
        description="Stereotype scores per response"
    )
    gender_bias_detected: bool = Field(default=False, description="Whether gender bias was detected")
    racial_bias_detected: bool = Field(default=False, description="Whether racial bias was detected")

class CounterfactualMetrics(BaseModel):
    """Counterfactual evaluation metrics"""
    sentiment_bias: Optional[float] = Field(default=None, description="Average sentiment bias score")
    detailed_analysis: Optional[Dict[str, Any]] = Field(default=None, description="Detailed counterfactual analysis")

class FairnessMetrics(BaseModel):
    """Combined fairness metrics from evaluation"""
    ftu_satisfied: bool = Field(description="Whether Fairness Through Unawareness is satisfied")
    race_words_count: int = Field(default=0, description="Count of race-related words")
    gender_words_count: int = Field(default=0, description="Count of gender-related words")
    toxicity: ToxicityMetrics = Field(default_factory=ToxicityMetrics)
    stereotype: StereotypeMetrics = Field(default_factory=StereotypeMetrics)
    counterfactual: Optional[CounterfactualMetrics] = Field(default=None)

class AutoEvalResult(BaseModel):
    """Complete results from LangFair AutoEval"""
    metrics: FairnessMetrics = Field(description="Computed fairness metrics")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw evaluation data")
    summary: Optional[str] = Field(default=None, description="GPT-generated analysis summary") 