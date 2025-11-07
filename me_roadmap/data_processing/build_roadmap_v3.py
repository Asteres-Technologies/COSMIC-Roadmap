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
    and returns the merged data along with lists of use_cases and capabilities.

    Args:
        readiness_file (str): Path to the readiness CSV file.
        dependency_file (str): Path to the dependency CSV file.

    Returns:
        tuple: A tuple containing:
            - dict: A dictionary of merged use_case data.
            - list: A list of use_case names.
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

    # Get the list of use_cases and capabilities
    use_cases = df_readiness.columns.tolist()
    capabilities = df_readiness.index.tolist()

    # Create the merged data structure
    use_case_data = {}
    for use_case in use_cases:
        use_case_data[use_case] = []
        for capability in capabilities:
            readiness = df_readiness.loc[capability, use_case]
            dependency = df_dependency.loc[capability, use_case]
            use_case_data[use_case].append((readiness, dependency))

    return use_case_data, use_cases, capabilities

def generate_simplified_csvs(use_case_data, use_cases, capabilities):
    """
    Generates two simplified CSV files for readiness and dependency data.

    Args:
        use_case_data (dict): Dictionary of use_case data.
        use_cases (list): List of use_case names.
        capabilities (list): List of capability names.
    """
    # --- Create simplified_readiness.csv ---
    with open('simplified_readiness.csv', 'w', newline='') as f_readiness:
        writer_readiness = csv.writer(f_readiness)
        # Write header row with capabilities
        writer_readiness.writerow([''] + capabilities)
        # Write data rows for each use_case
        for use_case in use_cases:
            readiness_data = [t[0] if pd.notna(t[0]) else '' for t in use_case_data[use_case]]
            writer_readiness.writerow([use_case] + readiness_data)

    # --- Create simplified_dependency.csv ---
    with open('simplified_dependency.csv', 'w', newline='') as f_dependency:
        writer_dependency = csv.writer(f_dependency)
        # Write header row with capabilities
        writer_dependency.writerow([''] + capabilities)
        # Write data rows for each use_case
        for use_case in use_cases:
            dependency_data = [t[1] if pd.notna(t[1]) else '' for t in use_case_data[use_case]]
            writer_dependency.writerow([use_case] + dependency_data)

# =============================================================================
# Optimization Functions
# =============================================================================

def cost_function(p_vector):
    """
    Cost function for use_case optimization.

    Args:
        p_vector: Permutation vector representing use_case order

    Returns:
        float: Total cost for this use_case ordering
    """
    global save_results, active_model, file_prefix, use_cases, use_case_data, capabilities

    if save_results:
        print(p_vector)

    # Get ordered use_case data
    use_case_order = [use_cases[ii] for ii in p_vector]
    use_case_data_ordered = [use_case_data[mm] for mm in use_case_order]

    # Reward deferring all capability upgrades as much as possible
    readiness_so_far = [0 for rr, dd in use_case_data_ordered[0]]
    cost = 0

    cost_matrix = []
    readiness_progression_matrix = []
    cost_progression_matrix = []
    upgrade_cost_matrix = []
    penalty_cost_matrix = []

    for idx, this_use_case_data in enumerate(use_case_data_ordered):
        this_readiness = [rr for rr, dd in this_use_case_data]
        this_dependency = [dd for rr, dd in this_use_case_data]

        if active_model in [1, 2, 3]:
            # Dependency is 0..1
            # 1 is use_case critical
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
                last_use_case_readiness = readiness_progression_matrix[-1]
                last_upgrade = upgrade_cost_matrix[-1]
                last_penalty = penalty_cost_matrix[-1]
            else:
                # If nothing previously, assume not ready
                last_use_case_readiness = [0 for rr in this_readiness]
                last_upgrade = [0 for rr in this_readiness]
                last_penalty = [0 for rr in this_readiness]

            # If dependent, force to at least a 9 readiness
            # Use highest of 9, the baseline readiness, or the established readiness
            # Else use the highest of the previous readiness or the current baseline readiness
            readiness_progression_matrix += [[max([lr, rr]) if dd < dependency_threshold else max([lr, rr, 9]) 
                                            for lr, rr, dd in zip(last_use_case_readiness, this_readiness, this_dependency)]]

            # Calculate upgrade cost (difference between new and old readiness)
            upgrade_cost_matrix += [[max([0, nr - lr]) 
                                   for nr, lr in zip(readiness_progression_matrix[-1], last_use_case_readiness)]]

            # Calculate time penalty (use_cases that had upgrades suffer time penalty)
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
            # Write data rows for each use_case
            for idx, use_case in enumerate(use_case_order):
                this_writer.writerow([use_case] + cost_progression_matrix[idx])

        # Create capability_growth_matrix.csv
        with open(file_prefix + 'cap_growth_matrix.csv', 'w', newline='') as this_f:
            this_writer = csv.writer(this_f)
            # Write header row with capabilities
            this_writer.writerow([''] + capabilities)
            # Write data rows for each use_case
            for idx, use_case in enumerate(use_case_order):
                this_writer.writerow([use_case] + readiness_progression_matrix[idx])

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

def save_optimized_files(optimal_permutation, use_case_data, use_cases, capabilities, file_prefix):
    """
    Save the optimized use_case order to CSV files.

    Args:
        optimal_permutation: Optimized order of use_cases
        use_case_data: Dictionary of use_case data
        use_cases: List of use_case names
        capabilities: List of capability names
        file_prefix: Prefix for output files
    """
    # Save optimized readiness file
    with open(file_prefix + 'optimized_readiness.csv', 'w', newline='') as f_readiness:
        writer_readiness = csv.writer(f_readiness)
        # Write header row with capabilities
        writer_readiness.writerow([''] + capabilities)
        # Write data rows for each use_case
        for ii in optimal_permutation:
            use_case = use_cases[ii]
            readiness_data = [t[0] if pd.notna(t[0]) else '' for t in use_case_data[use_case]]
            writer_readiness.writerow([use_case] + readiness_data)

    # Save optimized dependency file
    with open(file_prefix + 'optimized_dependency.csv', 'w', newline='') as f_dependency:
        writer_dependency = csv.writer(f_dependency)
        # Write header row with capabilities
        writer_dependency.writerow([''] + capabilities)
        # Write data rows for each use_case
        for ii in optimal_permutation:
            use_case = use_cases[ii]
            print(f"Processing use_case: {use_case}")
            dependency_data = [t[1] if pd.notna(t[1]) else '' for t in use_case_data[use_case]]
            writer_dependency.writerow([use_case] + dependency_data)

# =============================================================================
# Main Execution
# =============================================================================

def main():
    """
    Main function to run the complete use_case optimization process.
    """
    global use_case_data, use_cases, capabilities, save_results

    try:
        print("Loading and processing data...")
        # Load and process the data from the original CSV files
        use_case_data, use_cases, capabilities = load_and_merge_data('Roadmap-readiness.csv', 'Roadmap-dependency.csv')

        print("Generating simplified CSV files...")
        # Generate the new simplified CSV files
        generate_simplified_csvs(use_case_data, use_cases, capabilities)
        print("Successfully generated 'simplified_readiness.csv' and 'simplified_dependency.csv'")

        print("\nOptimizing use_case order...")
        # Differential Evolution Solver
        vector_length = len(use_cases)  # Use actual number of use_cases

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
        save_optimized_files(optimal_permutation, use_case_data, use_cases, capabilities, file_prefix)

        print("\nOptimization complete!")
        print(f"Results saved with prefix: '{file_prefix}'")

    except FileNotFoundError as e:
        print(f"Error: Make sure 'Roadmap-readiness.csv' and 'Roadmap-dependency.csv' are in the same directory as the script.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
