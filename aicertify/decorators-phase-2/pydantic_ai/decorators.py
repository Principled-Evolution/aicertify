from functools import wraps

from ...models.evaluation_models import (
    SystemType
)
from ..base import BaseDecorator

class PydanticAIMonitor(BaseDecorator):
    """PydanticAI-specific monitoring decorators"""
    
    @staticmethod
    def monitor_agent(
        system_name: str,
        system_type: SystemType = SystemType.AI,
        capture_media: bool = True
    ):
        """Monitor PydanticAI agent behavior"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Implementation as before...
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def monitor_llm(operation_name: str):
        """Monitor PydanticAI LLM calls"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Implementation as before...
                return await func(*args, **kwargs)
            return wrapper
        return decorator 