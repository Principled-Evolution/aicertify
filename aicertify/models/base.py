"""
Base models and utilities for AICertify.

This module contains common base classes and utilities used across
all model definitions in the AICertify system.
"""

from typing import Any, Dict, Optional, NamedTuple, Type
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)


class ValidationResult(NamedTuple):
    """Result of a model validation operation."""

    is_valid: bool
    error_message: Optional[str] = None
    model_instance: Optional[BaseModel] = None


def validate_model_data(
    data: Dict[str, Any], model_class: Type[BaseModel], log_full_exception: bool = False
) -> ValidationResult:
    """
    Validate data against a Pydantic model class (Pydantic v2 API).

    This function attempts to create a model instance from raw data,
    which is useful for validating external inputs before using them.

    Args:
        data: Dictionary containing data to validate
        model_class: Pydantic model class to validate against
        log_full_exception: Whether to log the full exception traceback (default: False)

    Returns:
        ValidationResult containing validation status, error message (if any),
        and the validated model instance (if successful)
    """
    try:
        # Create and validate a model instance from the data
        instance = model_class.model_validate(data)
        return ValidationResult(is_valid=True, model_instance=instance)
    except ValidationError as e:
        error_msg = str(e)
        context = f"Validating data against {model_class.__name__}"

        if log_full_exception:
            logger.exception(f"Model validation failed: {context} - {error_msg}")
        else:
            logger.error(f"Model validation failed: {context} - {error_msg}")

        return ValidationResult(is_valid=False, error_message=error_msg)
