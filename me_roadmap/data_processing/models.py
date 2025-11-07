"""
Pydantic models for roadmap data structures.

This module defines the data models used throughout the COSMIC roadmap system,
providing type safety, validation, and serialization capabilities.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, field_validator
import pandas as pd


class RoadmapEntry(BaseModel):
    """
    Represents a single capability entry with dependency and readiness values.
    """
    dependency: Optional[str] = None
    readiness: Optional[str] = None
    
    @field_validator('dependency', 'readiness', mode='before')
    @classmethod
    def handle_nan_values(cls, v):
        """Convert pandas NaN values to None for cleaner handling."""
        if pd.isna(v):
            return None
        return str(v) if v is not None else None
    
    @property
    def is_use_case_critical(self) -> bool:
        """Check if this capability is use_case critical."""
        return self.dependency is not None and "Use Case Critical" in self.dependency
    
    @property
    def is_not_used(self) -> bool:
        """Check if this capability is not used."""
        return self.dependency is not None and "Not Used" in self.dependency
    
    @property
    def dependency_level(self) -> Optional[float]:
        """Extract numeric dependency level if available."""
        if not self.dependency:
            return None
        try:
            return float(self.dependency.split(' - ')[0])
        except (ValueError, IndexError):
            return None
    
    @property
    def readiness_level(self) -> Optional[int]:
        """Extract numeric readiness level if available."""
        if not self.readiness:
            return None
        try:
            return int(self.readiness.split(' - ')[0])
        except (ValueError, IndexError):
            return None


class Use_Case(BaseModel):
    """
    Represents a use_case with its associated capabilities.
    """
    name: str
    capabilities: Dict[str, RoadmapEntry]
    
    def get_critical_capabilities(self) -> List[str]:
        """Get list of use_case critical capabilities."""
        return [
            capability for capability, entry in self.capabilities.items()
            if entry.is_use_case_critical
        ]
    
    def get_unused_capabilities(self) -> List[str]:
        """Get list of unused capabilities."""
        return [
            capability for capability, entry in self.capabilities.items()
            if entry.is_not_used
        ]
    
    def get_capability_count(self) -> int:
        """Get total number of capabilities for this use_case."""
        return len(self.capabilities)


class RoadmapData(BaseModel):
    """
    Main container for all roadmap data with analysis methods.
    """
    use_cases: Dict[str, Use_Case]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Any]]) -> "RoadmapData":
        """
        Create RoadmapData from the legacy dictionary format.
        
        Args:
            data: Dictionary in format {use_case: {capability: (dependency, readiness)}}
            
        Returns:
            RoadmapData instance
        """
        use_cases = {}
        for use_case_name, capabilities_dict in data.items():
            capabilities = {}
            for capability_name, (dependency, readiness) in capabilities_dict.items():
                capabilities[capability_name] = RoadmapEntry(
                    dependency=dependency,
                    readiness=readiness
                )
            use_cases[use_case_name] = Use_Case(
                name=use_case_name,
                capabilities=capabilities
            )
        return cls(use_cases=use_cases)
    
    def to_dict(self) -> Dict[str, Dict[str, tuple]]:
        """
        Convert back to legacy dictionary format for backward compatibility.
        
        Returns:
            Dictionary in format {use_case: {capability: (dependency, readiness)}}
        """
        result = {}
        for use_case_name, use_case in self.use_cases.items():
            result[use_case_name] = {}
            for capability_name, entry in use_case.capabilities.items():
                result[use_case_name][capability_name] = (entry.dependency, entry.readiness)
        return result
    
    def get_use_case_names(self) -> List[str]:
        """Get list of all use_case names."""
        return list(self.use_cases.keys())
    
    def get_all_capabilities(self) -> List[str]:
        """Get list of all unique capabilities across use_cases."""
        capabilities = set()
        for use_case in self.use_cases.values():
            capabilities.update(use_case.capabilities.keys())
        return sorted(list(capabilities))
    
    def get_use_cases_using_capability(self, capability: str) -> List[str]:
        """Get list of use_cases that use a specific capability."""
        use_cases = []
        for use_case_name, use_case in self.use_cases.items():
            if capability in use_case.capabilities and not use_case.capabilities[capability].is_not_used:
                use_cases.append(use_case_name)
        return use_cases
    
    def get_critical_capabilities_by_use_case(self, use_case_name: str) -> List[str]:
        """Get use_case critical capabilities for a specific use_case."""
        if use_case_name not in self.use_cases:
            return []
        return self.use_cases[use_case_name].get_critical_capabilities()
    
    def get_capability_usage_stats(self) -> Dict[str, int]:
        """Get usage statistics for all capabilities."""
        stats = {}
        for capability in self.get_all_capabilities():
            stats[capability] = len(self.get_use_cases_using_capability(capability))
        return stats
    
    def get_use_case_count(self) -> int:
        """Get total number of use_cases."""
        return len(self.use_cases)
    
    def get_total_capability_entries(self) -> int:
        """Get total number of capability entries across all use_cases."""
        return sum(use_case.get_capability_count() for use_case in self.use_cases.values())
    
    def get_average_capabilities_per_use_case(self) -> float:
        """Get average number of capabilities per use_case."""
        if not self.use_cases:
            return 0.0
        return self.get_total_capability_entries() / self.get_use_case_count()
