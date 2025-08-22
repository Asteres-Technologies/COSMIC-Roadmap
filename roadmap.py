from src.visualization.text import (
    print_roadmap_sample, 
    print_full_roadmap, 
    print_roadmap_table, 
    print_roadmap_summary, 
    print_capabilities_analysis
)
from src.data_processing.combine import create_combined_roadmap
from src.data_processing.models import RoadmapData
from typing import Dict, Tuple, Any
from argparse import ArgumentParser
from os import path

def main(dependency_filename: str = 'Roadmap-dependency.csv', 
         readiness_filename: str = 'Roadmap-readiness.csv',
         full_roadmap: bool = False,
         table_format: bool = False,
         summary: bool = False,
         capabilities: bool = False) -> RoadmapData:
    """
    Main function to execute the roadmap combination process.

    Args:
        dependency_filename (str): Name of the dependency CSV file.
        readiness_filename (str): Name of the readiness CSV file.
        full_roadmap (bool): Whether to print the full roadmap.
        table_format (bool): Whether to print in table format.
        summary (bool): Whether to print summary information.
        capabilities (bool): Whether to print capabilities analysis.

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
        else:
            print_roadmap_sample(roadmap_data)
    else:
        print("❌ Could not generate roadmap data. Please check the input files and error messages.")
    
    return roadmap_data


if __name__ == "__main__":
    # Define the names of your input files.
    default_dependency = './data/raw/Roadmap-dependency.csv'
    default_readiness = './data/raw/Roadmap-readiness.csv'
    parser = ArgumentParser(description="Combine and visualize roadmap dependency and readiness data.")
    parser.add_argument("--dependency", default=default_dependency, help="Path to the dependency CSV file.")
    parser.add_argument("--readiness", default=default_readiness, help="Path to the readiness CSV file.")
    parser.add_argument("--full", action="store_true", help="Print the full roadmap instead of a sample.")
    parser.add_argument("--table", action="store_true", help="Print roadmap data in table format.")
    parser.add_argument("--summary", action="store_true", help="Print a summary of the roadmap data.")
    parser.add_argument("--capabilities", action="store_true", help="Print analysis of all capabilities.")
    args = parser.parse_args()

    main(args.dependency, args.readiness, args.full, args.table, args.summary, args.capabilities)
