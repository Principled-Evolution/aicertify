from functools import wraps

from ...models.evaluation_models import (
    SystemType
)
from ..base import BaseDecorator

class LangChainMonitor(BaseDecorator):
    """LangChain-specific monitoring decorators"""
    
    @staticmethod
    def monitor_agent(
        system_name: str,
        system_type: SystemType = SystemType.AI,
        capture_media: bool = True
    ):
        """Monitor LangChain agent behavior"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # LangChain-specific implementation...
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def monitor_llm(operation_name: str):
        """Monitor LangChain LLM calls"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # LangChain-specific implementation...
                return await func(*args, **kwargs)
            return wrapper
        return decorator 