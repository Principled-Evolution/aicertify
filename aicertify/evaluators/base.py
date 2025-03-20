"""
Add required metric definitions to evaluator classes
"""
class BaseEvaluator:
    SUPPORTED_METRICS = []  # Default empty list
    
    @classmethod
    def get_supported_metrics(cls):
        return cls.SUPPORTED_METRICS 