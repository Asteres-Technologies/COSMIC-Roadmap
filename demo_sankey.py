"""
Demo script for Sankey diagram functionality.

This script demonstrates how to use the Sankey visualization features
with sample or existing roadmap data.
"""
from me_roadmap.data_processing.models import RoadmapData, Use_Case, RoadmapEntry
from me_roadmap.visualization.sankey import plot_sankey, plot_all_sankey_types
from me_roadmap.data_processing.combine import create_combined_roadmap
import os


def create_sample_data() -> RoadmapData:
    """
    Creates sample roadmap data for demonstration purposes.
    
    Returns:
        RoadmapData: Sample data structure
    """
    use_cases_data = {
        "Satellite Deployment": {
            "Inspection and Metrology": RoadmapEntry(dependency="1.0 - Use_Case Critical", readiness="13 - Sustainable System"),
            "Relocation": RoadmapEntry(dependency="1.0 - Use_Case Critical", readiness="7 - System Demonstration"),
            "Docking": RoadmapEntry(dependency="0.8 - High", readiness="9 - System Qualification"),
            "Power Systems": RoadmapEntry(dependency="0.9 - High", readiness="11 - System Operation")
        },
        "Spare Parts Manufacturing": {
            "Parts and Good Manufacture": RoadmapEntry(dependency="1.0 - Use_Case Critical", readiness="5 - Component Validation"),
            "Material Processing": RoadmapEntry(dependency="0.9 - High", readiness="6 - System Integration"),
            "Quality Control": RoadmapEntry(dependency="0.8 - High", readiness="8 - System Validation"),
            "Assembly": RoadmapEntry(dependency="0.7 - Medium", readiness="7 - System Demonstration")
        },
        "Space Station Maintenance": {
            "Inspection and Metrology": RoadmapEntry(dependency="0.9 - High", readiness="13 - Sustainable System"),
            "Repair Operations": RoadmapEntry(dependency="1.0 - Use_Case Critical", readiness="4 - Component Testing"),
            "Tool Management": RoadmapEntry(dependency="0.6 - Medium", readiness="8 - System Validation"),
            "Safety Systems": RoadmapEntry(dependency="1.0 - Use_Case Critical", readiness="10 - System Test")
        },
        "Deep Space Use_Cases": {
            "Communication Systems": RoadmapEntry(dependency="1.0 - Use_Case Critical", readiness="12 - System Proven"),
            "Navigation": RoadmapEntry(dependency="0.9 - High", readiness="11 - System Operation"),
            "Life Support": RoadmapEntry(dependency="1.0 - Use_Case Critical", readiness="9 - System Qualification"),
            "Propulsion": RoadmapEntry(dependency="0.8 - High", readiness="8 - System Validation")
        }
    }
    
    use_cases = {}
    for use_case_name, capabilities_dict in use_cases_data.items():
        use_cases[use_case_name] = Use_Case(
            name=use_case_name,
            capabilities=capabilities_dict
        )
    
    return RoadmapData(use_cases=use_cases)


def demo_sankey_with_sample_data():
    """Demonstrates Sankey diagrams with sample data."""
    print("🚀 Creating Sankey diagrams with sample data...")
    
    sample_data = create_sample_data()
    
    print("\n📊 Sample Data Summary:")
    print(f"   └─ Use Cases: {sample_data.get_use_case_count()}")
    print(f"   └─ Capabilities: {len(sample_data.get_all_capabilities())}")
    
    # Create different types of Sankey diagrams
    output_dir = os.path.join("data", "processed", "sankey", "demo")
    
    print(f"\n🎯 Creating Sankey diagrams in: {output_dir}")
    
    # Use Case to Capability flow
    print("\n1. Use Case → Capability Flow")
    plot_sankey(
        sample_data,
        flow_type="use_case_to_capability",
        title="COSMIC Demo: Use Case to Capability Flow",
        output_dir=output_dir,
        show_plot=False
    )
    
    # Capability to Readiness flow  
    print("\n2. Capability → Readiness Flow")
    plot_sankey(
        sample_data,
        flow_type="capability_to_readiness", 
        title="COSMIC Demo: Capability to Readiness Flow",
        output_dir=output_dir,
        show_plot=False
    )
    
    # Use Case to Readiness flow (3-level)
    print("\n3. Use Case → Capability → Readiness Flow")
    plot_sankey(
        sample_data,
        flow_type="use_case_to_readiness",
        title="COSMIC Demo: Complete Flow Analysis",
        output_dir=output_dir,
        show_plot=False
    )
    
    # Dependency flow
    print("\n4. Dependency → Capability → Readiness Flow")
    plot_sankey(
        sample_data,
        flow_type="dependency_flow",
        title="COSMIC Demo: Dependency Analysis Flow",
        output_dir=output_dir,
        show_plot=False
    )
    
    print(f"\n✅ Demo complete! Check the HTML files in: {output_dir}")


def demo_sankey_with_real_data():
    """Demonstrates Sankey diagrams with real CSV data if available."""
    dependency_file = os.path.join("data", "raw", "Roadmap-dependency.csv")
    readiness_file = os.path.join("data", "raw", "Roadmap-readiness.csv")
    
    if os.path.exists(dependency_file) and os.path.exists(readiness_file):
        print("\n🚀 Creating Sankey diagrams with real roadmap data...")
        
        try:
            roadmap_data = create_combined_roadmap(dependency_file, readiness_file)
            
            if roadmap_data.use_cases:
                print(f"\n📊 Real Data Summary:")
                print(f"   └─ Use Cases: {roadmap_data.get_use_case_count()}")
                print(f"   └─ Capabilities: {len(roadmap_data.get_all_capabilities())}")
                
                # Create all types with limited use_cases for clarity
                print("\n🎯 Creating comprehensive Sankey analysis...")
                saved_files = plot_all_sankey_types(
                    roadmap_data,
                    max_use_cases=8,  # Limit for readability
                    min_dependency_level=0.5  # Filter for meaningful relationships
                )
                
                print(f"\n✅ Created {len(saved_files)} Sankey diagrams with real data!")
            else:
                print("❌ Could not load real roadmap data.")
        except Exception as e:
            print(f"❌ Error processing real data: {e}")
    else:
        print("\n⚠️  Real CSV files not found. Using sample data only.")


if __name__ == "__main__":
    print("="*60)
    print("🎯 COSMIC ROADMAP SANKEY DEMO")
    print("="*60)
    
    # Always demo with sample data
    demo_sankey_with_sample_data()
    
    # Try to demo with real data if available
    demo_sankey_with_real_data()
    
    print("\n" + "="*60)
    print("📖 USAGE INSTRUCTIONS:")
    print("="*60)
    print("To use Sankey diagrams in the main script:")
    print("  python roadmap.py --dependency data/raw/Roadmap-dependency.csv \\")
    print("                    --readiness data/raw/Roadmap-readiness.csv \\") 
    print("                    --sankey --sankey-type use_case_to_capability")
    print()
    print("Available Sankey types:")
    print("  • use_case_to_capability    - Shows use_case dependencies on capabilities")
    print("  • capability_to_readiness  - Shows capability readiness distributions")
    print("  • use_case_to_readiness     - Shows complete 3-level flow")
    print("  • dependency_flow          - Shows dependency level flows")
    print("  • all                      - Creates all diagram types")
    print("="*60)