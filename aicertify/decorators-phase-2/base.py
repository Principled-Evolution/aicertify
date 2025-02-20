from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar
from ..models.evaluation_models import BehaviorEvaluation, SystemInteraction

F = TypeVar('F', bound=Callable[..., Any])

class BaseMonitor(ABC):
    """Abstract base class for framework-specific monitors"""
    
    @abstractmethod
    async def capture_interaction(self, interaction: SystemInteraction) -> None:
        """Capture a single interaction"""
        pass
    
    @abstractmethod
    async def store_evaluation(self, evaluation: BehaviorEvaluation) -> None:
        """Store complete evaluation"""
        pass

class BaseDecorator(ABC):
    """Abstract base class for framework-specific decorators"""
    
    @abstractmethod
    def monitor_system(self, *args, **kwargs) -> Callable[[F], F]:
        """Decorator for monitoring complete system behavior"""
        pass
    
    @abstractmethod
    def monitor_call(self, *args, **kwargs) -> Callable[[F], F]:
        """Decorator for monitoring individual calls"""
        pass 