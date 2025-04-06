"""
Evaluator Registry Module

This module implements a registry for evaluators in AICertify, mapping metric names 
to the evaluator classes that can produce them. It provides functions to register
evaluators with the metrics they produce and to discover which evaluators are needed
to provide a set of required metrics.

The registry design helps maintain a loosely coupled architecture where:
1. Policy files can declare required metrics without needing to know which 
   specific evaluators will provide them
2. The system can dynamically determine which evaluators to run based on policy requirements

Usage:
    # Register an evaluator for specific metrics
    register_evaluator_for_metrics(FairnessEvaluator, ["fairness.score", "gender_bias_detected"])
    
    # Discover evaluators needed for a set of metrics
    required_metrics = {"fairness.score", "toxicity.score"}
    evaluator_classes = discover_evaluators_for_metrics(required_metrics)
    
    # Initialize the registry with all available evaluators
    initialize_evaluator_registry()
"""

from typing import Dict, List, Set, Type
import logging
import threading
from collections import defaultdict
from aicertify.evaluators.base_evaluator import BaseEvaluator

logger = logging.getLogger(__name__)

# Lock for thread-safe registry operations
_registry_lock = threading.RLock()

# Flag to track if the registry has been initialized
_registry_initialized = False

# Default registry instance
_default_registry = None

# For backwards compatibility, maintain the global dict
# but use the registry internally 
METRIC_EVALUATOR_MAP: Dict[str, Type[BaseEvaluator]] = {}

class EvaluatorRegistry:
    """
    Registry for evaluators that map metric names to evaluator classes.
    
    This class maintains a registry of evaluators and the metrics they produce,
    allowing dynamic discovery of which evaluators are needed for a given set
    of metrics.
    """
    
    # Singleton instance
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        """Ensure only one instance of the registry exists."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EvaluatorRegistry, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialize a new registry."""
        # Only initialize once
        with self.__class__._lock:
            if not hasattr(self, '_initialized') or not self._initialized:
                # Map from metric name to set of evaluator classes
                self._metric_evaluator_map: Dict[str, Set[Type[BaseEvaluator]]] = defaultdict(set)
                # Track registered evaluators to avoid duplicates
                self._registered_evaluators: Set[Type[BaseEvaluator]] = set()
                self._initialized = True
    
    def register_evaluator(self, evaluator_class: Type[BaseEvaluator], metrics: List[str]) -> None:
        """
        Register an evaluator for specific metrics.
        
        Args:
            evaluator_class: The evaluator class to register
            metrics: List of metric names this evaluator can produce
        """
        with _registry_lock:
            # Check if this evaluator is already registered for these metrics
            already_registered = True
            for metric in metrics:
                if evaluator_class not in self._metric_evaluator_map.get(metric, set()):
                    already_registered = False
                    break
                    
            if already_registered:
                logger.debug(f"Evaluator {evaluator_class.__name__} already registered for these metrics, skipping")
                return
                
            # Add to registered evaluators set
            self._registered_evaluators.add(evaluator_class)
            
            # Register for each metric
            for metric in metrics:
                self._metric_evaluator_map[metric].add(evaluator_class)
                
                # Log if this is overriding an existing registration from a different class
                if len(self._metric_evaluator_map[metric]) > 1:
                    logger.debug(f"Multiple evaluators registered for metric '{metric}': {self._metric_evaluator_map[metric]}")
    
    def discover_evaluators(self, metrics: List[str]) -> List[Type[BaseEvaluator]]:
        """
        Discover evaluators that support the given metrics.
        
        Args:
            metrics: List of metrics to discover evaluators for.
            
        Returns:
            List of evaluator classes that support the given metrics.
        """
        logger.info(f"Discovering evaluators for metrics: {metrics}")
        
        if not metrics:
            logger.warning("No metrics provided to discover_evaluators")
            return []
            
        evaluators = set()
        
        # For debugging, log all registered evaluators and their supported metrics
        for evaluator_class in self._registered_evaluators:
            if hasattr(evaluator_class, 'get_supported_metrics'):
                supported = evaluator_class.get_supported_metrics()
                logger.info(f"Evaluator {evaluator_class.__name__} supports metrics: {supported}")
            elif hasattr(evaluator_class, 'SUPPORTED_METRICS'):
                supported = evaluator_class.SUPPORTED_METRICS
                logger.info(f"Evaluator {evaluator_class.__name__} has SUPPORTED_METRICS: {supported}")
            else:
                logger.warning(f"Evaluator {evaluator_class.__name__} does not define supported metrics")
        
        # Find evaluators that support the requested metrics
        for metric in metrics:
            metric_evaluators = self.get_evaluators_for_metric(metric)
            
            if metric_evaluators:
                logger.info(f"Found {len(metric_evaluators)} evaluators for metric '{metric}': {[e.__name__ for e in metric_evaluators]}")
                evaluators.update(metric_evaluators)
            else:
                logger.warning(f"No evaluators found for metric '{metric}'")
                
        # Log the final discovered evaluators
        evaluator_names = [e.__name__ for e in evaluators]
        logger.info(f"Discovered {len(evaluators)} evaluators: {evaluator_names}")
                
        return list(evaluators)
    
    def get_evaluators_for_metric(self, metric: str) -> Set[Type[BaseEvaluator]]:
        """
        Get evaluators that can produce a specific metric.
        
        Args:
            metric: The metric name
            
        Returns:
            Set of evaluator classes that can produce the metric
        """
        logger.info(f"Looking for evaluators that support metric: '{metric}'")
        
        with _registry_lock:
            if metric in self._metric_evaluator_map:
                evaluators = self._metric_evaluator_map[metric]
                if evaluators:
                    logger.info(f"Found {len(evaluators)} evaluators for metric '{metric}': {[e.__name__ for e in evaluators]}")
                    return evaluators
            
            logger.warning(f"No evaluators found for metric '{metric}' in registry")
            # Check if there's a case mismatch
            lower_metric = metric.lower()
            for key in self._metric_evaluator_map:
                if key.lower() == lower_metric:
                    evaluators = self._metric_evaluator_map[key]
                    logger.info(f"Found case-insensitive match for metric '{metric}' -> '{key}': {[e.__name__ for e in evaluators]}")
                    return evaluators
            
            # Deep scan of all registered evaluators to find any that might support this metric
            for evaluator_class in self._registered_evaluators:
                supported_metrics = []
                if hasattr(evaluator_class, 'get_supported_metrics'):
                    supported_metrics = evaluator_class.get_supported_metrics()
                elif hasattr(evaluator_class, 'SUPPORTED_METRICS'):
                    supported_metrics = evaluator_class.SUPPORTED_METRICS
                
                if metric in supported_metrics:
                    logger.info(f"Found evaluator {evaluator_class.__name__} supporting metric '{metric}' through deep scan")
                    return {evaluator_class}
            
            logger.warning(f"No evaluators found for metric '{metric}' after deep scan")
            return set()
    
    def get_metrics_for_evaluator(self, evaluator_class: Type[BaseEvaluator]) -> Set[str]:
        """
        Get all metrics that can be produced by a specific evaluator class.
        
        Args:
            evaluator_class: The evaluator class to look up
            
        Returns:
            Set of metric names that can be produced by the evaluator
        """
        with _registry_lock:
            metrics = set()
            for metric, evaluators in self._metric_evaluator_map.items():
                if evaluator_class in evaluators:
                    metrics.add(metric)
            return metrics
    
    def clear(self) -> None:
        """Clear all registrations from the registry."""
        with _registry_lock:
            self._metric_evaluator_map.clear()
            self._registered_evaluators.clear()
            
    def get_all_metrics(self) -> Set[str]:
        """
        Get all registered metric names.
        
        Returns:
            Set of all metric names in the registry
        """
        with _registry_lock:
            return set(self._metric_evaluator_map.keys())
            
    def get_all_evaluators(self) -> Set[Type[BaseEvaluator]]:
        """
        Get all registered evaluator classes.
        
        Returns:
            Set of all evaluator classes in the registry
        """
        with _registry_lock:
            return self._registered_evaluators.copy()
            
    def get_metrics_count(self) -> int:
        """
        Get the number of registered metrics.
        
        Returns:
            Number of metrics in the registry
        """
        with _registry_lock:
            return len(self._metric_evaluator_map)
            
    def get_evaluators_count(self) -> int:
        """
        Get the number of registered evaluator classes.
        
        Returns:
            Number of unique evaluator classes in the registry
        """
        with _registry_lock:
            return len(self._registered_evaluators)

    def is_evaluator_registered(self, evaluator_class: Type[BaseEvaluator]) -> bool:
        """
        Check if an evaluator class is already registered.
        
        Args:
            evaluator_class: The evaluator class to check
            
        Returns:
            True if the evaluator is registered, False otherwise
        """
        with _registry_lock:
            return evaluator_class in self._registered_evaluators

def register_evaluator_for_metrics(evaluator_class: Type[BaseEvaluator], metrics: List[str]) -> None:
    """
    Register an evaluator class for specific metrics.
    
    Args:
        evaluator_class: The evaluator class to register
        metrics: List of metric names this evaluator can produce
    """
    registry = get_default_registry()
    
    # Check if already registered to avoid duplicate registrations
    if registry.is_evaluator_registered(evaluator_class):
        # Update the global dict for backwards compatibility
        for metric in metrics:
            METRIC_EVALUATOR_MAP[metric] = evaluator_class
        return
        
    # Register with the registry
    registry.register_evaluator(evaluator_class, metrics)
    
    # For backwards compatibility, also update the global dict
    for metric in metrics:
        METRIC_EVALUATOR_MAP[metric] = evaluator_class

def discover_evaluators_for_metrics(required_metrics: Set[str]) -> Set[Type[BaseEvaluator]]:
    """
    Discover evaluators needed to produce the required metrics.
    
    Args:
        required_metrics: Set of metric names required by policies
        
    Returns:
        Set of evaluator classes that can produce the required metrics
    """
    return get_default_registry().discover_evaluators(list(required_metrics))

def get_default_registry() -> EvaluatorRegistry:
    """
    Get the default evaluator registry instance.
    
    Returns:
        The default EvaluatorRegistry instance
    """
    global _default_registry
    if _default_registry is None:
        _default_registry = EvaluatorRegistry()
    return _default_registry

def initialize_evaluator_registry() -> None:
    """
    Initialize the evaluator registry by discovering and registering all available evaluators.
    
    This function:
    1. Discovers all evaluator classes that inherit from BaseEvaluator
    2. Determines the metrics each evaluator supports via:
       - SUPPORTED_METRICS class attribute (must be a list or tuple)
       - get_supported_metrics() instance method (must return a list or tuple)
    3. Registers each evaluator with the metrics it supports
    
    Note: Evaluator classes must be defined in modules directly under the
    aicertify.evaluators package.
    """
    global _registry_initialized
    
    # Use a lock to ensure thread safety
    with _registry_lock:
        # Check if the registry has already been initialized
        if _registry_initialized:
            logger.debug("Evaluator registry already initialized, skipping")
            return
            
        # Add stack trace logging to identify where this is being called from
        import traceback
        stack = traceback.extract_stack()
        caller = stack[-2]  # The caller of this function
        logger.debug(f"initialize_evaluator_registry called from {caller.filename}:{caller.lineno}")
        
        # Get the default registry instance
        registry = get_default_registry()
        
        # Set the flag to prevent multiple initializations
        _registry_initialized = True
        
        # Import required modules
        from aicertify.evaluators import base_evaluator
        from importlib import import_module
        import inspect
        import pkgutil
        
        def discover_evaluator_classes() -> List[Type[base_evaluator.BaseEvaluator]]:
            """
            Discover all evaluator classes that inherit from BaseEvaluator.
            
            Returns:
                List of evaluator classes
            """
            evaluator_classes = []
            
            # Import the evaluators package
            try:
                evaluators_pkg = import_module('aicertify.evaluators')
                pkg_path = evaluators_pkg.__path__
            except (ImportError, AttributeError) as e:
                logger.exception(f"Failed to import evaluators package: {e}")
                return []
            
            # Discover all modules in the evaluators package
            for _, module_name, is_pkg in pkgutil.iter_modules(pkg_path):
                # Skip __init__ and base modules
                if module_name in ['__init__', 'base_evaluator', 'evaluator_registry']:
                    continue
                    
                try:
                    # Import the module
                    module = import_module(f'aicertify.evaluators.{module_name}')
                    
                    # Find all classes in the module that inherit from BaseEvaluator
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, base_evaluator.BaseEvaluator) and 
                            obj is not base_evaluator.BaseEvaluator):
                            evaluator_classes.append(obj)
                            logger.debug(f"Found evaluator class: {obj.__name__} in module {module_name}")
                except Exception as e:
                    logger.exception(f"Error loading evaluator module {module_name}: {e}")
            
            return evaluator_classes
        
        def register_evaluator(evaluator_class: Type[base_evaluator.BaseEvaluator]) -> bool:
            """
            Register an evaluator class with its supported metrics.
            
            Args:
                evaluator_class: The evaluator class to register
                
            Returns:
                True if registration succeeded, False otherwise
            """
            # Check if already registered to avoid duplicate work
            if registry.is_evaluator_registered(evaluator_class):
                logger.debug(f"Evaluator {evaluator_class.__name__} already registered, skipping")
                return True
                
            # Log the module where this evaluator is defined
            module_name = evaluator_class.__module__
            logger.debug(f"Registering evaluator {evaluator_class.__name__} from module {module_name}")
            
            try:
                # Try to get the metrics directly from a class attribute
                if hasattr(evaluator_class, 'SUPPORTED_METRICS'):
                    metrics = evaluator_class.SUPPORTED_METRICS
                    if isinstance(metrics, (list, tuple)):
                        metrics_list = list(metrics)
                        register_evaluator_for_metrics(evaluator_class, metrics_list)
                        logger.info(f"Registered {evaluator_class.__name__} for metrics: {metrics_list}")
                        return True
                    else:
                        logger.warning(
                            f"SUPPORTED_METRICS for {evaluator_class.__name__} is not a list or tuple. "
                            f"Type: {type(metrics)}"
                        )
                        
                # If no SUPPORTED_METRICS attribute or it's not iterable, try to instantiate the evaluator
                evaluator = evaluator_class()
                if hasattr(evaluator, 'get_supported_metrics'):
                    metrics = evaluator.get_supported_metrics()
                    if isinstance(metrics, (list, tuple)):
                        metrics_list = list(metrics)
                        register_evaluator_for_metrics(evaluator_class, metrics_list)
                        logger.info(f"Registered {evaluator_class.__name__} for metrics: {metrics_list}")
                        return True
                    else:
                        logger.warning(
                            f"get_supported_metrics() for {evaluator_class.__name__} did not return a list or tuple. "
                            f"Type: {type(metrics)}"
                        )
                else:
                    logger.warning(
                        f"Evaluator {evaluator_class.__name__} does not define SUPPORTED_METRICS "
                        f"or get_supported_metrics()"
                    )
                    
            except Exception as e:
                logger.exception(f"Error registering evaluator {evaluator_class.__name__}: {e}")
            
            return False
        
        # Discover and register evaluator classes
        evaluator_classes = discover_evaluator_classes()
        logger.info(f"Discovered {len(evaluator_classes)} evaluator classes")
        
        # Count successful registrations
        sum(1 for evaluator_class in evaluator_classes if register_evaluator(evaluator_class))
        
        # Log the number of evaluators and metrics registered
        evaluator_count = registry.get_evaluators_count()
        metric_count = registry.get_metrics_count()
        logger.info(f"Initialized evaluator registry with {evaluator_count} evaluators for {metric_count} metrics")
        
        if metric_count > 0:
            logger.info(f"Registered metrics: {', '.join(sorted(registry.get_all_metrics()))}")
        else:
            logger.warning("No metrics were registered in the evaluator registry")
