from pathlib import Path
import pandas as pd
import numpy as np
import time
from collections import defaultdict
from .constraint_evaluation import constraint_evaluation
from .constraint_evaluation_other import constraint_evaluation_other
from .operators import operators
import os
from functools import lru_cache
import hashlib
import json
from pandas.errors import EmptyDataError

def _resolve_cache_dir() -> Path:
    # Prefer explicit CACHE_DIR; else fall back to OUTPUT_DIR/cache; else ./output/cache
    base = os.getenv("CACHE_DIR")
    if base:
        p = Path(base)
    p = p.resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p

CACHE_DIR = _resolve_cache_dir()


def make_cache_key(dataName, dataSize, bucket, branch, conditions, operators):
    """Create a unique hash for given run configuration."""
    import hashlib
    key_str = json.dumps({
        "dataName": dataName,
        "dataSize": dataSize,
        "bucket": bucket,
        "branch": branch,
        "conditions": conditions,
        "operators": operators
    }, sort_keys=True)
    return hashlib.sha256(key_str.encode()).hexdigest()


class filtered_fully:
    def __init__(self):
        self.applyOperator = operators()

    def check_predicates(self, sorted_possible_refinements, statistical_tree, expression, datasize, dataName, result_num, query_num, const_num, constraint, predicates, combination, outputDirectory,  bucket, branch):
        counter, i = 0, 0
        agg_counter = 0
        satisfied_conditions = []
        check_counter_Not = 0
        check_counter = 0
        refinement_counter = 0
        solutions_count = 0
        end_time = 0
        checked_num = 0
        accesses_num = 0
        refinement_num = 0

        # Create dictionaries for parent-child relationships and cluster info
        parent_child_map = defaultdict(list)
        cluster_map = {}

        for row in statistical_tree:
            parent_key = (row['Parent level'], row['Parent cluster'])
            child_key = (row['Level'], row['Cluster Id'])
            parent_child_map[parent_key].append(child_key) 
            cluster_map[child_key] = row  

        # Find the root clusters (clusters with Parent level 0)
        root_clusters = [(row['Level'], row['Cluster Id']) for row in statistical_tree if row['Parent level'] == 0]

        start_time = time.time()
        
        for refinement in sorted_possible_refinements:
            # Loop over each condition in the refinement dictionary   
            conditions = []
            operators = []
            for ref in refinement['refinements']:
                conditions.append(ref['value'])
                operators.append(ref['operator'])

            #print(conditions)
            cache_key = make_cache_key(dataName, datasize, bucket, branch, conditions, operators)
            cache_file =  CACHE_DIR / f"filtered_clusters_{cache_key}.csv" 
            similarity = refinement['distance']

            filtered_clusters = []   
            cached_df = None
            if os.path.exists(cache_file):
                try:
                    cached_df = pd.read_csv(cache_file)
                except EmptyDataError:
                    # Corrupt/empty cache file — treat as miss and recompute
                    cached_df = None

            if cached_df is not None:
                # Rebuild from IDs
                for _, row in cached_df.iterrows():
                    key = (int(row["Level"]), int(row["Cluster Id"]))
                    if key in cluster_map:
                        filtered_clusters.append(cluster_map[key])
                counter += len(filtered_clusters)
            else:   
                filtered_clusters = []    
                for root_key in root_clusters:
                    filtered_clusters, counter = self.filter_clusters_Hash(root_key, cluster_map, conditions, operators, filtered_clusters, counter, parent_child_map)
                
                    # Convert the filtered clusters to a DataFrame and save to CSV
                filtered_df_to_cache = pd.DataFrame([
                        {"Level": c['Level'], "Cluster Id": c['Cluster Id']}
                        for c in filtered_clusters
                    ])
                filtered_df_to_cache.to_csv(cache_file, index=False)
            filtered_df = pd.DataFrame(filtered_clusters)
            # Evaluate and store the results
            check_counter += 1
            if check_counter % 1000 == 0:
                print(f"Checked {check_counter} refinements in {time.time() - start_time:.2f} sec")

            #satisfied, agg_counter = evaluate_constraint.cardinality(filtered_df, counter, agg_counter, condition1, condition2)
            if dataName == "TPCH":
                evaluate_constraint = constraint_evaluation_other() 
            else:
                evaluate_constraint = constraint_evaluation() 
            
            satisfied, agg_counter, Not_satisfied, result = evaluate_constraint.evaluate_constraint1(filtered_df, expression, conditions, agg_counter, similarity, "full")

            if satisfied != []:
                #check_counter_satisfy += 1
                refinement_counter += 1
                satisfied_conditions.append(satisfied)
                solutions_count +=1


                if len(satisfied_conditions) == result_num:
                    end_time = time.time() 
                    checked_num = check_counter
                    accesses_num = counter
                    refinement_num = refinement_counter 
                    break
        
        if end_time == 0: #no solutions
            end_time = time.time()
            checked_num = check_counter
            accesses_num = counter
            refinement_num = refinement_counter
                    
        self.print_results(satisfied_conditions, start_time, end_time, dataName, datasize, query_num, const_num, combination, 
                accesses_num, solutions_count, checked_num, check_counter_Not, refinement_num, constraint, predicates, result_num, outputDirectory)
            


    def print_results(self, satisfied_conditions, start_time, end_time, dataName, datasize, query_num, const_num, combination, 
        counter, solutions_count, check_counter, check_counter_Not, refinement_counter, constraint, predicates, result_num, outputDirectory):
                    
        '''
        directory = '/Users/Shatha/Downloads/Query_Refinment_Shatha/running_files'
        filename = f'filtered_fully_{conditions}.csv'
        filename = filename.replace(" ", "_").replace(",", "_")
        # Save to CSV
        # Join the directory and file name to create the full path
        full_path = os.path.join(directory, filename)
        filtered_df.to_csv(full_path, index=False)
        '''
        # Save satisfied conditions to CSV
        satisfied_conditions_df = pd.DataFrame(satisfied_conditions)
        output_directory = outputDirectory
        # For the second file
        file_path_2 = os.path.join(
            output_directory, 
            f"satisfied_conditions_Fully_{dataName}_size{datasize}_query{query_num}_constraint{constraint}.csv"
        )
        satisfied_conditions_df.to_csv(file_path_2, index=False)

        elapsed_time = end_time - start_time

        info = []
        refinement_info = {
            "Data Name": dataName,
            "Data Size": datasize,
            "Query Num": query_num,
            "Constraint Num": const_num,
            "Type": "Fully",
            "Top-K": result_num,
            "Combinations Num": combination,
            "Distance": round((check_counter) / combination * 100, 3),
            "Access Num": counter,
            "Checked Num": (check_counter),
            "Refinement Num": refinement_counter,
            "Time": round(elapsed_time, 3),
            "Constraint Width": round(constraint[1]-constraint[0], 2),
            "Solutions Count": solutions_count,
            "Constraint": constraint, 
            #"Distribution": distribution,
            #"Correlation": Correlation,
            "Query": predicates,
            "Range Evaluation Time": " ",
            "Division Time": " ",
            "Single Time": " ",
            "Processing Time": " "
        }
        info.append(refinement_info)
        info_df = pd.DataFrame(info)
        output_directory = outputDirectory
        # Ensure the directory exists
        os.makedirs(output_directory, exist_ok=True)

        # Define the full file path including the directory
        file_path = os.path.join(output_directory, f"Run_info_{dataName}_size{datasize}_constraint{const_num}.csv")

        write_header = not os.path.exists(file_path)  # Write header only if the file does not exist

        # Write to CSV with appropriate header setting
        info_df.to_csv(file_path, mode='a', index=False, header=write_header)

        print("\nTop-", result_num," :")
        print("Number of boxes access: ", counter)
        print("Number of checked", check_counter)
        #print("Checked No.-Not:", check_counter_Not)
        #print("Checked No.-Satisfy:", check_counter_satisfy)
        print("Number of refinments", refinement_counter)
        print("Time taken Overall:", round(elapsed_time, 3), "seconds")  


    def filter_clusters_Hash(self, current_key, cluster_map, conditions, operators, filtered_clusters, 
    counter, parent_child_map):
    
        stack = [current_key]

        while stack:
            counter += 1
            current_key = stack.pop()
            current_cluster = cluster_map[current_key]

            # Initialize a flag to track if the current cluster satisfies all conditions
            fully_satisfies = True

            # Loop through each condition and operator
            for idx, (condition, operator) in enumerate(zip(conditions, operators)):
                data_min = current_cluster['Data_Min'][idx]  # Get the corresponding Data_Min value for this condition
                data_max = current_cluster['Data_Max'][idx]  # Get the corresponding Data_Max value for this condition
                

                # If any condition is not satisfied, mark as False and break
                if not self.applyOperator.apply_operator(data_min, data_max, condition, operator, "Full"):
                    fully_satisfies = False
                    break

            # If all conditions are satisfied, mark the cluster as "Full"
            if fully_satisfies:
                current_cluster['Satisfy'] = 'Full'
                filtered_clusters.append(current_cluster)

            else:  # Otherwise, check the child clusters
                stack.extend(parent_child_map.get(current_key, []))

        return filtered_clusters, counter
    
    def filter_clusters_Hash1(self, current_key, cluster_map, condition1, condition1_operator, condition2, condition2_operator, condition3, condition3_operator, filtered_clusters, counter, parent_child_map):

        stack = [current_key]

        while stack:
            counter += 1
            current_key = stack.pop()
            current_cluster = cluster_map[current_key]

            if (self.applyOperator.apply_operator(current_cluster['Data_Min'][0], current_cluster['Data_Max'][0], condition1, condition1_operator, "Full") and 
                self.applyOperator.apply_operator(current_cluster['Data_Min'][1], current_cluster['Data_Max'][1], condition2, condition2_operator, "Full") and 
                self.applyOperator.apply_operator(current_cluster['Data_Min'][2], current_cluster['Data_Max'][2], condition3, condition3_operator, "Full")):
                current_cluster['Satisfy'] = 'Full'
                filtered_clusters.append(current_cluster)

                
            else: # Otherwise, check the child clusters
                stack.extend(parent_child_map.get(current_key, []))

        return filtered_clusters, counter

    def filter_clusters_Hash2(self, current_key, cluster_map, condition1, condition1_operator, condition2, condition2_operator, filtered_clusters, counter, parent_child_map):

        stack = [current_key]

        while stack:
            counter += 1
            current_key = stack.pop()
            current_cluster = cluster_map[current_key]

            if (self.applyOperator.apply_operator(current_cluster['Data_Min'][0], current_cluster['Data_Max'][0], condition1, condition1_operator, "Full") and 
                self.applyOperator.apply_operator(current_cluster['Data_Min'][1], current_cluster['Data_Max'][1], condition2, condition2_operator, "Full")):
                current_cluster['Satisfy'] = 'Full'
                filtered_clusters.append(current_cluster)

                
            else: # Otherwise, check the child clusters
                stack.extend(parent_child_map.get(current_key, []))

        return filtered_clusters, counter
            