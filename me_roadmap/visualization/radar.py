"""
Radar chart visualization for roadmap data.

This module provides a function to generate radar charts for missions and capabilities using matplotlib.
"""
import matplotlib.pyplot as plt
import numpy as np
import random
from me_roadmap.data_processing.models import RoadmapData
import os
from me_roadmap.visualization import PRIMARY_COLOR, SECONDARY_COLOR
import string

def plot_radar_charts(roadmap_data: RoadmapData, value_type: str = "dependency", missions_per_plot: int = 6, output_dir: str = None):
    """
    Plots radar charts for roadmap missions and capabilities.
    Each chart shows up to `missions_per_plot` missions.

    Args:
        roadmap_data (RoadmapData): The roadmap data to visualize.
        value_type (str): "dependency" or "readiness".
        missions_per_plot (int): Number of missions per radar chart.
        output_dir (str, optional): Directory to save the chart PNGs. Defaults to data/processed.
    """
    if not roadmap_data.missions:
        print("❌ No roadmap data available to display.")
        return

    capabilities = roadmap_data.get_all_capabilities()
    cap_labels = list(string.ascii_uppercase)[:len(capabilities)]
    cap_legend = {label: cap for label, cap in zip(cap_labels, capabilities)}
    missions = list(roadmap_data.missions.keys())
    num_plots = int(np.ceil(len(missions) / missions_per_plot))

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '../../data/processed/radar')
    os.makedirs(output_dir, exist_ok=True)

    def random_color():
        return "#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])

    for plot_idx in range(num_plots):
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))
        start = plot_idx * missions_per_plot
        end = min(start + missions_per_plot, len(missions))
        plot_missions = missions[start:end]

        angles = np.linspace(0, 2 * np.pi, len(capabilities), endpoint=False).tolist()
        angles += angles[:1]  # close the circle

        min_val = -0.1  # Set minimum value for all axes
        ax.set_ylim(min_val, None)

        for mission in plot_missions:
            values = []
            for cap in capabilities:
                entry = roadmap_data.missions[mission].capabilities.get(cap)
                if entry:
                    val = entry.dependency_level if value_type == "dependency" else entry.readiness_level
                    values.append(val if val is not None else 0)
                else:
                    values.append(0)
            values += values[:1]  # close the circle
            color = random_color()
            ax.plot(angles, values, label=mission, color=color, linewidth=2)
            ax.fill(angles, values, color=color, alpha=0.18)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(cap_labels, fontsize=12)
        ax.set_yticklabels([])
        ax.set_title(f"Roadmap {value_type.title()} Radar Chart ({start+1}-{end})", fontsize=16, pad=20)
        # Move legend below chart
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), fontsize=10, ncol=2, frameon=False)
        # Add capability legend as horizontal list below chart
        cap_legend_str = '   '.join([f"{label}: {name}" for label, name in cap_legend.items()])
        plt.figtext(0.5, 0.02, f"Capabilities: {cap_legend_str}", ha='center', va='bottom', fontsize=10, wrap=True)
        plt.tight_layout(rect=[0, 0.05, 1, 1])
        out_path = os.path.join(output_dir, f"roadmap_{value_type}_radar_{plot_idx+1}.png")
        plt.savefig(out_path)
        print(f"✅ Radar chart saved to {out_path}")
        plt.close(fig)
