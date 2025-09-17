"""
Sankey diagram visualization for roadmap data.

This module provides functions to generate Sankey diagrams showing the flow relationships
between missions, capabilities, dependency levels, and readiness levels.
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
                      flow_type: str = "mission_to_capability",
                      min_dependency_level: float = 0.0,
                      max_missions: Optional[int] = None) -> Dict:
    """
    Creates the data structure needed for a Sankey diagram.
    
    Args:
        roadmap_data (RoadmapData): The roadmap data to visualize
        flow_type (str): Type of flow to visualize:
            - "mission_to_capability": Missions -> Capabilities
            - "capability_to_readiness": Capabilities -> Readiness Levels  
            - "mission_to_readiness": Missions -> Capabilities -> Readiness Levels
            - "dependency_flow": Dependency Levels -> Capabilities -> Readiness Levels
        min_dependency_level (float): Minimum dependency level to include
        max_missions (int, optional): Limit number of missions for clarity
        
    Returns:
        Dict: Sankey diagram data structure with nodes and links
    """
    if not roadmap_data.missions:
        return {"nodes": [], "links": []}
    
    missions = list(roadmap_data.missions.keys())
    if max_missions:
        missions = missions[:max_missions]
    
    capabilities = roadmap_data.get_all_capabilities()
    
    if flow_type == "mission_to_capability":
        return _create_mission_capability_flow(roadmap_data, missions, capabilities, min_dependency_level)
    elif flow_type == "capability_to_readiness":
        return _create_capability_readiness_flow(roadmap_data, missions, capabilities, min_dependency_level)
    elif flow_type == "mission_to_readiness":
        return _create_mission_readiness_flow(roadmap_data, missions, capabilities, min_dependency_level)
    elif flow_type == "dependency_flow":
        return _create_dependency_flow(roadmap_data, missions, capabilities, min_dependency_level)
    else:
        raise ValueError(f"Unknown flow_type: {flow_type}")


def _create_mission_capability_flow(roadmap_data: RoadmapData, 
                                   missions: List[str], 
                                   capabilities: List[str],
                                   min_dependency_level: float) -> Dict:
    """Create Mission -> Capability flow."""
    nodes = []
    links = []
    
    # Create nodes
    mission_nodes = {mission: i for i, mission in enumerate(missions)}
    capability_nodes = {cap: i + len(missions) for i, cap in enumerate(capabilities)}
    
    # Add mission nodes
    for mission in missions:
        nodes.append({
            "label": f"Mission: {mission[:30]}{'...' if len(mission) > 30 else ''}",
            "color": PRIMARY_COLOR,
            "group": "mission"
        })
    
    # Add capability nodes  
    for capability in capabilities:
        nodes.append({
            "label": f"Capability: {capability}",
            "color": SECONDARY_COLOR,
            "group": "capability"
        })
    
    # Create links
    for mission in missions:
        mission_obj = roadmap_data.missions[mission]
        for capability, entry in mission_obj.capabilities.items():
            if capability in capabilities and entry.dependency_level is not None:
                if entry.dependency_level >= min_dependency_level:
                    links.append({
                        "source": mission_nodes[mission],
                        "target": capability_nodes[capability],
                        "value": entry.dependency_level,
                        "label": f"Dependency: {entry.dependency_level}"
                    })
    
    return {"nodes": nodes, "links": links}


def _create_capability_readiness_flow(roadmap_data: RoadmapData,
                                     missions: List[str],
                                     capabilities: List[str],
                                     min_dependency_level: float) -> Dict:
    """Create Capability -> Readiness Level flow."""
    nodes = []
    links = []
    
    # Collect unique readiness levels
    readiness_levels = set()
    for mission in missions:
        mission_obj = roadmap_data.missions[mission]
        for capability, entry in mission_obj.capabilities.items():
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
    
    for mission in missions:
        mission_obj = roadmap_data.missions[mission]
        for capability, entry in mission_obj.capabilities.items():
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


def _create_mission_readiness_flow(roadmap_data: RoadmapData,
                                  missions: List[str],
                                  capabilities: List[str],
                                  min_dependency_level: float) -> Dict:
    """Create Mission -> Capability -> Readiness Level flow."""
    nodes = []
    links = []
    
    # Collect unique readiness levels
    readiness_levels = set()
    for mission in missions:
        mission_obj = roadmap_data.missions[mission]
        for capability, entry in mission_obj.capabilities.items():
            if (capability in capabilities and 
                entry.dependency_level is not None and 
                entry.dependency_level >= min_dependency_level and
                entry.readiness_level is not None):
                readiness_levels.add(entry.readiness_level)
    
    readiness_levels = sorted(list(readiness_levels))
    
    # Create nodes with proper indexing
    mission_nodes = {mission: i for i, mission in enumerate(missions)}
    capability_nodes = {cap: i + len(missions) for i, cap in enumerate(capabilities)}
    readiness_nodes = {rl: i + len(missions) + len(capabilities) for i, rl in enumerate(readiness_levels)}
    
    # Add nodes
    for mission in missions:
        nodes.append({
            "label": f"Mission: {mission[:25]}{'...' if len(mission) > 25 else ''}",
            "color": PRIMARY_COLOR,
            "group": "mission"
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
    
    # Create Mission -> Capability links
    mission_capability_flows = defaultdict(lambda: defaultdict(float))
    
    for mission in missions:
        mission_obj = roadmap_data.missions[mission]
        for capability, entry in mission_obj.capabilities.items():
            if (capability in capabilities and 
                entry.dependency_level is not None and 
                entry.dependency_level >= min_dependency_level):
                mission_capability_flows[mission][capability] += entry.dependency_level
    
    for mission, capability_flows in mission_capability_flows.items():
        for capability, flow_value in capability_flows.items():
            links.append({
                "source": mission_nodes[mission],
                "target": capability_nodes[capability],
                "value": flow_value,
                "label": f"Dependency: {flow_value:.1f}"
            })
    
    # Create Capability -> Readiness links
    capability_readiness_flows = defaultdict(lambda: defaultdict(int))
    
    for mission in missions:
        mission_obj = roadmap_data.missions[mission]
        for capability, entry in mission_obj.capabilities.items():
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
                           missions: List[str],
                           capabilities: List[str],
                           min_dependency_level: float) -> Dict:
    """Create Dependency Level -> Capability -> Readiness Level flow."""
    nodes = []
    links = []
    
    # Collect unique dependency and readiness levels
    dependency_levels = set()
    readiness_levels = set()
    
    for mission in missions:
        mission_obj = roadmap_data.missions[mission]
        for capability, entry in mission_obj.capabilities.items():
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
    
    for mission in missions:
        mission_obj = roadmap_data.missions[mission]
        for capability, entry in mission_obj.capabilities.items():
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
               flow_type: str = "mission_to_capability",
               min_dependency_level: float = 0.0,
               max_missions: Optional[int] = None,
               title: Optional[str] = None,
               output_dir: Optional[str] = None,
               show_plot: bool = True) -> str:
    """
    Creates and saves a Sankey diagram for roadmap data.
    
    Args:
        roadmap_data (RoadmapData): The roadmap data to visualize
        flow_type (str): Type of flow to visualize
        min_dependency_level (float): Minimum dependency level to include
        max_missions (int, optional): Limit number of missions for clarity
        title (str, optional): Custom title for the plot
        output_dir (str, optional): Directory to save the plot
        show_plot (bool): Whether to display the plot in browser
        
    Returns:
        str: Path to the saved HTML file
    """
    if not roadmap_data.missions:
        print("❌ No roadmap data available to display.")
        return ""
    
    # Create Sankey data
    sankey_data = create_sankey_data(
        roadmap_data, 
        flow_type=flow_type,
        min_dependency_level=min_dependency_level,
        max_missions=max_missions
    )
    
    if not sankey_data["nodes"] or not sankey_data["links"]:
        print("❌ No data available for the specified criteria.")
        return ""
    
    # Set default title
    if title is None:
        title_map = {
            "mission_to_capability": "Mission to Capability Flow",
            "capability_to_readiness": "Capability to Readiness Flow", 
            "mission_to_readiness": "Mission → Capability → Readiness Flow",
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
                         max_missions: Optional[int] = 10,
                         output_dir: Optional[str] = None) -> List[str]:
    """
    Creates all types of Sankey diagrams for comprehensive analysis.
    
    Args:
        roadmap_data (RoadmapData): The roadmap data to visualize
        min_dependency_level (float): Minimum dependency level to include
        max_missions (int, optional): Limit number of missions for clarity
        output_dir (str, optional): Directory to save the plots
        
    Returns:
        List[str]: Paths to all saved HTML files
    """
    flow_types = [
        "mission_to_capability",
        "capability_to_readiness", 
        "mission_to_readiness",
        "dependency_flow"
    ]
    
    saved_files = []
    
    for flow_type in flow_types:
        try:
            output_path = plot_sankey(
                roadmap_data,
                flow_type=flow_type,
                min_dependency_level=min_dependency_level,
                max_missions=max_missions,
                output_dir=output_dir,
                show_plot=False
            )
            if output_path:
                saved_files.append(output_path)
        except Exception as e:
            print(f"❌ Error creating {flow_type} Sankey diagram: {e}")
    
    print(f"\n✅ Created {len(saved_files)} Sankey diagrams in {output_dir or 'default directory'}")
    return saved_files