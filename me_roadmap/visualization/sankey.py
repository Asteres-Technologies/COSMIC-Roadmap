"""
Sankey diagram visualization for roadmap data.

This module provides functions to generate Sankey diagrams showing the flow relationships
between use_cases, capabilities, dependency levels, and readiness levels.
"""
import plotly.graph_objects as go
import plotly.offline as pyo
from me_roadmap.data_processing.models import RoadmapData
from me_roadmap.visualization import PRIMARY_COLOR, SECONDARY_COLOR
from typing import Dict, List, Tuple, Optional
import os
import numpy as np
from collections import defaultdict


def create_sankey_data(roadmap_data: RoadmapData, 
                      flow_type: str = "use_case_to_capability",
                      min_dependency_level: float = 0.0,
                      max_use_cases: Optional[int] = None) -> Dict:
    """
    Creates the data structure needed for a Sankey diagram.
    
    Args:
        roadmap_data (RoadmapData): The roadmap data to visualize
        flow_type (str): Type of flow to visualize:
            - "use_case_to_capability": Use_Cases -> Capabilities
            - "capability_to_readiness": Capabilities -> Readiness Levels  
            - "use_case_to_readiness": Use_Cases -> Capabilities -> Readiness Levels
            - "dependency_flow": Dependency Levels -> Capabilities -> Readiness Levels
        min_dependency_level (float): Minimum dependency level to include
        max_use_cases (int, optional): Limit number of use_cases for clarity
        
    Returns:
        Dict: Sankey diagram data structure with nodes and links
    """
    if not roadmap_data.use_cases:
        return {"nodes": [], "links": []}
    
    use_cases = list(roadmap_data.use_cases.keys())
    if max_use_cases:
        use_cases = use_cases[:max_use_cases]
    
    capabilities = roadmap_data.get_all_capabilities()
    
    if flow_type == "use_case_to_capability":
        return _create_use_case_capability_flow(roadmap_data, use_cases, capabilities, min_dependency_level)
    elif flow_type == "capability_to_readiness":
        return _create_capability_readiness_flow(roadmap_data, use_cases, capabilities, min_dependency_level)
    elif flow_type == "use_case_to_readiness":
        return _create_use_case_readiness_flow(roadmap_data, use_cases, capabilities, min_dependency_level)
    elif flow_type == "dependency_flow":
        return _create_dependency_flow(roadmap_data, use_cases, capabilities, min_dependency_level)
    else:
        raise ValueError(f"Unknown flow_type: {flow_type}")


def _create_use_case_capability_flow(roadmap_data: RoadmapData, 
                                   use_cases: List[str], 
                                   capabilities: List[str],
                                   min_dependency_level: float) -> Dict:
    """Create Use_Case -> Capability flow."""
    nodes = []
    links = []
    
    # Create nodes
    use_case_nodes = {use_case: i for i, use_case in enumerate(use_cases)}
    capability_nodes = {cap: i + len(use_cases) for i, cap in enumerate(capabilities)}
    
    # Add use_case nodes
    for use_case in use_cases:
        nodes.append({
            "label": f"Use_Case: {use_case[:30]}{'...' if len(use_case) > 30 else ''}",
            "color": PRIMARY_COLOR,
            "group": "use_case"
        })
    
    # Add capability nodes  
    for capability in capabilities:
        nodes.append({
            "label": f"Capability: {capability}",
            "color": SECONDARY_COLOR,
            "group": "capability"
        })
    
    # Create links
    for use_case in use_cases:
        use_case_obj = roadmap_data.use_cases[use_case]
        for capability, entry in use_case_obj.capabilities.items():
            if capability in capabilities and entry.dependency_level is not None:
                if entry.dependency_level >= min_dependency_level:
                    links.append({
                        "source": use_case_nodes[use_case],
                        "target": capability_nodes[capability],
                        "value": entry.dependency_level,
                        "label": f"Dependency: {entry.dependency_level}"
                    })
    
    return {"nodes": nodes, "links": links}


def _create_capability_readiness_flow(roadmap_data: RoadmapData,
                                     use_cases: List[str],
                                     capabilities: List[str],
                                     min_dependency_level: float) -> Dict:
    """Create Capability -> Readiness Level flow."""
    nodes = []
    links = []
    
    # Collect unique readiness levels
    readiness_levels = set()
    for use_case in use_cases:
        use_case_obj = roadmap_data.use_cases[use_case]
        for capability, entry in use_case_obj.capabilities.items():
            if (capability in capabilities and 
                entry.dependency_level is not None and 
                entry.dependency_level >= min_dependency_level and
                entry.readiness_level is not None):
                readiness_levels.add(entry.readiness_level)
    
    readiness_levels = sorted(list(readiness_levels))
    
    # Create nodes
    capability_nodes = {cap: i for i, cap in enumerate(capabilities)}
    readiness_nodes = {rl: i + len(capabilities) for i, rl in enumerate(readiness_levels)}
    
    # Add capability nodes
    for capability in capabilities:
        nodes.append({
            "label": f"Capability: {capability}",
            "color": PRIMARY_COLOR,
            "group": "capability"
        })
    
    # Add readiness nodes
    for readiness_level in readiness_levels:
        nodes.append({
            "label": f"Readiness Level: {readiness_level}",
            "color": SECONDARY_COLOR,
            "group": "readiness"
        })
    
    # Create links - aggregate by capability and readiness level
    capability_readiness_counts = defaultdict(lambda: defaultdict(int))
    
    for use_case in use_cases:
        use_case_obj = roadmap_data.use_cases[use_case]
        for capability, entry in use_case_obj.capabilities.items():
            if (capability in capabilities and 
                entry.dependency_level is not None and 
                entry.dependency_level >= min_dependency_level and
                entry.readiness_level is not None):
                capability_readiness_counts[capability][entry.readiness_level] += 1
    
    for capability, readiness_counts in capability_readiness_counts.items():
        for readiness_level, count in readiness_counts.items():
            links.append({
                "source": capability_nodes[capability],
                "target": readiness_nodes[readiness_level], 
                "value": count,
                "label": f"Count: {count}"
            })
    
    return {"nodes": nodes, "links": links}


def _create_use_case_readiness_flow(roadmap_data: RoadmapData,
                                  use_cases: List[str],
                                  capabilities: List[str],
                                  min_dependency_level: float) -> Dict:
    """Create Use_Case -> Capability -> Readiness Level flow."""
    nodes = []
    links = []
    
    # Collect unique readiness levels
    readiness_levels = set()
    for use_case in use_cases:
        use_case_obj = roadmap_data.use_cases[use_case]
        for capability, entry in use_case_obj.capabilities.items():
            if (capability in capabilities and 
                entry.dependency_level is not None and 
                entry.dependency_level >= min_dependency_level and
                entry.readiness_level is not None):
                readiness_levels.add(entry.readiness_level)
    
    readiness_levels = sorted(list(readiness_levels))
    
    # Create nodes with proper indexing
    use_case_nodes = {use_case: i for i, use_case in enumerate(use_cases)}
    capability_nodes = {cap: i + len(use_cases) for i, cap in enumerate(capabilities)}
    readiness_nodes = {rl: i + len(use_cases) + len(capabilities) for i, rl in enumerate(readiness_levels)}
    
    # Add nodes
    for use_case in use_cases:
        nodes.append({
            "label": f"Use_Case: {use_case[:25]}{'...' if len(use_case) > 25 else ''}",
            "color": PRIMARY_COLOR,
            "group": "use_case"
        })
    
    for capability in capabilities:
        nodes.append({
            "label": f"Capability: {capability[:20]}{'...' if len(capability) > 20 else ''}",
            "color": "#7fb069",  # Medium green
            "group": "capability"
        })
    
    for readiness_level in readiness_levels:
        nodes.append({
            "label": f"Readiness: {readiness_level}",
            "color": SECONDARY_COLOR,
            "group": "readiness"
        })
    
    # Create Use_Case -> Capability links
    use_case_capability_flows = defaultdict(lambda: defaultdict(float))
    
    for use_case in use_cases:
        use_case_obj = roadmap_data.use_cases[use_case]
        for capability, entry in use_case_obj.capabilities.items():
            if (capability in capabilities and 
                entry.dependency_level is not None and 
                entry.dependency_level >= min_dependency_level):
                use_case_capability_flows[use_case][capability] += entry.dependency_level
    
    for use_case, capability_flows in use_case_capability_flows.items():
        for capability, flow_value in capability_flows.items():
            links.append({
                "source": use_case_nodes[use_case],
                "target": capability_nodes[capability],
                "value": flow_value,
                "label": f"Dependency: {flow_value:.1f}"
            })
    
    # Create Capability -> Readiness links
    capability_readiness_flows = defaultdict(lambda: defaultdict(int))
    
    for use_case in use_cases:
        use_case_obj = roadmap_data.use_cases[use_case]
        for capability, entry in use_case_obj.capabilities.items():
            if (capability in capabilities and 
                entry.dependency_level is not None and 
                entry.dependency_level >= min_dependency_level and
                entry.readiness_level is not None):
                capability_readiness_flows[capability][entry.readiness_level] += 1
    
    for capability, readiness_flows in capability_readiness_flows.items():
        for readiness_level, count in readiness_flows.items():
            links.append({
                "source": capability_nodes[capability],
                "target": readiness_nodes[readiness_level],
                "value": count,
                "label": f"Count: {count}"
            })
    
    return {"nodes": nodes, "links": links}


def _create_dependency_flow(roadmap_data: RoadmapData,
                           use_cases: List[str],
                           capabilities: List[str],
                           min_dependency_level: float) -> Dict:
    """Create Dependency Level -> Capability -> Readiness Level flow."""
    nodes = []
    links = []
    
    # Collect unique dependency and readiness levels
    dependency_levels = set()
    readiness_levels = set()
    
    for use_case in use_cases:
        use_case_obj = roadmap_data.use_cases[use_case]
        for capability, entry in use_case_obj.capabilities.items():
            if (capability in capabilities and 
                entry.dependency_level is not None and 
                entry.dependency_level >= min_dependency_level):
                dependency_levels.add(entry.dependency_level)
                if entry.readiness_level is not None:
                    readiness_levels.add(entry.readiness_level)
    
    dependency_levels = sorted(list(dependency_levels))
    readiness_levels = sorted(list(readiness_levels))
    
    # Create nodes
    dependency_nodes = {dl: i for i, dl in enumerate(dependency_levels)}
    capability_nodes = {cap: i + len(dependency_levels) for i, cap in enumerate(capabilities)}
    readiness_nodes = {rl: i + len(dependency_levels) + len(capabilities) for i, rl in enumerate(readiness_levels)}
    
    # Add nodes
    for dep_level in dependency_levels:
        nodes.append({
            "label": f"Dependency: {dep_level}",
            "color": PRIMARY_COLOR,
            "group": "dependency"
        })
    
    for capability in capabilities:
        nodes.append({
            "label": f"Capability: {capability[:20]}{'...' if len(capability) > 20 else ''}",
            "color": "#7fb069",
            "group": "capability"
        })
    
    for readiness_level in readiness_levels:
        nodes.append({
            "label": f"Readiness: {readiness_level}",
            "color": SECONDARY_COLOR,
            "group": "readiness"
        })
    
    # Create Dependency -> Capability links
    dep_cap_flows = defaultdict(lambda: defaultdict(int))
    cap_readiness_flows = defaultdict(lambda: defaultdict(int))
    
    for use_case in use_cases:
        use_case_obj = roadmap_data.use_cases[use_case]
        for capability, entry in use_case_obj.capabilities.items():
            if (capability in capabilities and 
                entry.dependency_level is not None and 
                entry.dependency_level >= min_dependency_level):
                dep_cap_flows[entry.dependency_level][capability] += 1
                
                if entry.readiness_level is not None:
                    cap_readiness_flows[capability][entry.readiness_level] += 1
    
    # Add Dependency -> Capability links
    for dep_level, cap_flows in dep_cap_flows.items():
        for capability, count in cap_flows.items():
            links.append({
                "source": dependency_nodes[dep_level],
                "target": capability_nodes[capability],
                "value": count,
                "label": f"Count: {count}"
            })
    
    # Add Capability -> Readiness links
    for capability, readiness_flows in cap_readiness_flows.items():
        for readiness_level, count in readiness_flows.items():
            links.append({
                "source": capability_nodes[capability],
                "target": readiness_nodes[readiness_level],
                "value": count,
                "label": f"Count: {count}"
            })
    
    return {"nodes": nodes, "links": links}


def plot_sankey(roadmap_data: RoadmapData,
               flow_type: str = "use_case_to_capability",
               min_dependency_level: float = 0.0,
               max_use_cases: Optional[int] = None,
               title: Optional[str] = None,
               output_dir: Optional[str] = None,
               show_plot: bool = True) -> str:
    """
    Creates and saves a Sankey diagram for roadmap data.
    
    Args:
        roadmap_data (RoadmapData): The roadmap data to visualize
        flow_type (str): Type of flow to visualize
        min_dependency_level (float): Minimum dependency level to include
        max_use_cases (int, optional): Limit number of use_cases for clarity
        title (str, optional): Custom title for the plot
        output_dir (str, optional): Directory to save the plot
        show_plot (bool): Whether to display the plot in browser
        
    Returns:
        str: Path to the saved HTML file
    """
    if not roadmap_data.use_cases:
        print("❌ No roadmap data available to display.")
        return ""
    
    # Create Sankey data
    sankey_data = create_sankey_data(
        roadmap_data, 
        flow_type=flow_type,
        min_dependency_level=min_dependency_level,
        max_use_cases=max_use_cases
    )
    
    if not sankey_data["nodes"] or not sankey_data["links"]:
        print("❌ No data available for the specified criteria.")
        return ""
    
    # Set default title
    if title is None:
        title_map = {
            "use_case_to_capability": "Use_Case to Capability Flow",
            "capability_to_readiness": "Capability to Readiness Flow", 
            "use_case_to_readiness": "Use_Case → Capability → Readiness Flow",
            "dependency_flow": "Dependency → Capability → Readiness Flow"
        }
        title = f"COSMIC Roadmap: {title_map.get(flow_type, 'Data Flow')}"
    
    # Create Plotly Sankey figure
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=[node["label"] for node in sankey_data["nodes"]],
            color=[node["color"] for node in sankey_data["nodes"]]
        ),
        link=dict(
            source=[link["source"] for link in sankey_data["links"]],
            target=[link["target"] for link in sankey_data["links"]],
            value=[link["value"] for link in sankey_data["links"]],
            hovertemplate='<b>%{source.label}</b> → <b>%{target.label}</b><br>' +
                         'Value: %{value}<br>' +
                         '<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title_text=title,
        title_x=0.5,
        title_font_size=16,
        font_size=10,
        height=600
    )
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '../../data/processed/sankey')
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the plot
    filename = f"roadmap_sankey_{flow_type}.html"
    output_path = os.path.join(output_dir, filename)
    
    fig.write_html(output_path)
    print(f"✅ Sankey diagram saved to {output_path}")
    
    if show_plot:
        fig.show()
    
    return output_path


def plot_all_sankey_types(roadmap_data: RoadmapData,
                         min_dependency_level: float = 0.0,
                         max_use_cases: Optional[int] = 10,
                         output_dir: Optional[str] = None) -> List[str]:
    """
    Creates all types of Sankey diagrams for comprehensive analysis.
    
    Args:
        roadmap_data (RoadmapData): The roadmap data to visualize
        min_dependency_level (float): Minimum dependency level to include
        max_use_cases (int, optional): Limit number of use_cases for clarity
        output_dir (str, optional): Directory to save the plots
        
    Returns:
        List[str]: Paths to all saved HTML files
    """
    flow_types = [
        "use_case_to_capability",
        "capability_to_readiness", 
        "use_case_to_readiness",
        "dependency_flow"
    ]
    
    saved_files = []
    
    for flow_type in flow_types:
        try:
            output_path = plot_sankey(
                roadmap_data,
                flow_type=flow_type,
                min_dependency_level=min_dependency_level,
                max_use_cases=max_use_cases,
                output_dir=output_dir,
                show_plot=False
            )
            if output_path:
                saved_files.append(output_path)
        except Exception as e:
            print(f"❌ Error creating {flow_type} Sankey diagram: {e}")
    
    print(f"\n✅ Created {len(saved_files)} Sankey diagrams in {output_dir or 'default directory'}")
    return saved_files