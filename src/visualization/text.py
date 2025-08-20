"""
A module to support text or console based visualization of roadmap data.
Provides clean, readable formatting for debugging and verification purposes.
"""
from typing import Dict, Tuple, Any, Optional
import pandas as pd


def format_value(value: Any) -> str:
    """
    Format a single value for display, handling NaN values gracefully.
    
    Args:
        value: The value to format
        
    Returns:
        str: Formatted string representation
    """
    if pd.isna(value):
        return "N/A"
    return str(value)


def print_roadmap_sample(roadmap_data: Dict[str, Dict[str, Tuple[Any, Any]]], 
                        mission_key: Optional[str] = None) -> None:
    """
    Prints a clean, formatted sample of the roadmap data for verification purposes.

    Args:
        roadmap_data (dict): The combined roadmap data structure.
        mission_key (str, optional): Specific mission to print. If None, prints the first mission.
    """
    if not roadmap_data:
        print("❌ No roadmap data available to display.")
        return

    if mission_key is None:
        mission_key = list(roadmap_data.keys())[0]
    
    if mission_key not in roadmap_data:
        print(f"❌ Mission '{mission_key}' not found in roadmap data.")
        return

    print("="*80)
    print("📊 COSMIC ROADMAP DATA - SAMPLE")
    print("="*80)
    print(f"\n🎯 Mission: {mission_key}")
    print("-" * 80)
    
    capabilities = roadmap_data[mission_key]
    
    for capability, (dependency, readiness) in capabilities.items():
        dep_str = format_value(dependency)
        read_str = format_value(readiness)
        
        print(f"\n🔧 {capability}")
        print(f"   └─ Dependency:  {dep_str}")
        print(f"   └─ Readiness:   {read_str}")
    
    print("\n" + "="*80)


def print_full_roadmap(roadmap_data: Dict[str, Dict[str, Tuple[Any, Any]]]) -> None:
    """
    Prints the entire roadmap data structure in a clean, readable format.

    Args:
        roadmap_data (dict): The combined roadmap data structure.
    """
    if not roadmap_data:
        print("❌ No roadmap data available to display.")
        return

    print("="*100)
    print("📊 COSMIC ROADMAP DATA - COMPLETE ANALYSIS")
    print("="*100)
    
    for i, (mission, capabilities) in enumerate(roadmap_data.items(), 1):
        print(f"\n🎯 Mission {i}: {mission}")
        print("-" * 100)
        
        for capability, (dependency, readiness) in capabilities.items():
            dep_str = format_value(dependency)
            read_str = format_value(readiness)
            
            print(f"\n  🔧 {capability}")
            print(f"     └─ Dependency:  {dep_str}")
            print(f"     └─ Readiness:   {read_str}")
        
        if i < len(roadmap_data):  # Don't print separator after last mission
            print("\n" + "─" * 100)
    
    print("\n" + "="*100)


def print_roadmap_table(roadmap_data: Dict[str, Dict[str, Tuple[Any, Any]]], 
                       mission_key: Optional[str] = None) -> None:
    """
    Prints roadmap data in a clean table format.

    Args:
        roadmap_data (dict): The combined roadmap data structure.
        mission_key (str, optional): Specific mission to print. If None, prints the first mission.
    """
    if not roadmap_data:
        print("❌ No roadmap data available to display.")
        return

    if mission_key is None:
        mission_key = list(roadmap_data.keys())[0]
    
    if mission_key not in roadmap_data:
        print(f"❌ Mission '{mission_key}' not found in roadmap data.")
        return

    capabilities = roadmap_data[mission_key]
    
    print("="*120)
    print(f"📊 ROADMAP TABLE: {mission_key}")
    print("="*120)
    
    # Table header
    print(f"{'CAPABILITY':<45} {'DEPENDENCY':<35} {'READINESS':<35}")
    print("-" * 120)
    
    # Table rows
    for capability, (dependency, readiness) in capabilities.items():
        dep_str = format_value(dependency)[:33]  # Truncate if too long
        read_str = format_value(readiness)[:33]
        
        print(f"{capability:<45} {dep_str:<35} {read_str:<35}")
    
    print("="*120)


def print_roadmap_summary(roadmap_data: Dict[str, Dict[str, Tuple[Any, Any]]]) -> None:
    """
    Prints a high-level summary of the roadmap data.

    Args:
        roadmap_data (dict): The combined roadmap data structure.
    """
    if not roadmap_data:
        print("❌ No roadmap data available to display.")
        return

    print("="*80)
    print("📈 COSMIC ROADMAP SUMMARY")
    print("="*80)
    
    total_missions = len(roadmap_data)
    total_capabilities = sum(len(capabilities) for capabilities in roadmap_data.values())
    
    print(f"\n📊 Overview:")
    print(f"   └─ Total Missions: {total_missions}")
    print(f"   └─ Total Capabilities: {total_capabilities}")
    print(f"   └─ Avg Capabilities per Mission: {total_capabilities/total_missions:.1f}")
    
    print(f"\n🎯 Missions:")
    for i, mission in enumerate(roadmap_data.keys(), 1):
        capability_count = len(roadmap_data[mission])
        print(f"   {i:2d}. {mission[:70]}{'...' if len(mission) > 70 else ''}")
        print(f"       └─ {capability_count} capabilities")
    
    print("\n" + "="*80)


def print_capabilities_analysis(roadmap_data: Dict[str, Dict[str, Tuple[Any, Any]]]) -> None:
    """
    Prints an analysis of capabilities across all missions.

    Args:
        roadmap_data (dict): The combined roadmap data structure.
    """
    if not roadmap_data:
        print("❌ No roadmap data available to display.")
        return

    # Collect all unique capabilities
    all_capabilities = set()
    for mission_capabilities in roadmap_data.values():
        all_capabilities.update(mission_capabilities.keys())
    
    print("="*100)
    print("🔧 CAPABILITIES ANALYSIS")
    print("="*100)
    
    print(f"\n📊 Total Unique Capabilities: {len(all_capabilities)}")
    print("\n🔧 All Capabilities:")
    
    for i, capability in enumerate(sorted(all_capabilities), 1):
        # Count how many missions use this capability
        usage_count = sum(1 for mission_caps in roadmap_data.values() 
                         if capability in mission_caps)
        print(f"   {i:2d}. {capability}")
        print(f"       └─ Used in {usage_count} mission(s)")
    
    print("\n" + "="*100)