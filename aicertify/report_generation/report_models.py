from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

class MetricValue(BaseModel):
    """Base model for metric values that can be of different types"""
    name: str
    value: Union[str, bool, float, int, Dict[str, Any]]
    display_name: str = Field(..., description="Human readable name for the metric")
    
class MetricGroup(BaseModel):
    """Group of related metrics"""
    name: str
    display_name: str
    metrics: List[MetricValue]
    description: Optional[str] = None

class PolicyResult(BaseModel):
    """Result of a policy evaluation"""
    name: str
    result: bool
    details: Optional[Dict[str, Any]] = None

class ApplicationDetails(BaseModel):
    """Basic details about the application being evaluated"""
    name: str
    evaluation_mode: str
    contract_count: int
    evaluation_date: datetime = Field(default_factory=datetime.now)

class EvaluationReport(BaseModel):
    """Main report model containing all evaluation data"""
    app_details: ApplicationDetails
    metric_groups: List[MetricGroup]
    policy_results: List[PolicyResult]
    summary: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "app_details": {
                    "name": "TestApp",
                    "evaluation_mode": "Automatic",
                    "contract_count": 5,
                    "evaluation_date": "2024-03-20T10:00:00"
                },
                "metric_groups": [
                    {
                        "name": "fairness",
                        "display_name": "Fairness Metrics",
                        "metrics": [
                            {
                                "name": "ftu_satisfied",
                                "display_name": "FTU Satisfied",
                                "value": True
                            },
                            {
                                "name": "race_words_count",
                                "display_name": "Race Words Count",
                                "value": 0
                            }
                        ]
                    }
                ],
                "policy_results": [
                    {
                        "name": "eu_ai_act",
                        "result": True,
                        "details": {"specific_rule": "passed"}
                    }
                ],
                "summary": "All evaluation criteria met"
            }
        } 