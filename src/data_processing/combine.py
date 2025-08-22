"""
Roadmap Data Combiner Module

This module provides functionality to combine dependency and readiness data from CSV files
into a unified data structure for analysis and visualization.
"""
from typing import Dict, Tuple, Any
import pandas as pd
from .models import RoadmapData


def load_csv_files(dependency_file: str, readiness_file: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Loads dependency and readiness CSV files into DataFrames.
    
    Args:
        dependency_file (str): The file path for the dependency CSV.
        readiness_file (str): The file path for the readiness CSV.
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Dependency and readiness DataFrames.
        
    Raises:
        FileNotFoundError: If either CSV file cannot be found.
        Exception: If there's an error reading the CSV files.
    """
    try:
        dependency_df = pd.read_csv(dependency_file, header=2, index_col=0)
        readiness_df = pd.read_csv(readiness_file, header=2, index_col=0)
        return dependency_df, readiness_df
    except FileNotFoundError as e:
        print(f"Error: {e}. Please make sure the CSV files are in the same directory as the script.")
        raise
    except Exception as e:
        print(f"An error occurred while reading the CSV files: {e}")
        raise


def clean_dataframes(dependency_df: pd.DataFrame, readiness_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Cleans the DataFrames by removing whitespace and empty rows/columns.
    
    Args:
        dependency_df (pd.DataFrame): The dependency DataFrame to clean.
        readiness_df (pd.DataFrame): The readiness DataFrame to clean.
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Cleaned dependency and readiness DataFrames.
    """
    dep_clean = dependency_df.copy()
    read_clean = readiness_df.copy()
    
    dep_clean.columns = dep_clean.columns.str.strip()
    read_clean.columns = read_clean.columns.str.strip()
    dep_clean.index = dep_clean.index.str.strip()
    read_clean.index = read_clean.index.str.strip()

    dep_clean.dropna(how='all', axis=0, inplace=True)
    dep_clean.dropna(how='all', axis=1, inplace=True)
    read_clean.dropna(how='all', axis=0, inplace=True)
    read_clean.dropna(how='all', axis=1, inplace=True)
    
    return dep_clean, read_clean


def align_dataframes(dependency_df: pd.DataFrame, readiness_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aligns DataFrames to have common missions and capabilities.
    
    Args:
        dependency_df (pd.DataFrame): The dependency DataFrame.
        readiness_df (pd.DataFrame): The readiness DataFrame.
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Aligned dependency and readiness DataFrames.
    """
    common_missions = dependency_df.columns.intersection(readiness_df.columns)
    common_capabilities = dependency_df.index.intersection(readiness_df.index)

    dep_aligned = dependency_df.loc[common_capabilities, common_missions]
    read_aligned = readiness_df.loc[common_capabilities, common_missions]
    
    return dep_aligned, read_aligned


def build_combined_structure(dependency_df: pd.DataFrame, readiness_df: pd.DataFrame) -> Dict[str, Dict[str, Tuple[Any, Any]]]:
    """
    Builds the combined data structure from aligned DataFrames.
    
    Args:
        dependency_df (pd.DataFrame): The aligned dependency DataFrame.
        readiness_df (pd.DataFrame): The aligned readiness DataFrame.
        
    Returns:
        Dict[str, Dict[str, Tuple[Any, Any]]]: Combined data structure.
                Structure: {mission: {capability: (dependency, readiness)}}
    """
    combined_data = {}
    
    for mission in dependency_df.columns:
        if pd.notna(mission) and mission:
            combined_data[mission] = {}
            for capability in dependency_df.index:
                if pd.notna(capability) and capability:
                    dependency_value = dependency_df.loc[capability, mission]
                    readiness_value = readiness_df.loc[capability, mission]
                    combined_data[mission][capability] = (dependency_value, readiness_value)

    return combined_data


def create_combined_roadmap(dependency_file: str, readiness_file: str) -> RoadmapData:
    """
    Orchestrates the complete process of loading, cleaning, aligning, and combining roadmap data.

    This function coordinates all the steps needed to transform CSV files into a unified
    data structure for analysis and visualization.

    Args:
        dependency_file (str): The file path for the dependency CSV.
        readiness_file (str): The file path for the readiness CSV.

    Returns:
        RoadmapData: A Pydantic model containing the combined roadmap data.
                    Returns empty RoadmapData if processing fails.
    """
    try:
        dependency_df, readiness_df = load_csv_files(dependency_file, readiness_file)
        dependency_df, readiness_df = clean_dataframes(dependency_df, readiness_df)
        dependency_df, readiness_df = align_dataframes(dependency_df, readiness_df)
        combined_dict = build_combined_structure(dependency_df, readiness_df)
        return RoadmapData.from_dict(combined_dict)
    except Exception:
        return RoadmapData(missions={})