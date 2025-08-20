"""
Roadmap Data Combiner Module

This module provides functionality to combine dependency and readiness data from CSV files
into a unified data structure for analysis and visualization.
"""
import pandas as pd
import pprint
from typing import Dict, Tuple, Any, Optional


def create_combined_roadmap(dependency_file: str, readiness_file: str) -> Dict[str, Dict[str, Tuple[Any, Any]]]:
    """
    Loads dependency and readiness data from CSV files and combines them into a
    nested dictionary structure.

    The function reads two CSV files, cleans the data by removing empty rows/columns
    and stripping whitespace, and then aligns the data based on common missions
    and capabilities.

    Args:
        dependency_file (str): The file path for the dependency CSV.
        readiness_file (str): The file path for the readiness CSV.

    Returns:
        dict: A nested dictionary with the combined data.
              The structure is: {mission: {capability: (dependency, readiness)}}
    """
    try:
        # Load the datasets. The actual headers (mission names) are in the 3rd row (index 2).
        # The first column (index 0) contains the capabilities and is used as the DataFrame index.
        dependency_df = pd.read_csv(dependency_file, header=2, index_col=0)
        readiness_df = pd.read_csv(readiness_file, header=2, index_col=0)
    except FileNotFoundError as e:
        print(f"Error: {e}. Please make sure the CSV files are in the same directory as the script.")
        return {}
    except Exception as e:
        print(f"An error occurred while reading the CSV files: {e}")
        return {}

    # --- Data Cleaning ---
    # Strip any leading/trailing whitespace from mission names (columns) and capability names (index).
    dependency_df.columns = dependency_df.columns.str.strip()
    readiness_df.columns = readiness_df.columns.str.strip()
    dependency_df.index = dependency_df.index.str.strip()
    readiness_df.index = readiness_df.index.str.strip()

    # Drop any rows or columns that are completely empty (contain only NaN values).
    dependency_df.dropna(how='all', axis=0, inplace=True)
    dependency_df.dropna(how='all', axis=1, inplace=True)
    readiness_df.dropna(how='all', axis=0, inplace=True)
    readiness_df.dropna(how='all', axis=1, inplace=True)

    # --- Data Alignment ---
    # Find the common missions and capabilities between the two files to ensure alignment.
    common_missions = dependency_df.columns.intersection(readiness_df.columns)
    common_capabilities = dependency_df.index.intersection(readiness_df.index)

    # Filter both DataFrames to only include the common missions and capabilities.
    dependency_df = dependency_df.loc[common_capabilities, common_missions]
    readiness_df = readiness_df.loc[common_capabilities, common_missions]

    # --- Build the Combined Data Structure ---
    combined_data = {}
    for mission in common_missions:
        # Ensure the mission name is valid before adding it to the dictionary.
        if pd.notna(mission) and mission:
            combined_data[mission] = {}
            for capability in common_capabilities:
                # Ensure the capability name is valid.
                if pd.notna(capability) and capability:
                    dependency_value = dependency_df.loc[capability, mission]
                    readiness_value = readiness_df.loc[capability, mission]
                    combined_data[mission][capability] = (dependency_value, readiness_value)

    return combined_data


def print_roadmap_sample(roadmap_data: Dict[str, Dict[str, Tuple[Any, Any]]], 
                        mission_key: Optional[str] = None) -> None:
    """
    Pretty-prints a sample of the roadmap data for verification purposes.

    Args:
        roadmap_data (dict): The combined roadmap data structure.
        mission_key (str, optional): Specific mission to print. If None, prints the first mission.
    """
    if not roadmap_data:
        print("No roadmap data available to display.")
        return

    if mission_key is None:
        mission_key = list(roadmap_data.keys())[0]
    
    if mission_key not in roadmap_data:
        print(f"Mission '{mission_key}' not found in roadmap data.")
        return

    print("--- Combined Roadmap Data (Sample) ---")
    print(f"\nData for Mission: '{mission_key}'")
    pprint.pprint(roadmap_data[mission_key])


def print_full_roadmap(roadmap_data: Dict[str, Dict[str, Tuple[Any, Any]]]) -> None:
    """
    Pretty-prints the entire roadmap data structure.

    Args:
        roadmap_data (dict): The combined roadmap data structure.
    """
    if not roadmap_data:
        print("No roadmap data available to display.")
        return

    print("--- Full Combined Roadmap Data ---")
    pprint.pprint(roadmap_data)


def main(dependency_filename: str = 'Roadmap-dependency.csv', 
         readiness_filename: str = 'Roadmap-readiness.csv') -> Dict[str, Dict[str, Tuple[Any, Any]]]:
    """
    Main function to execute the roadmap combination process.

    Args:
        dependency_filename (str): Name of the dependency CSV file.
        readiness_filename (str): Name of the readiness CSV file.

    Returns:
        dict: The combined roadmap data structure.
    """
    # Generate the combined data structure.
    roadmap_data = create_combined_roadmap(dependency_filename, readiness_filename)

    # --- Verification ---
    # Pretty-print the data for the first mission as a sample to verify the output.
    if roadmap_data:
        print_roadmap_sample(roadmap_data)
        
        # To print the entire dictionary, you can uncomment the following line:
        # print_full_roadmap(roadmap_data)
    else:
        print("Could not generate roadmap data. Please check the input files and error messages.")
    
    return roadmap_data


if __name__ == "__main__":
    # Define the names of your input files.
    dependency_filename = 'Roadmap-dependency.csv'
    readiness_filename = 'Roadmap-readiness.csv'
    
    main(dependency_filename, readiness_filename)
