from me_roadmap.visualization.text import (
    print_roadmap_sample, 
    print_full_roadmap, 
    print_roadmap_table, 
    print_roadmap_summary, 
    print_capabilities_analysis
)
from me_roadmap.visualization.heatmap import plot_heatmap
from me_roadmap.visualization.radar import plot_radar_charts
from me_roadmap.visualization.sankey import plot_sankey, plot_all_sankey_types
from me_roadmap.data_processing.combine import create_combined_roadmap
from me_roadmap.data_processing.models import RoadmapData
from typing import Dict, Tuple, Any
from argparse import ArgumentParser
from os import path
import click 

def main(dependency_filename: str = 'Roadmap-dependency.csv', 
         readiness_filename: str = 'Roadmap-readiness.csv',
         full_roadmap: bool = False,
         table_format: bool = False,
         summary: bool = False,
         capabilities: bool = False,
         heatmap: bool = False,
         radar: bool = False,
         sankey: bool = False,
         sankey_type: str = "use_case_to_capability") -> RoadmapData:
    """
    Main function to execute the roadmap combination process.

    Args:
        dependency_filename (str): Name of the dependency CSV file.
        readiness_filename (str): Name of the readiness CSV file.
        full_roadmap (bool): Whether to print the full roadmap.
        table_format (bool): Whether to print in table format.
        summary (bool): Whether to print summary information.
        capabilities (bool): Whether to print capabilities analysis.
        heatmap (bool): Whether to show a heatmap of roadmap dependency levels.
        radar (bool): Whether to show radar charts of roadmap use_cases and capabilities.
        sankey (bool): Whether to show Sankey diagrams of roadmap flows.
        sankey_type (str): Type of Sankey flow to visualize.

    Returns:
        RoadmapData: The combined roadmap data structure.
    """
    roadmap_data = create_combined_roadmap(dependency_filename, readiness_filename)

    if roadmap_data.use_cases:
        if summary:
            print_roadmap_summary(roadmap_data)
        elif capabilities:
            print_capabilities_analysis(roadmap_data)
        elif full_roadmap:
            print_full_roadmap(roadmap_data)
        elif table_format:
            print_roadmap_table(roadmap_data)
        elif heatmap:
            plot_heatmap(roadmap_data)
        elif radar:
            plot_radar_charts(roadmap_data)
        elif sankey:
            if sankey_type == "all":
                plot_all_sankey_types(roadmap_data, max_use_cases=10)
            else:
                plot_sankey(roadmap_data, flow_type=sankey_type, max_use_cases=10)
        else:
            print_roadmap_sample(roadmap_data)
    else:
        print("❌ Could not generate roadmap data. Please check the input files and error messages.")
    
    return roadmap_data


# TODO Change everything to use case instead of use_case.
@click.command()
@click.option('--dependency', type=click.Path(exists=True), required=True, help='Path to dependency CSV')
@click.option('--readiness', type=click.Path(exists=True), required=True, help='Path to readiness CSV')
@click.option('--full', is_flag=True, help='Print the full roadmap instead of a sample.')
@click.option('--table', is_flag=True, help='Print roadmap data in table format.')
@click.option('--summary', is_flag=True, help='Print a summary of the roadmap data.')
@click.option('--capabilities', is_flag=True, help='Print analysis of all capabilities.')
@click.option('--heatmap', is_flag=True, help='Show a heatmap of roadmap dependency levels.')
@click.option('--radar', is_flag=True, help='Show radar charts of roadmap use_cases and capabilities.')
@click.option('--sankey', is_flag=True, help='Show Sankey diagrams of roadmap flows.')
@click.option('--sankey-type', default='use_case_to_capability', 
              type=click.Choice(['use_case_to_capability', 'capability_to_readiness', 'use_case_to_readiness', 'dependency_flow', 'all']),
              help='Type of Sankey flow to visualize.')
def cli_main(dependency, readiness, full, table, summary, capabilities, heatmap, radar, sankey, sankey_type):
    roadmap_data = create_combined_roadmap(dependency, readiness)
    if heatmap:
        plot_heatmap(roadmap_data)
    if radar:
        plot_radar_charts(roadmap_data)
    if sankey:
        if sankey_type == "all":
            plot_all_sankey_types(roadmap_data, max_use_cases=10)
        else:
            plot_sankey(roadmap_data, flow_type=sankey_type, max_use_cases=10)
    main(dependency, readiness, full, table, summary, capabilities, heatmap, radar, sankey, sankey_type)


if __name__ == "__main__":
    cli_main()
