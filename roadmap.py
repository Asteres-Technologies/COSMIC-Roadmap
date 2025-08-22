from me_roadmap.visualization.text import (
    print_roadmap_sample, 
    print_full_roadmap, 
    print_roadmap_table, 
    print_roadmap_summary, 
    print_capabilities_analysis
)
from me_roadmap.visualization.heatmap import plot_heatmap
from me_roadmap.visualization.radar import plot_radar_charts
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
         radar: bool = False) -> RoadmapData:
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
        radar (bool): Whether to show radar charts of roadmap missions and capabilities.

    Returns:
        RoadmapData: The combined roadmap data structure.
    """
    roadmap_data = create_combined_roadmap(dependency_filename, readiness_filename)

    if roadmap_data.missions:
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
        else:
            print_roadmap_sample(roadmap_data)
    else:
        print("❌ Could not generate roadmap data. Please check the input files and error messages.")
    
    return roadmap_data


@click.command()
@click.option('--dependency', type=click.Path(exists=True), required=True, help='Path to dependency CSV')
@click.option('--readiness', type=click.Path(exists=True), required=True, help='Path to readiness CSV')
@click.option('--full', is_flag=True, help='Print the full roadmap instead of a sample.')
@click.option('--table', is_flag=True, help='Print roadmap data in table format.')
@click.option('--summary', is_flag=True, help='Print a summary of the roadmap data.')
@click.option('--capabilities', is_flag=True, help='Print analysis of all capabilities.')
@click.option('--heatmap', is_flag=True, help='Show a heatmap of roadmap dependency levels.')
@click.option('--radar', is_flag=True, help='Show radar charts of roadmap missions and capabilities.')
@click.option('--stackedbar', is_flag=True, help='Generate stacked bar chart visualization')
def cli_main(dependency, readiness, full, table, summary, capabilities, heatmap, radar):
    roadmap_data = create_combined_roadmap(dependency, readiness)
    if heatmap:
        plot_heatmap(roadmap_data)
    if radar:
        plot_radar_charts(roadmap_data)
    main(dependency, readiness, full, table, summary, capabilities, heatmap, radar)
    main(dependency, readiness, full, table, summary, capabilities, heatmap, radar)


if __name__ == "__main__":
    cli_main()
