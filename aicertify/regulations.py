"""
AICertify Regulations Module

This module provides a simple interface for creating and managing regulation sets 
that applications can be evaluated against.
"""

import logging
from typing import Dict, List, Set

from aicertify.opa_core.policy_loader import PolicyLoader
from aicertify.opa_core.evaluator import OpaEvaluator

logger = logging.getLogger(__name__)

class RegulationSet:
    """
    A collection of regulations that an AI application can be evaluated against.
    
    This class allows users to select specific regulations to evaluate
    their applications against, and provides an interface for evaluating
    applications against these regulations.
    """
    
    def __init__(self, name: str = "default"):
        """
        Initialize a new regulation set.
        
        Args:
            name: Name of the regulation set
        """
        self.name = name
        self._policy_loader = PolicyLoader()
        self._opa_evaluator = OpaEvaluator(use_external_server=False)
        self._regulations: Set[str] = set()
        
        # Ensure policies are loaded
        self._opa_evaluator.load_policies()
        
        # Get available regulations
        self._available_regulations = self._get_available_regulations()
        logger.debug(f"Available regulations: {self._available_regulations}")
    
    def _get_available_regulations(self) -> Dict[str, str]:
        """
        Get all available regulations from the OPA policies directory.
        
        Returns:
            Dictionary mapping regulation names to their folder paths
        """
        available_regs = {}
        
        # Get all policy folders that contain policies
        for category in self._policy_loader.get_all_categories():
            # Skip 'global' category due to a folder topology issue
            # TODO: Fix this issue
            if isinstance(category, tuple) and category[0] == 'global':
                continue
            
            # Convert tuple to string path if needed
            category_path = '/'.join(filter(None, category)) if isinstance(category, tuple) else category
            # Skip empty categories
            if not self._policy_loader.get_policies_by_category(category_path):
                continue
                
            # Use the category name as the regulation name
            # Strip any path-like structure and use the last component
            reg_name = category_path.split('/')[-1]
            available_regs[reg_name] = category_path
            
        return available_regs
    
    def list_available(self) -> List[str]:
        """
        List all available regulations that can be added to this set.
        
        Returns:
            List of regulation names
        """
        return list(self._available_regulations.keys())
    
    def add(self, regulation_name: str) -> bool:
        """
        Add a regulation to this set.
        
        Args:
            regulation_name: Name of the regulation to add
            
        Returns:
            True if the regulation was added, False otherwise
            
        Raises:
            ValueError: If the regulation is not available
        """
        if regulation_name not in self._available_regulations:
            matching_folders = self._opa_evaluator.find_matching_policy_folders(regulation_name)
            if not matching_folders:
                raise ValueError(
                    f"Regulation '{regulation_name}' not found. Available regulations: {', '.join(self.list_available())}"
                )
            
            # Use the first matching folder
            self._regulations.add(matching_folders[0])
            logger.info(f"Added regulation '{regulation_name}' (using folder: {matching_folders[0]})")
            return True
        else:
            # Use the exact regulation name
            self._regulations.add(self._available_regulations[regulation_name])
            logger.info(f"Added regulation '{regulation_name}'")
            return True
    
    def remove(self, regulation_name: str) -> bool:
        """
        Remove a regulation from this set.
        
        Args:
            regulation_name: Name of the regulation to remove
            
        Returns:
            True if the regulation was removed, False otherwise
        """
        # Check if the regulation is in the set by folder path
        if regulation_name in self._available_regulations:
            folder_path = self._available_regulations[regulation_name]
            if folder_path in self._regulations:
                self._regulations.remove(folder_path)
                logger.info(f"Removed regulation '{regulation_name}'")
                return True
        
        # Check for partial matches in the set
        for reg in list(self._regulations):
            if reg.endswith(regulation_name):
                self._regulations.remove(reg)
                logger.info(f"Removed regulation '{regulation_name}' (folder: {reg})")
                return True
        
        logger.warning(f"Regulation '{regulation_name}' not found in this set")
        return False
    
    def get_regulations(self) -> List[str]:
        """
        Get all regulations in this set.
        
        Returns:
            List of regulation names
        """
        return list(self._regulations)
    
    def clear(self) -> None:
        """
        Remove all regulations from this set.
        """
        self._regulations.clear()
        logger.info("Cleared all regulations from set")

    def get_evaluator(self) -> OpaEvaluator:
        """
        Get the OPA evaluator for this regulation set.
        
        Returns:
            OpaEvaluator instance
        """
        return self._opa_evaluator


def create(name: str = "default") -> RegulationSet:
    """
    Create a new regulation set.
    
    Args:
        name: Name of the regulation set
        
    Returns:
        A new RegulationSet instance
    """
    return RegulationSet(name) 