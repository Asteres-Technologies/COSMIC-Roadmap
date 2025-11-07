"""
A module to support text or console based visualization of roadmap data.
Provides clean, readable formatting for debugging and verification purposes.
"""
from me_roadmap.data_processing.models import RoadmapData
from typing import Optional
import pandas as pd


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
                        use_case_key: Optional[str] = None) -> None:
    """
    Prints a clean, formatted sample of the roadmap data for verification purposes.

    Args:
        roadmap_data (RoadmapData): The combined roadmap data structure.
        use_case_key (str, optional): Specific use_case to print. If None, prints the first use_case.
    """
    if not roadmap_data.use_cases:
        print("❌ No roadmap data available to display.")
        return

    if use_case_key is None:
        use_case_key = list(roadmap_data.use_cases.keys())[0]
    
    if use_case_key not in roadmap_data.use_cases:
        print(f"❌ Use Case '{use_case_key}' not found in roadmap data.")
        return

    print("="*80)
    print("📊 COSMIC ROADMAP DATA - SAMPLE")
    print("="*80)
    print(f"\n🎯 Use Case: {use_case_key}")
    print("-" * 80)
    
    use_case = roadmap_data.use_cases[use_case_key]
    
    for capability, entry in use_case.capabilities.items():
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
    if not roadmap_data.use_cases:
        print("❌ No roadmap data available to display.")
        return

    print("="*100)
    print("📊 COSMIC ROADMAP DATA - COMPLETE ANALYSIS")
    print("="*100)
    
    for i, (use_case_name, use_case) in enumerate(roadmap_data.use_cases.items(), 1):
        print(f"\n🎯 Use Case {i}: {use_case_name}")
        print("-" * 100)
        
        for capability, entry in use_case.capabilities.items():
            dep_str = format_value(entry.dependency)
            read_str = format_value(entry.readiness)
            
            print(f"\n  🔧 {capability}")
            print(f"     └─ Dependency:  {dep_str}")
            print(f"     └─ Readiness:   {read_str}")
        
        if i < len(roadmap_data.use_cases):
            print("\n" + "─" * 100)
    
    print("\n" + "="*100)


def print_roadmap_table(roadmap_data: RoadmapData, 
                       use_case_key: Optional[str] = None) -> None:
    """
    Prints roadmap data in a clean table format.

    Args:
        roadmap_data (RoadmapData): The combined roadmap data structure.
        use_case_key (str, optional): Specific use_case to print. If None, prints the first use_case.
    """
    if not roadmap_data.use_cases:
        print("❌ No roadmap data available to display.")
        return

    if use_case_key is None:
        use_case_key = list(roadmap_data.use_cases.keys())[0]
    
    if use_case_key not in roadmap_data.use_cases:
        print(f"❌ Use Case '{use_case_key}' not found in roadmap data.")
        return

    use_case = roadmap_data.use_cases[use_case_key]
    
    print("="*120)
    print(f"📊 ROADMAP TABLE: {use_case_key}")
    print("="*120)
    
    print(f"{'CAPABILITY':<45} {'DEPENDENCY':<35} {'READINESS':<35}")
    print("-" * 120)
    
    for capability, entry in use_case.capabilities.items():
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
    if not roadmap_data.use_cases:
        print("❌ No roadmap data available to display.")
        return

    print("="*80)
    print("📈 COSMIC ROADMAP SUMMARY")
    print("="*80)
    
    # Get all capabilities across use cases
    all_capabilities = roadmap_data.get_all_capabilities()
    
    print(f"\n📊 Use Cases and Contributors:")
    for i, (use_case_name, use_case) in enumerate(roadmap_data.use_cases.items(), 1):
        contributor = use_case.contributor or 'TBD'
        print(f"   {i:2d}. {use_case_name}")
        print(f"       └─ Contributor: {contributor}")
    
    print(f"\n🔧 Capabilities ({len(all_capabilities)} total):")
    for i, capability in enumerate(all_capabilities, 1):
        print(f"   {i:2d}. {capability}")
    
    print("\n" + "="*80)


def print_capabilities_analysis(roadmap_data: RoadmapData) -> None:
    """
    Prints an analysis of capabilities across all use_cases.

    Args:
        roadmap_data (RoadmapData): The combined roadmap data structure.
    """
    if not roadmap_data.use_cases:
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
        print(f"       └─ Used in {usage_count} use_case(s)")
    
    print("\n" + "="*100)