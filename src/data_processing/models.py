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
    def is_mission_critical(self) -> bool:
        """Check if this capability is mission critical."""
        return self.dependency is not None and "Mission Critical" in self.dependency
    
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


class Mission(BaseModel):
    """
    Represents a mission with its associated capabilities.
    """
    name: str
    capabilities: Dict[str, RoadmapEntry]
    
    def get_critical_capabilities(self) -> List[str]:
        """Get list of mission critical capabilities."""
        return [
            capability for capability, entry in self.capabilities.items()
            if entry.is_mission_critical
        ]
    
    def get_unused_capabilities(self) -> List[str]:
        """Get list of unused capabilities."""
        return [
            capability for capability, entry in self.capabilities.items()
            if entry.is_not_used
        ]
    
    def get_capability_count(self) -> int:
        """Get total number of capabilities for this mission."""
        return len(self.capabilities)


class RoadmapData(BaseModel):
    """
    Main container for all roadmap data with analysis methods.
    """
    missions: Dict[str, Mission]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Any]]) -> "RoadmapData":
        """
        Create RoadmapData from the legacy dictionary format.
        
        Args:
            data: Dictionary in format {mission: {capability: (dependency, readiness)}}
            
        Returns:
            RoadmapData instance
        """
        missions = {}
        for mission_name, capabilities_dict in data.items():
            capabilities = {}
            for capability_name, (dependency, readiness) in capabilities_dict.items():
                capabilities[capability_name] = RoadmapEntry(
                    dependency=dependency,
                    readiness=readiness
                )
            missions[mission_name] = Mission(
                name=mission_name,
                capabilities=capabilities
            )
        return cls(missions=missions)
    
    def to_dict(self) -> Dict[str, Dict[str, tuple]]:
        """
        Convert back to legacy dictionary format for backward compatibility.
        
        Returns:
            Dictionary in format {mission: {capability: (dependency, readiness)}}
        """
        result = {}
        for mission_name, mission in self.missions.items():
            result[mission_name] = {}
            for capability_name, entry in mission.capabilities.items():
                result[mission_name][capability_name] = (entry.dependency, entry.readiness)
        return result
    
    def get_mission_names(self) -> List[str]:
        """Get list of all mission names."""
        return list(self.missions.keys())
    
    def get_all_capabilities(self) -> List[str]:
        """Get list of all unique capabilities across missions."""
        capabilities = set()
        for mission in self.missions.values():
            capabilities.update(mission.capabilities.keys())
        return sorted(list(capabilities))
    
    def get_missions_using_capability(self, capability: str) -> List[str]:
        """Get list of missions that use a specific capability."""
        missions = []
        for mission_name, mission in self.missions.items():
            if capability in mission.capabilities and not mission.capabilities[capability].is_not_used:
                missions.append(mission_name)
        return missions
    
    def get_critical_capabilities_by_mission(self, mission_name: str) -> List[str]:
        """Get mission critical capabilities for a specific mission."""
        if mission_name not in self.missions:
            return []
        return self.missions[mission_name].get_critical_capabilities()
    
    def get_capability_usage_stats(self) -> Dict[str, int]:
        """Get usage statistics for all capabilities."""
        stats = {}
        for capability in self.get_all_capabilities():
            stats[capability] = len(self.get_missions_using_capability(capability))
        return stats
    
    def get_mission_count(self) -> int:
        """Get total number of missions."""
        return len(self.missions)
    
    def get_total_capability_entries(self) -> int:
        """Get total number of capability entries across all missions."""
        return sum(mission.get_capability_count() for mission in self.missions.values())
    
    def get_average_capabilities_per_mission(self) -> float:
        """Get average number of capabilities per mission."""
        if not self.missions:
            return 0.0
        return self.get_total_capability_entries() / self.get_mission_count()
