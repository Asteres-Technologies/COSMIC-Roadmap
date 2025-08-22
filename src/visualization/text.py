"""
A module to support text or console based visualization of roadmap data.
Provides clean, readable formatting for debugging and verification purposes.
"""
from typing import Optional
import pandas as pd
from ..data_processing.models import RoadmapData


def format_value(value) -> str:
    """
    Format a single value for display, handling NaN values gracefully.
    
    Args:
        value: The value to format
        
    Returns:
        str: Formatted string representation
    """
    if value is None or pd.isna(value):
        return "N/A"
    return str(value)


def print_roadmap_sample(roadmap_data: RoadmapData, 
                        mission_key: Optional[str] = None) -> None:
    """
    Prints a clean, formatted sample of the roadmap data for verification purposes.

    Args:
        roadmap_data (RoadmapData): The combined roadmap data structure.
        mission_key (str, optional): Specific mission to print. If None, prints the first mission.
    """
    if not roadmap_data.missions:
        print("❌ No roadmap data available to display.")
        return

    if mission_key is None:
        mission_key = list(roadmap_data.missions.keys())[0]
    
    if mission_key not in roadmap_data.missions:
        print(f"❌ Mission '{mission_key}' not found in roadmap data.")
        return

    print("="*80)
    print("📊 COSMIC ROADMAP DATA - SAMPLE")
    print("="*80)
    print(f"\n🎯 Mission: {mission_key}")
    print("-" * 80)
    
    mission = roadmap_data.missions[mission_key]
    
    for capability, entry in mission.capabilities.items():
        dep_str = format_value(entry.dependency)
        read_str = format_value(entry.readiness)
        
        print(f"\n🔧 {capability}")
        print(f"   └─ Dependency:  {dep_str}")
        print(f"   └─ Readiness:   {read_str}")
    
    print("\n" + "="*80)


def print_full_roadmap(roadmap_data: RoadmapData) -> None:
    """
    Prints the entire roadmap data structure in a clean, readable format.

    Args:
        roadmap_data (RoadmapData): The combined roadmap data structure.
    """
    if not roadmap_data.missions:
        print("❌ No roadmap data available to display.")
        return

    print("="*100)
    print("📊 COSMIC ROADMAP DATA - COMPLETE ANALYSIS")
    print("="*100)
    
    for i, (mission_name, mission) in enumerate(roadmap_data.missions.items(), 1):
        print(f"\n🎯 Mission {i}: {mission_name}")
        print("-" * 100)
        
        for capability, entry in mission.capabilities.items():
            dep_str = format_value(entry.dependency)
            read_str = format_value(entry.readiness)
            
            print(f"\n  🔧 {capability}")
            print(f"     └─ Dependency:  {dep_str}")
            print(f"     └─ Readiness:   {read_str}")
        
        if i < len(roadmap_data.missions):
            print("\n" + "─" * 100)
    
    print("\n" + "="*100)


def print_roadmap_table(roadmap_data: RoadmapData, 
                       mission_key: Optional[str] = None) -> None:
    """
    Prints roadmap data in a clean table format.

    Args:
        roadmap_data (RoadmapData): The combined roadmap data structure.
        mission_key (str, optional): Specific mission to print. If None, prints the first mission.
    """
    if not roadmap_data.missions:
        print("❌ No roadmap data available to display.")
        return

    if mission_key is None:
        mission_key = list(roadmap_data.missions.keys())[0]
    
    if mission_key not in roadmap_data.missions:
        print(f"❌ Mission '{mission_key}' not found in roadmap data.")
        return

    mission = roadmap_data.missions[mission_key]
    
    print("="*120)
    print(f"📊 ROADMAP TABLE: {mission_key}")
    print("="*120)
    
    print(f"{'CAPABILITY':<45} {'DEPENDENCY':<35} {'READINESS':<35}")
    print("-" * 120)
    
    for capability, entry in mission.capabilities.items():
        dep_str = format_value(entry.dependency)[:33]
        read_str = format_value(entry.readiness)[:33]
        
        print(f"{capability:<45} {dep_str:<35} {read_str:<35}")
    
    print("="*120)


def print_roadmap_summary(roadmap_data: RoadmapData) -> None:
    """
    Prints a high-level summary of the roadmap data.

    Args:
        roadmap_data (RoadmapData): The combined roadmap data structure.
    """
    if not roadmap_data.missions:
        print("❌ No roadmap data available to display.")
        return

    print("="*80)
    print("📈 COSMIC ROADMAP SUMMARY")
    print("="*80)
    
    total_missions = roadmap_data.get_mission_count()
    total_capabilities = roadmap_data.get_total_capability_entries()
    avg_capabilities = roadmap_data.get_average_capabilities_per_mission()
    
    print(f"\n📊 Overview:")
    print(f"   └─ Total Missions: {total_missions}")
    print(f"   └─ Total Capabilities: {total_capabilities}")
    print(f"   └─ Avg Capabilities per Mission: {avg_capabilities:.1f}")
    
    print(f"\n🎯 Missions:")
    for i, (mission_name, mission) in enumerate(roadmap_data.missions.items(), 1):
        capability_count = mission.get_capability_count()
        print(f"   {i:2d}. {mission_name[:70]}{'...' if len(mission_name) > 70 else ''}")
        print(f"       └─ {capability_count} capabilities")
    
    print("\n" + "="*80)


def print_capabilities_analysis(roadmap_data: RoadmapData) -> None:
    """
    Prints an analysis of capabilities across all missions.

    Args:
        roadmap_data (RoadmapData): The combined roadmap data structure.
    """
    if not roadmap_data.missions:
        print("❌ No roadmap data available to display.")
        return

    all_capabilities = roadmap_data.get_all_capabilities()
    usage_stats = roadmap_data.get_capability_usage_stats()
    
    print("="*100)
    print("🔧 CAPABILITIES ANALYSIS")
    print("="*100)
    
    print(f"\n📊 Total Unique Capabilities: {len(all_capabilities)}")
    print("\n🔧 All Capabilities:")
    
    for i, capability in enumerate(all_capabilities, 1):
        usage_count = usage_stats.get(capability, 0)
        print(f"   {i:2d}. {capability}")
        print(f"       └─ Used in {usage_count} mission(s)")
    
    print("\n" + "="*100)