from typing import Dict, List, Optional, Any, Iterator, TypeVar, Mapping, Union
from pydantic import BaseModel, RootModel
from collections.abc import MutableMapping

T = TypeVar('T')

class PolicyParameter(BaseModel):
    """
    Model for a single policy parameter with name and optional default value.
    
    This model is used to define parameters that OPA policies expect,
    including their default values if not provided by the caller.
    """
    name: str
    default_value: Optional[Any] = None

class PolicyParameters(RootModel[Dict[str, Any]], MutableMapping[str, Any]):
    """
    Model for policy parameters that will be included in OPA input.
    
    This class combines Pydantic's validation with a complete dictionary
    interface by implementing MutableMapping. It now uses RootModel to wrap
    a dictionary of parameters, in accordance with Pydantic v2.
    """
    def __getitem__(self, key: str) -> Any:
        """
        Get a parameter value by key, raising KeyError if not found.
        
        Args:
            key: The parameter name
            
        Returns:
            The parameter value
            
        Raises:
            KeyError: If the parameter does not exist
        """
        return self.__root__[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set a parameter value.
        
        Args:
            key: The parameter name
            value: The parameter value to set
        """
        self.__root__[key] = value
    
    def __delitem__(self, key: str) -> None:
        """
        Delete a parameter by key.
        
        Args:
            key: The parameter name to delete
            
        Raises:
            KeyError: If the parameter does not exist
        """
        del self.__root__[key]
    
    def __iter__(self) -> Iterator[str]:
        """
        Get an iterator over parameter names.
        
        Returns:
            Iterator over parameter names (keys)
        """
        return iter(self.__root__)
    
    def __len__(self) -> int:
        """
        Get the number of parameters.
        
        Returns:
            Number of parameters in the collection
        """
        return len(self.__root__)
    
    def __contains__(self, key: object) -> bool:
        """
        Check if a parameter exists.
        
        Args:
            key: The parameter name to check
            
        Returns:
            True if the parameter exists, False otherwise
        """
        return key in self.__root__
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a parameter value with a default if not found.
        
        Args:
            key: The parameter name
            default: Value to return if the key is not found
            
        Returns:
            The parameter value or default if not found
        """
        return self.__root__.get(key, default)
    
    def update(self, other: Union[Mapping[str, Any], 'PolicyParameters', Dict[str, Any]]) -> None:
        """
        Update parameters with values from another mapping.
        
        Args:
            other: Another mapping or PolicyParameters object to update from
        """
        if isinstance(other, PolicyParameters):
            self.__root__.update(other.__root__)
        else:
            self.__root__.update(other)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert parameters to a plain dictionary.
        
        This is a convenience method equivalent to Pydantic's dict() but
        directly returns the __root__ dictionary for simpler use.
        
        Returns:
            Dictionary of parameter names to values
        """
        return self.__root__
    
    @classmethod
    def from_dict(cls, params: Dict[str, Any]) -> 'PolicyParameters':
        """
        Create a PolicyParameters instance from a dictionary.
        
        Args:
            params: Dictionary of parameter names to values
            
        Returns:
            New PolicyParameters instance with the provided parameters
        """
        return cls(__root__=params)
