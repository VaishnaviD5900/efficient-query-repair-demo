from collections import defaultdict
from multiprocessing import Condition
from pathlib import Path
#from statistics import correlation
import pandas as pd
import time
from .constraint_evaluation1 import constraint_evaluation1
from .constraint_evaluation1_other import constraint_evaluation1_other
from .operators import operators
from .filtered_fully import filtered_fully
from .constraint_evaluation import constraint_evaluation
from .constraint_evaluation_other import constraint_evaluation_other
from itertools import product, tee
import heapq
import os

import json, hashlib  # add with your other imports

def _resolve_cache_dir() -> Path:
    base = os.getenv("CACHE_DIR")
    if not base or base.strip() == "":
        base = os.path.join(os.getenv("OUTPUT_DIR", "./output"), "cache")
    p = Path(base).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


CACHE_DIR = _resolve_cache_dir()

def make_range_cache_key(dataName, dataSize, bucket, branch, ranges, operators):
    """
    Build a stable cache key for an RP filtering step.
    `ranges` is a sequence of dicts like {'range': (lo, hi), 'min_distance': ...}
    """
    norm_ranges = []
    for r in ranges:
        lo, hi = r['range']
        norm_ranges.append([float(lo), float(hi)])
    payload = {
        "dataName": dataName,
        "dataSize": int(dataSize),
        "bucket": int(bucket),
        "branch": int(branch),
        "ranges": norm_ranges,                 # in predicate order
        "operators": list(operators),          # in predicate order
        "version": 1                           # bump if you change representation
    }
    s = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_cached_clusters(cache_file, cluster_map):
    """
    Rebuild list of clusters (with Satisfy flag) from CSV cache.
    Returns list[dict] or None if cache missing/bad.
    """
    cache_file = Path(cache_file)
    if not cache_file.exists():
        return None
    try:
        df = pd.read_csv(cache_file)
    except Exception:
        return None
    out = []
    for _, row in df.iterrows():
        key = (int(row["Level"]), int(row["Cluster Id"]))
        info = cluster_map.get(key)
        if info is not None:
            info['Satisfy'] = row.get("Satisfy", "")
            out.append(info)
    return out

def save_clusters_cache(cache_file, clusters):
    """
    Save Level/Cluster Id/Satisfy for later reconstruction.
    """
    cache_file = Path(cache_file)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    recs = []
    for c in clusters:
        recs.append({
            "Level": c['Level'],
            "Cluster Id": c['Cluster Id'],
            "Satisfy": c.get('Satisfy', "")
        })
    pd.DataFrame(recs).to_csv(cache_file, index=False)

class filtered_with_Ranges_generalize_topK1:
    def __init__(self):
        self.distance_cache = {}
        self.applyOperator = operators()
        self.evaluate_constraint1 = constraint_evaluation1()  
        self.evaluate_constraint = constraint_evaluation()
        self.filter_fully = filtered_fully()

    def calculate(self, value1, value2):
        """
        Caching and calculating the distance between two values.
        """
        if (value1, value2) not in self.distance_cache:
            self.distance_cache[(value1, value2)] = abs(value1 - value2)
        return self.distance_cache[(value1, value2)]

    def divide_ranges(self, conditions_ranges):
        """
        Divides each condition's range into two halves if possible.
        """
        new_ranges_list = []

        for condition_range in conditions_ranges:
            # Extract condition_range values from a dictionary
            cond_min, cond_max = condition_range['range']
            # Divide range
            if cond_max - cond_min > 0:
                mid_point = (cond_min + cond_max) // 2
                new_ranges_list.append([
                    {'range': (cond_min, mid_point)}, 
                    {'range': (mid_point + 1, cond_max)}
                ])

            else:
                new_ranges_list.append([{'range': (cond_min, cond_max)}])
        return new_ranges_list

    def generalized_concrete_values(self, combination_time, satisfied, type, concrete_counter, Concrete_values_list, UserpredicateList, refinement_tuples):
        #start_time = time.time()
        # Use itertools.product to generate the Cartesian product of all lists in concrete_values
        if type == 'full':
            if tuple(satisfied['conditions']) in refinement_tuples:
                conditions_tuple = satisfied['conditions']  # (418, 8, 5)
                total_distance = sum(self.calculate(conditions_tuple[i], predicate[2]) for i, predicate in enumerate(UserpredicateList))
                
                # Prepare the new row and append
                Concrete_values_list.append({
                    'conditions': tuple(satisfied['conditions']),
                    "Similarity": total_distance,
                    'Result': satisfied['Result']
                })
                concrete_counter += 1

        else:
            filtered_refinement_tuples = refinement_tuples
                
            # Step 1: Loop dynamically through all 'condition' keys in the satisfied dictionary
            i = 1
            while f'condition{i}' in satisfied:
                condition_key = f'condition{i}'
                condition_value = satisfied[condition_key]  # Access the range (min, max)
                
                # Filter refinement tuples based on the current condition's range
                filtered_refinement_tuples = [
                    tuple_value for tuple_value in filtered_refinement_tuples
                    if condition_value[0] <= tuple_value[i - 1] <= condition_value[1]  # Check that the tuple value for this condition is in range
                ]
                
                # Exit early if no combinations left
                if not filtered_refinement_tuples:
                    break
                
                i += 1

            # Step 2: For each tuple in the filtered refinement tuples, calculate the similarity
            for combination in filtered_refinement_tuples:
                # Calculate similarity for each combination
                total_similarity = sum(self.calculate(combination[j], UserpredicateList[j][2]) for j in range(len(combination)))
                # Prepare the new row and append
                Concrete_values_list.append({
                    'conditions': combination,
                    "Similarity": total_similarity,
                    'Result': satisfied['Result']
                })
                concrete_counter += 1

        #combination_time += time.time() - start_time
        return Concrete_values_list, concrete_counter, combination_time

    def check_predicates(self, statistical_tree, all_pred_possible_Ranges, sorted_possible_refinments, expression, datasize, dataName, result_num, UserpredicateList, query_num, const_num, constraint, combination, outputDirectory, bucket,
    branch ):
        Concrete_values_list = []
        combination_time = 0
        solutions_count = 0
        Division_time, full_time, single_time, processing_time1, processing_time2 = 0, 0, 0, 0, 0
        agg_counter, counter, child_counter, check_counter, refinement_counter, concrete_counter = 0, 0, 0, 0, 0, 0

        # Use a dictionary or a pre-sorted structure for fast range-based lookups
        refinement_tuples = [tuple(r['value'] for r in refinement['refinements']) for refinement in sorted_possible_refinments]
        refinement_tuples = set(refinement_tuples)  # Convert the list to a set
        
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

        # Extract conditions and operators
        predicates = all_pred_possible_Ranges
        operators_list = [p['operator'] for p in predicates]

        # Generate all combinations of ranges for each predicate
        combinations = list(product(*[pred['values'] for pred in predicates]))

        priority_queue = []
        index = 0  # This index will be used to avoid comparing dictionaries

        priority_queue = []
        for index, current_ranges in enumerate(combinations):
            min_distance = sum(c_range['min_distance'] for c_range in current_ranges)
            heapq.heappush(priority_queue, (min_distance, index, current_ranges))
            index += 1

        start_time = time.time()
        # Process ranges based on priority (smallest min_distance first)
        while priority_queue:
            processing_start_time1 = time.time()
            
            next_range_min_distance = 0

            min_distance, indx, current_ranges = heapq.heappop(priority_queue)

            if priority_queue:
                # Peek the next item in the priority queue without removing it
                next_range_min_distance, indx, next_ranges = priority_queue[0]  # Peek the smallest element
            #ranges_counter += 1
            filtered_clusters = []

            if any(r['range'][0] != r['range'][1] for r in current_ranges):
                processing_time1 += (time.time() - processing_start_time1)
                full_start_time = time.time()
                
                cache_id = make_range_cache_key(dataName, datasize, bucket, branch, current_ranges, operators_list)
                cache_file = CACHE_DIR / f"rp_filtered_{cache_id}.csv"

                filtered_clusters = load_cached_clusters(cache_file, cluster_map)
                if filtered_clusters is None:
                    # print("Not in cache")
                    filtered_clusters = []
                    for root_key in root_clusters:
                        filtered_clusters_list_df, counter, child_counter = self.filter_clusters_partial_modified(
                            root_key, parent_child_map, cluster_map, filtered_clusters,
                            current_ranges, operators_list, counter, child_counter)
                    # Persist cache
                    save_clusters_cache(cache_file, filtered_clusters)
                else:
                    # print("In cache")
                    # cache hit
                    filtered_clusters_list_df = filtered_clusters
                
                check_counter += 1
                if dataName == "TPCH":
                    evaluate_constraint = constraint_evaluation1_other() 
                else:
                    evaluate_constraint = constraint_evaluation1() 
                
                satisfied, agg_counter, not_satisfied, Range_Result = evaluate_constraint.calculate_expression_partially(
                    filtered_clusters_list_df, current_ranges, agg_counter, expression, "ranges", "similarity", " ")
          
                if satisfied and satisfied['Range Satisfaction'] == 'Full':
                    refinement_counter += 1
                    Concrete_values_list, concrete_counter, combination_time = self.generalized_concrete_values(combination_time, 
                    satisfied, "range", concrete_counter, Concrete_values_list, UserpredicateList, refinement_tuples)
                    
                    full_time += (time.time() - full_start_time)
                
                elif satisfied and satisfied['Range Satisfaction'] == 'Partial':
                        full_time += (time.time() - full_start_time)
                        #print("Here divide")
                        p_start_time = time.time()
                        new_conditions = self.divide_ranges(current_ranges)

                        # Loop over all combinations of ranges for each predicate
                        for new_range_set in product(*new_conditions):
                            sum_min_distance = 0
                            filtered_clusters = []
                            updated_range_set = []
                            found = True
                                
                            # Loop through each range in the new divided condition (new_range_set)
                            for range_index, current_range in enumerate(new_range_set):
                                
                                # Find the minimum value in refinement_tuples that falls within the current range
                                matching_values = list({
                                    tuple_value[range_index] for tuple_value in refinement_tuples
                                    if current_range['range'][0] <= tuple_value[range_index] <= current_range['range'][1]
                                })
                                
                                if matching_values:  
                                    # Extract the user query value for this predicate
                                    user_value = UserpredicateList[range_index][2]
                                    
                                    # Calculate the minimum distance from the user query value to any matching value
                                    min_distance = min(abs(value - user_value) for value in matching_values)
                                    
                                    updated_range_set.append({'range': current_range['range'], 'min_distance': min_distance})

                                else:
                                    found = False

                            if found:                      
                                for c_range in updated_range_set:
                                    # Only sum when the ranges are not equal
                                    sum_min_distance += c_range['min_distance']
                                
                                # Push new_range_set to the priority queue sorted by similarity
                                heapq.heappush(priority_queue, (sum_min_distance, index, updated_range_set))
                                index += 1
                        Division_time += (time.time() - p_start_time)
            else: # If the range is minimal, no need to divide and filter fully
                single_start_time = time.time()
                cache_id = make_range_cache_key(dataName, datasize, bucket, branch, current_ranges, operators_list)
                cache_file = CACHE_DIR / f"rp_filtered_{cache_id}.csv"

                filtered_clusters = load_cached_clusters(cache_file, cluster_map)
                if filtered_clusters is None:
                    # print("Not in cache")
                    filtered_clusters = []
                    for root_key in root_clusters:
                        filtered_clusters_list_df, counter = self.filter_fully.filter_clusters_Hash(
                            root_key, cluster_map, [range['range'][0] for range in current_ranges], operators_list, 
                            filtered_clusters, counter, parent_child_map)
                    save_clusters_cache(cache_file, filtered_clusters)
                else:
                    # print("In cache")
                    filtered_clusters_list_df = filtered_clusters

                check_counter += 1
                if dataName == "TPCH":
                    evaluate_constraint = constraint_evaluation_other() 
                else:
                    evaluate_constraint = constraint_evaluation() 
                
                satisfied, agg_counter, Not_satisfied, result = evaluate_constraint.evaluate_constraint1(
                    filtered_clusters, expression, [range['range'][0] for range in current_ranges], agg_counter, " ",
                    "ranges", " ")

                if satisfied != []:
                    refinement_counter += 1
                    Concrete_values_list, concrete_counter,combination_time = self.generalized_concrete_values(combination_time, satisfied, "full", 
                    concrete_counter, Concrete_values_list, UserpredicateList, refinement_tuples)
                single_time += (time.time() - single_start_time)    
            
            if next_ranges != None:
                processing_start_time2 = time.time()
                if Concrete_values_list != []:                    
                    if Concrete_values_list:
                        seen = set()
                        unique_concrete_values = []

                        for item in Concrete_values_list:
                            key = (item['Similarity'], tuple(item['conditions']))
                            if key not in seen:
                                seen.add(key)
                                unique_concrete_values.append(item)
                        
                        # Sort once all unique values are added
                        Concrete_values_sorted = sorted(unique_concrete_values, key=lambda x: (x['Similarity'], x['conditions']))
                        Concrete_values_sorted = Concrete_values_sorted[:result_num]
                    
                    if result_num != "all":
                        if next_range_min_distance > max([d['Similarity'] for d in Concrete_values_sorted]):
                            if len(Concrete_values_sorted) >= result_num:
                                break # stop and take top-k
                processing_time2 += (time.time() - processing_start_time2)
  
        elapsed_time = time.time() - start_time
 
        # Create a DataFrame from the filtered satisfied_conditions   
        #satisfied_conditions_df = pd.DataFrame(satisfied_conditions)
        #satisfied_conditions_df.to_csv("satisfied_conditions__Ranges.csv", index=False)
        Concrete_values_sorted = Concrete_values_sorted if 'Concrete_values_sorted' in locals() else []
        satisfied_conditions_concrete_df = pd.DataFrame(Concrete_values_sorted)
        
        output_directory = outputDirectory
        # For the second file
        file_path_2 = os.path.join(
            output_directory, 
            f"satisfied_conditions_Ranges_{dataName}_size{datasize}_query{query_num}_constraint{constraint}.csv"
        )
        satisfied_conditions_concrete_df.to_csv(file_path_2, index=False) 

        
        info = []
        refinement_info = {
            "Data Name": dataName,
            "Data Size": datasize,
            "Query No.": query_num,
            "Constraint Num": const_num,
            "Type": "Ranges",
            "Top-K": result_num,
            "Combinations No.": combination,
            "Distance": round(check_counter / combination * 100, 3),
            "Access No.": counter + child_counter,
            "Checked No.": check_counter,
            "Refinement No.": refinement_counter,
            "Time": round(elapsed_time, 3),
            "Constraint Width": round(constraint[1]-constraint[0], 2),
            "Solutions Count": solutions_count,
            "Constraint": constraint,
            #"Distribution": distribution,
            #"Correlation": Correlation,
            "Query": UserpredicateList,
            "Range Evaluation Time": round(full_time, 3),
            "Division Time": round(Division_time,3),
            "Single Time": round(single_time, 3),
            "Processing Time": round(processing_time1 + processing_time2, 3)
        }
        info.append(refinement_info)
        info_df = pd.DataFrame(info)
        output_directory = outputDirectory
        # Ensure the directory exists
        os.makedirs(output_directory, exist_ok=True)

        # Define the full file path including the directory
        file_path = os.path.join(output_directory, f"Run_info_{dataName}_size{datasize}_constraint{const_num}.csv") 

        write_header = not os.path.exists(file_path)  # Write header only if the file does not exist

        info_df.to_csv(file_path, mode='a', index=False, header=write_header)

        print("Number of boxes accessed:", counter + child_counter)
        print("Number of checks:", check_counter)
        print("Number of refinements:", refinement_counter)
        print("Partial Time:", round(Division_time, 3), "seconds")
        print("Time taken Overall:", round(elapsed_time, 3), "seconds")

    def filter_clusters_partial_modified(self, cluster_key, parent_child_map, cluster_map, filtered_clusters, conditions, operators, counter, child_counter):
        stack = [cluster_key]

        while stack:
            counter += 1
            cluster_key = stack.pop()
            cluster_info = cluster_map[cluster_key]

            # Extract relevant data
            data_Min = cluster_info['Data_Min']
            data_Max = cluster_info['Data_Max']

            # Check if this cluster fully satisfies all conditions
            fully_satisfies = True
            partially_satisfies = True

            for i, (condition, operator) in enumerate(zip(conditions, operators)):
                if not self.applyOperator.apply_operator_ranges(data_Min[i], data_Max[i], condition['range'][0], condition['range'][1], operator, "Full"):
                    fully_satisfies = False
                if not self.applyOperator.apply_operator_ranges(data_Min[i], data_Max[i], condition['range'][0], condition['range'][1], operator, "Partial"):
                    partially_satisfies = False
                    break  # If any condition is not partially satisfied, stop checking

            # Check if this cluster fully satisfies the conditions
            if fully_satisfies:
                cluster_info['Satisfy'] = 'Full' 
                filtered_clusters.append(cluster_info)

            elif partially_satisfies:
                if cluster_key in parent_child_map:
                    for child_key in parent_child_map[cluster_key]:

                        child_counter+=1
                        child_info = cluster_map[child_key]
                        child_Min = child_info['Data_Min']
                        child_Max = child_info['Data_Max']

                        # Check if the child fully satisfies the conditions
                        child_fully_satisfies = True
                        child_partially_satisfies = True

                        for i, (condition, operator) in enumerate(zip(conditions, operators)):
                            if not self.applyOperator.apply_operator_ranges(child_Min[i], child_Max[i], condition['range'][0], condition['range'][1], operator, "Full"):
                                child_fully_satisfies = False
                            if not self.applyOperator.apply_operator_ranges(child_Min[i], child_Max[i], condition['range'][0], condition['range'][1], operator, "Partial"):
                                child_partially_satisfies = False
                                break


                        # Fully satisfying child
                        if child_fully_satisfies:
                            child_info['Satisfy'] = 'Full'
                            filtered_clusters.append(child_info)

                        # Partial child
                        elif child_partially_satisfies:
                            stack.append(child_key)

                else:
                    cluster_info['Satisfy'] = 'Partial'
                    filtered_clusters.append(cluster_info)

            else:
                stack.extend(parent_child_map.get(cluster_key, []))
        
        return filtered_clusters, counter, child_counter

