"""
Heatmap visualizations for roadmap data.

This module provides functions to generate heatmaps for dependency and readiness values
across missions and capabilities.
"""
from matplotlib.colors import LinearSegmentedColormap
from me_roadmap.data_processing.models import RoadmapData
import matplotlib.pyplot as plt
from typing import Optional
import numpy as np
import os

from matplotlib.colors import LinearSegmentedColormap

def plot_heatmap(roadmap_data: RoadmapData, value_type: str = "dependency", mission_keys: Optional[list] = None, capability_keys: Optional[list] = None, cmap: str = "YlOrRd"):
    """
    Plots a heatmap for the given value type ("dependency" or "readiness") across missions and capabilities.

    Args:
        roadmap_data (RoadmapData): The roadmap data to visualize.
        value_type (str): "dependency" or "readiness".
        mission_keys (list, optional): List of missions to include. If None, use all.
        capability_keys (list, optional): List of capabilities to include. If None, use all.
        cmap (str): Matplotlib colormap name.
    """
    if not roadmap_data.missions:
        print("❌ No roadmap data available to display.")
        return

    # Select missions and capabilities
    missions = mission_keys if mission_keys else list(roadmap_data.missions.keys())
    capabilities = capability_keys if capability_keys else roadmap_data.get_all_capabilities()

    # Build the matrix
    matrix = []
    for capability in capabilities:
        row = []
        for mission in missions:
            entry = roadmap_data.missions[mission].capabilities.get(capability)
            if entry:
                if value_type == "dependency":
                    val = entry.dependency_level
                else:
                    val = entry.readiness_level
                row.append(val if val is not None else np.nan)
            else:
                row.append(np.nan)
        matrix.append(row)
    matrix = np.array(matrix)

    # Plot
    # Calculate figure size for better aspect ratio
    min_width, min_height = 12, 8
    width = max(min_width, len(missions) * 1.2)
    height = max(min_height, len(capabilities) * 0.7)
    fig, ax = plt.subplots(figsize=(width, height))
    custom_cmap = LinearSegmentedColormap.from_list(
        "custom_gradient", ["#b8d232", "#231f20"], N=256
    )
    im = ax.imshow(matrix, aspect="auto", cmap=custom_cmap, interpolation="nearest")
    cbar = fig.colorbar(im, ax=ax, label=f"{value_type.title()} Level")

    ax.set_xticks(np.arange(len(missions)))
    ax.set_xticklabels(missions, rotation=45, ha="right", fontsize=14)
    ax.set_yticks(np.arange(len(capabilities)))
    ax.set_yticklabels(capabilities, fontsize=14)
    ax.set_title(f"Roadmap {value_type.title()} Heatmap", fontsize=18, pad=20)
    
    fig.subplots_adjust(bottom=0.25, left=0.25)
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    output_dir = os.path.join(os.path.dirname(__file__), '../../data/processed')
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"roadmap_{value_type}_heatmap.png")
    fig.savefig(out_path, bbox_inches="tight")
    print(f"✅ Heatmap saved to {out_path}")
    plt.close(fig)
