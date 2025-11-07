import pandas as pd
import numpy as np
import re
import csv
from scipy.optimize import differential_evolution

# =============================================================================
# Configuration
# =============================================================================

# Define cost model to use
cost_models = [
    ("NA", 0),
    ("Case 1 - min dev critical - ", 1),
    ("Case 2 - min dev important- ", 2),
    ("Case 3 - min dev optional - ", 3),
    ("Case 4 - fastest critical - ", 4),
    ("Case 5 - fastest important- ", 5),
    ("Case 6 - fastest optional - ", 6),
]
active_model = 1
file_prefix = cost_models[active_model][0]
save_results = False

# =============================================================================
# Data Processing Functions
# =============================================================================

def clean_value(value):
    """
    Cleans a single value by extracting the leading number.
    If the value is a string, it extracts the number.
    If the value is NaN or cannot be converted, it returns NaN.
    """
    if isinstance(value, str):
        match = re.match(r"^\s*(\d+\.?\d*)\s*-", value)
        if match:
            return float(match.group(1))
    return 0  # np.nan

def load_and_merge_data(readiness_file, dependency_file):
    """
    Loads readiness and dependency data from CSV files, merges them,
    and returns the merged data along with lists of missions and capabilities.

    Args:
        readiness_file (str): Path to the readiness CSV file.
        dependency_file (str): Path to the dependency CSV file.

    Returns:
        tuple: A tuple containing:
            - dict: A dictionary of merged mission data.
            - list: A list of mission names.
            - list: A list of capability names.
    """
    # Load the datasets, skipping the first two rows
    df_readiness = pd.read_csv(readiness_file, header=2)
    df_dependency = pd.read_csv(dependency_file, header=2)

    # Set the first column as the index
    df_readiness.rename(columns={df_readiness.columns[0]: 'Capability'}, inplace=True)
    df_dependency.rename(columns={df_dependency.columns[0]: 'Capability'}, inplace=True)
    df_readiness.set_index('Capability', inplace=True)
    df_dependency.set_index('Capability', inplace=True)

    # Clean column names
    df_readiness.columns = df_readiness.columns.str.strip()
    df_dependency.columns = df_dependency.columns.str.strip()

    # Apply the cleaning function to all data cells
    for col in df_readiness.columns:
        df_readiness[col] = df_readiness[col].apply(clean_value)
    for col in df_dependency.columns:
        df_dependency[col] = df_dependency[col].apply(clean_value)

    # Get the list of missions and capabilities
    missions = df_readiness.columns.tolist()
    capabilities = df_readiness.index.tolist()

    # Create the merged data structure
    mission_data = {}
    for mission in missions:
        mission_data[mission] = []
        for capability in capabilities:
            readiness = df_readiness.loc[capability, mission]
            dependency = df_dependency.loc[capability, mission]
            mission_data[mission].append((readiness, dependency))

    return mission_data, missions, capabilities

def generate_simplified_csvs(mission_data, missions, capabilities):
    """
    Generates two simplified CSV files for readiness and dependency data.

    Args:
        mission_data (dict): Dictionary of mission data.
        missions (list): List of mission names.
        capabilities (list): List of capability names.
    """
    # --- Create simplified_readiness.csv ---
    with open('simplified_readiness.csv', 'w', newline='') as f_readiness:
        writer_readiness = csv.writer(f_readiness)
        # Write header row with capabilities
        writer_readiness.writerow([''] + capabilities)
        # Write data rows for each mission
        for mission in missions:
            readiness_data = [t[0] if pd.notna(t[0]) else '' for t in mission_data[mission]]
            writer_readiness.writerow([mission] + readiness_data)

    # --- Create simplified_dependency.csv ---
    with open('simplified_dependency.csv', 'w', newline='') as f_dependency:
        writer_dependency = csv.writer(f_dependency)
        # Write header row with capabilities
        writer_dependency.writerow([''] + capabilities)
        # Write data rows for each mission
        for mission in missions:
            dependency_data = [t[1] if pd.notna(t[1]) else '' for t in mission_data[mission]]
            writer_dependency.writerow([mission] + dependency_data)

# =============================================================================
# Optimization Functions
# =============================================================================

def cost_function(p_vector):
    """
    Cost function for mission optimization.

    Args:
        p_vector: Permutation vector representing mission order

    Returns:
        float: Total cost for this mission ordering
    """
    global save_results, active_model, file_prefix, missions, mission_data, capabilities

    if save_results:
        print(p_vector)

    # Get ordered mission data
    mission_order = [missions[ii] for ii in p_vector]
    mission_data_ordered = [mission_data[mm] for mm in mission_order]

    # Reward deferring all capability upgrades as much as possible
    readiness_so_far = [0 for rr, dd in mission_data_ordered[0]]
    cost = 0

    cost_matrix = []
    readiness_progression_matrix = []
    cost_progression_matrix = []
    upgrade_cost_matrix = []
    penalty_cost_matrix = []

    for idx, this_mission_data in enumerate(mission_data_ordered):
        this_readiness = [rr for rr, dd in this_mission_data]
        this_dependency = [dd for rr, dd in this_mission_data]

        if active_model in [1, 2, 3]:
            # Dependency is 0..1
            # 1 is mission critical
            # 0 is unneeded
            # Readiness is 0 to 13, 9 is operational

            # Assume there is a cost to use a critical dependency capability and move it to readiness 9
            # If dependency is 1, must pay price to go from existing readiness to level 9 or above

            if active_model == 1:
                dependency_threshold = 0.9  # must use if at or above this
            elif active_model == 2:
                dependency_threshold = 0.5  # must use if at or above this
            else:
                dependency_threshold = 0.2  # must use if at or above this

            if idx > 0:
                # Grab last readiness
                last_mission_readiness = readiness_progression_matrix[-1]
                last_upgrade = upgrade_cost_matrix[-1]
                last_penalty = penalty_cost_matrix[-1]
            else:
                # If nothing previously, assume not ready
                last_mission_readiness = [0 for rr in this_readiness]
                last_upgrade = [0 for rr in this_readiness]
                last_penalty = [0 for rr in this_readiness]

            # If dependent, force to at least a 9 readiness
            # Use highest of 9, the baseline readiness, or the established readiness
            # Else use the highest of the previous readiness or the current baseline readiness
            readiness_progression_matrix += [[max([lr, rr]) if dd < dependency_threshold else max([lr, rr, 9]) 
                                            for lr, rr, dd in zip(last_mission_readiness, this_readiness, this_dependency)]]

            # Calculate upgrade cost (difference between new and old readiness)
            upgrade_cost_matrix += [[max([0, nr - lr]) 
                                   for nr, lr in zip(readiness_progression_matrix[-1], last_mission_readiness)]]

            # Calculate time penalty (missions that had upgrades suffer time penalty)
            penalty_cost_matrix += [[lp if ((lp > 0) or (lu > 0)) else 0 
                                   for lp, lu in zip(last_penalty, last_upgrade)]]

            # Calculate upgrade cost plus time penalty
            this_cost = [uc + pc for uc, pc in zip(upgrade_cost_matrix[-1], penalty_cost_matrix[-1])]
            if save_results:
                print(this_cost)

            cost_progression_matrix += [this_cost]
            if save_results:
                print(cost_progression_matrix)
                print()

    # Save intermediate data if requested
    cost = sum([sum(cc) for cc in cost_progression_matrix])

    if save_results:
        # Create cost_matrix.csv
        with open(file_prefix + 'cost_matrix.csv', 'w', newline='') as this_f:
            this_writer = csv.writer(this_f)
            # Write header row with capabilities
            this_writer.writerow([''] + capabilities)
            # Write data rows for each mission
            for idx, mission in enumerate(mission_order):
                this_writer.writerow([mission] + cost_progression_matrix[idx])

        # Create capability_growth_matrix.csv
        with open(file_prefix + 'cap_growth_matrix.csv', 'w', newline='') as this_f:
            this_writer = csv.writer(this_f)
            # Write header row with capabilities
            this_writer.writerow([''] + capabilities)
            # Write data rows for each mission
            for idx, mission in enumerate(mission_order):
                this_writer.writerow([mission] + readiness_progression_matrix[idx])

    return cost

def cost_wrapper(float_vector):
    """
    Wrapper for the optimizer - converts float vector into integer permutation.

    Args:
        float_vector: Float array from optimizer

    Returns:
        float: Cost for this permutation
    """
    # The argsort() trick: get indices that would sort the array. This is a permutation.
    permutation = np.argsort(float_vector)
    return cost_function(permutation)

# =============================================================================
# Output Functions
# =============================================================================

def save_optimized_files(optimal_permutation, mission_data, missions, capabilities, file_prefix):
    """
    Save the optimized mission order to CSV files.

    Args:
        optimal_permutation: Optimized order of missions
        mission_data: Dictionary of mission data
        missions: List of mission names
        capabilities: List of capability names
        file_prefix: Prefix for output files
    """
    # Save optimized readiness file
    with open(file_prefix + 'optimized_readiness.csv', 'w', newline='') as f_readiness:
        writer_readiness = csv.writer(f_readiness)
        # Write header row with capabilities
        writer_readiness.writerow([''] + capabilities)
        # Write data rows for each mission
        for ii in optimal_permutation:
            mission = missions[ii]
            readiness_data = [t[0] if pd.notna(t[0]) else '' for t in mission_data[mission]]
            writer_readiness.writerow([mission] + readiness_data)

    # Save optimized dependency file
    with open(file_prefix + 'optimized_dependency.csv', 'w', newline='') as f_dependency:
        writer_dependency = csv.writer(f_dependency)
        # Write header row with capabilities
        writer_dependency.writerow([''] + capabilities)
        # Write data rows for each mission
        for ii in optimal_permutation:
            mission = missions[ii]
            print(f"Processing mission: {mission}")
            dependency_data = [t[1] if pd.notna(t[1]) else '' for t in mission_data[mission]]
            writer_dependency.writerow([mission] + dependency_data)

# =============================================================================
# Main Execution
# =============================================================================

def main():
    """
    Main function to run the complete mission optimization process.
    """
    global mission_data, missions, capabilities, save_results

    try:
        print("Loading and processing data...")
        # Load and process the data from the original CSV files
        mission_data, missions, capabilities = load_and_merge_data('Roadmap-readiness.csv', 'Roadmap-dependency.csv')

        print("Generating simplified CSV files...")
        # Generate the new simplified CSV files
        generate_simplified_csvs(mission_data, missions, capabilities)
        print("Successfully generated 'simplified_readiness.csv' and 'simplified_dependency.csv'")

        print("\nOptimizing mission order...")
        # Differential Evolution Solver
        vector_length = len(missions)  # Use actual number of missions

        # Define bounds for the N-dimensional search space. [0, 1] for each dimension is fine.
        bounds = [(0, 1)] * vector_length

        # Run the optimizer
        result = differential_evolution(cost_wrapper, bounds, strategy='best1bin', popsize=5, mutation=(0.5, 1.5))

        # Get the final answer - convert the best float vector into our final permutation
        optimal_permutation = np.argsort(result.x)

        print(f"Optimal Vector Found: {optimal_permutation}")
        print(f"Minimum Cost Found: {result.fun}")

        print("\nSaving results...")
        # Run again to save the right permutation
        save_results = True
        cost_function(optimal_permutation)

        # Save the optimized files
        save_optimized_files(optimal_permutation, mission_data, missions, capabilities, file_prefix)

        print("\nOptimization complete!")
        print(f"Results saved with prefix: '{file_prefix}'")

    except FileNotFoundError as e:
        print(f"Error: Make sure 'Roadmap-readiness.csv' and 'Roadmap-dependency.csv' are in the same directory as the script.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
