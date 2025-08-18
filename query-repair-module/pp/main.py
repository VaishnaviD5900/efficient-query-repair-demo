import time
from typing import List, Union
from SQL_operators import SQL_operators
from kd_tree1 import kd_tree1
from brute_force import brute_force
from Dataframe import Dataframe
from attributesRanges1 import attributesRanges1
from attributesRanges import attributesRanges
from ExpressionEvaluator1 import ExpressionEvaluator1
import pandas as pd
import numpy as np
from generate_convex_hull import generate_convex_hull
from statistical_calculation import statistical_calculation
from filtered_fully import filtered_fully
from filtered_with_Ranges_generalize_topK1 import filtered_with_Ranges_generalize_topK1
from filtered_with_Ranges_generalize_topK1_norm import filtered_with_Ranges_generalize_topK1_norm
from predicatesPossibleValues import predicatesPossibleValues
from ExpressionEvaluator import ExpressionEvaluator
import matplotlib.pyplot as plt
import re
def analyze_distribution(df, column):
    plt.figure(figsize=(10, 6))

    # Plot histogram
    plt.hist(df[column], bins=30, edgecolor='black')
    plt.title(f"Distribution of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.show()
 
def get_clusters(df_merged, buckestSize, branchNum):
    start_time = time.time() 
    KD_tree = kd_tree1(df_merged, 3, buckestSize, branchNum)
    KD_tree_dict = KD_tree.flatten_tree()
    KD_tree.save_to_csv("KD_tree.csv")
    # Save the tree to a CSV file
    #generator1 = generate_clusters1()
    #cluster_tree1 = generator1.generating_clusters(df_merged.values)#, n_clusters=None, distance_threshold=20)  # Adjust as needed    
    #cleaned_clusters = generator1.remove_duplicates(cluster_tree1)
    #final_cluster_tree = generator1.add_metadata(cleaned_clusters, df_merged.values, cluster_tree1)
    end_time = time.time() 
    print("Generating clusters time: ", round(end_time - start_time, 3))

    return KD_tree_dict

def get_convex_hull(cluster_tree):
    convex_hull = generate_convex_hull()
    # Calculate and print convex hull points for each cluster in the tree
    hulls = convex_hull.calculate_convex_hulls_for_tree(cluster_tree)
    
    #for hull in hulls:
        #print(f"Convex Hull Points: {hull['Convex Hull Points']}, Level {hull['Level']}, Cluster {hull['Cluster Id']}")
    # Prepare hull info for CSV
    hull_info_list = []
    for hull in hulls:
        hull_info_list.append({
            'Level': hull['Level'],
            'Cluster Id': hull['Cluster Id'],
            'Data points': hull['Data points']
            #'Constraint points': hull['Constraint points']
        })

    # Create a DataFrame
    df_hulls = pd.DataFrame(hull_info_list)

    # Save to CSV
    df_hulls.to_csv('hull_info.csv', index=False)

    #convex_hull.draw_convex_hulls(cluster_tree)
    return hull_info_list

def get_statistical_info(cluster_tree, df, aggregations, predicates_number, constraint_columns, dataName, dataSize, query_num):
    stat_info = statistical_calculation()
    stat_tree = stat_info.statistical_calculation(cluster_tree, df, aggregations, predicates_number, constraint_columns, dataName, dataSize, query_num)

    return stat_tree

def userQuery_Healthcare_Q1(qua, size):
    query_num = 1
    #getting dataframe
    input = Dataframe()
    df_original, dataName, dataSize = input.getDataframe_Healthcare(size)
    print("\n\nData Size: ", dataSize)
    op = SQL_operators()
    predAttRanges = attributesRanges()
    df1 = op.filter("UQ", df_original, "income", ">=", 250) 
    df2 = op.filter("UQ", df1, "num-children", ">=", 3)
    df3 = op.filter("UQ", df2, "county", "<=", 3)

    all_pred_possible_values = predAttRanges.generatePossibleValues(df_original, op.get_predicates_attributes()) 

    return df_original, df3, all_pred_possible_values, op, dataName, dataSize, query_num  

def userQuery_Healthcare_Q2(qua, size):
    query_num = 2
    #getting dataframe
    input = Dataframe()
    df_original, dataName, dataSize = input.getDataframe_Healthcare(size)
    op = SQL_operators()
    predAttRanges = attributesRanges()
    df1 = op.filter("UQ", df_original, "income", "<=", 100000)
    df2 = op.filter("UQ", df1, "complications", ">=", 5)
    df3 = op.filter("UQ", df2, "num-children", ">=", 4)

    all_pred_possible_values = predAttRanges.generatePossibleValues(df_original, op.get_predicates_attributes()) 

    return df_original, df3, all_pred_possible_values, op, dataName, dataSize, query_num

def userQuery_Healthcare_Q3(qua, size):
    query_num = 3
    #getting dataframe
    input = Dataframe()
    df_original, dataName, dataSize = input.getDataframe_Healthcare(size)
    op = SQL_operators()
    predAttRanges = attributesRanges()
    df1 = op.filter("UQ", df_original, "income", ">=", 300000)
    df2 = op.filter("UQ", df1, "complications", ">=", 5)
    df3 = op.filter("UQ", df2, "county", "==", 1) 

    all_pred_possible_values = predAttRanges.generatePossibleValues(df_original, op.get_predicates_attributes()) 

    return df_original, df3, all_pred_possible_values, op, dataName, dataSize, query_num    

def constraint1_Healthcare(df, constraint): 
    result_list = []
    const_num = 1
    evaluator = ExpressionEvaluator()
    aggregations = {
        "agg1": 'count("race == 1 and label == 1")',
        "agg2":'count("race == 1")',
        "agg3": 'count("race == 2 and label == 1")',
        "agg4": 'count("race == 2")'
    }
    expression = [f"{constraint[0]} <= (agg1 / agg2) - (agg3 / agg4) <= {constraint[1]}"]

    # Evaluate individual aggregations
    for index, (agg_name, agg_func) in enumerate(aggregations.items(), start=1):
        result = evaluator.evaluate_aggregation(df, agg_func)
        result_list.append(f"agg{index}: {result}")
    
    # Retrieve list of all columns used in the queries
    columns_used = evaluator.get_columns_used()
    
    return columns_used, aggregations, expression, const_num

def constraint2_Healthcare(df, constraint): 
    result_list = []
    const_num = 2
    evaluator = ExpressionEvaluator()
    aggregations = {
        "agg1": 'count("ageGroup == 1 and label == 1")',
        "agg2":'count("ageGroup == 1")',
        "agg3": 'count("ageGroup == 2 and label == 1")',
        "agg4": 'count("ageGroup == 2")'
    }
    expression = f"{constraint[0]} <= (agg1 / agg2) - (agg3 / agg4) <= {constraint[1]}"

    # Evaluate individual aggregations
    for index, (agg_name, agg_func) in enumerate(aggregations.items(), start=1):
        result = evaluator.evaluate_aggregation(df, agg_func)
        result_list.append(f"agg{index}: {result}")
    
    # Retrieve list of all columns used in the queries
    columns_used = evaluator.get_columns_used()
    
    return columns_used, aggregations, expression, const_num

def userQuery_ACSIncome_Q4(qua, size):
    query_num = 1
    #getting dataframe
    input = Dataframe()
    df_original, dataName, dataSize = input.getDataframe_ACSIncome(size)
    print("\n\nData Size: ", dataSize)
    op = SQL_operators()
    predAttRanges = attributesRanges()
    #df_original = adjust_unique_values(df_original, 'WKHP', qua) 

    df1 = op.filter("UQ", df_original, "WKHP", ">=", 30) 
    df2 = op.filter("UQ", df1, "SCHL", ">=", 12) 
    df3 = op.filter("UQ", df2, "COW", ">=", 3.0) 

    all_pred_possible_values = predAttRanges.generatePossibleValues(df_original, op.get_predicates_attributes()) 
    return df_original, df3, all_pred_possible_values, op, dataName, dataSize, query_num

def adjust_unique_values(df, column, new_unique_count):
    """
    Adjusts the number of unique values in a column while keeping the DataFrame length the same.
    
    :param df: DataFrame
    :param column: Column name to modify
    :param new_unique_count: Desired number of unique values
    :return: Modified DataFrame
    """
    unique_values = np.linspace(1, new_unique_count, new_unique_count, dtype=int)  # Generate spread-out unique values
    df[column] = np.random.choice(unique_values, size=len(df), replace=True)  # Assign values while keeping length same
    return df

def userQuery_ACSIncome_Q5(qua, size):
    query_num = 2
    #getting dataframe
    input = Dataframe()
    df_original, dataName, dataSize = input.getDataframe_ACSIncome(size)
    op = SQL_operators()
    predAttRanges = attributesRanges()
    df1 = op.filter("UQ", df_original, "WKHP", "<=", 40)
    df2 = op.filter("UQ", df1, "SCHL", "<=", 19)
    df3 = op.filter("UQ", df2, "COW", "<=", 4)
    all_pred_possible_values = predAttRanges.generatePossibleValues(df_original, op.get_predicates_attributes()) 

    return df_original, df3, all_pred_possible_values, op, dataName, dataSize, query_num
    
def userQuery_ACSIncome_Q6(qua, size):
    query_num = 3
    #getting dataframe
    input = Dataframe()
    df_original, dataName, dataSize = input.getDataframe_ACSIncome(size)
    op = SQL_operators()
    predAttRanges = attributesRanges()
    df1 = op.filter("UQ", df_original, "AGEP", ">=", 35)
    df2 = op.filter("UQ", df_original, "COW", ">=", 2)
    df3 = op.filter("UQ", df1, "SCHL", "<=", 15)

    all_pred_possible_values = predAttRanges.generatePossibleValues(df_original, op.get_predicates_attributes()) 

    return df_original, df3, all_pred_possible_values, op, dataName, dataSize, query_num  

def constraint3_ACSIncome(df, constraint): 
    result_list = []
    const_num = 3
    evaluator = ExpressionEvaluator()
    aggregations = {
        "agg1": 'count("SEX == 1 and PINCP >= 20000")',
        "agg2":'count("SEX == 1")',
        "agg3": 'count("SEX == 2 and PINCP >= 20000")',
        "agg4": 'count("SEX == 2")'
    }
    expression = f"{constraint[0]} <= (agg1 / agg2) - (agg3 / agg4) <= {constraint[1]}"

    # Evaluate individual aggregations
    for index, (agg_name, agg_func) in enumerate(aggregations.items(), start=1):
        result = evaluator.evaluate_aggregation(df, agg_func)
        result_list.append(f"agg{index}: {result}")
    
    # Retrieve list of all columns used in the queries
    columns_used = evaluator.get_columns_used()
    
    return columns_used, aggregations, expression, const_num

def constraint4_ACSIncome(df, constraint):
    result_list = []
    const_num = 4
    evaluator = ExpressionEvaluator()
    aggregations = {
        "agg1": 'count("RAC1P == 1 and PINCP >= 10000")',
        "agg2":'count("RAC1P == 1")',
        "agg3": 'count("RAC1P == 2 and PINCP >= 10000")',
        "agg4": 'count("RAC1P == 2")'
    }
    expression = f"{constraint[0]} <= (agg1 / agg2) - (agg3 / agg4) <= {constraint[1]}"

    # Evaluate individual aggregations
    for index, (agg_name, agg_func) in enumerate(aggregations.items(), start=1):
        result = evaluator.evaluate_aggregation(df, agg_func)
        result_list.append(f"agg{index}: {result}")

    # Retrieve list of all columns used in the queries
    columns_used = evaluator.get_columns_used()

    return columns_used, aggregations, expression, const_num

def constraint2_Cardinality_ACSIncome(df, constraint):
    result_list = []
    evaluator = ExpressionEvaluator1()
    aggregations = {
        "agg1": 'count("SEX == 2 and MAR == 1")',
        "agg2": 'count("RAC1P == 2")'
        #"agg3": 'count("ageGroup == 3")'
    }
    expression = [f"{constraint[2]} <= agg1 <= {constraint[0]}", f"{constraint[2]} <= agg2 <= {constraint[1]}"]#, f"{constraint[3]} <= agg3 <= {constraint[2]}"]

    # Evaluate individual aggregations
    for index, (agg_name, agg_func) in enumerate(aggregations.items(), start=1):
        result = evaluator.evaluate_aggregation(df, agg_func)
        result_list.append(f"agg{index}: {result}")

    # Retrieve list of all columns used in the queries
    columns_used = evaluator.get_columns_used()

    return columns_used, aggregations, expression

def constraint_Cardinality(df, constraint): 
    result_list = []
    evaluator = ExpressionEvaluator()
    aggregations = {
        "agg1": 'count("SEX == 1")'
    }
    expression = '10 <= agg1 <= 35'

    # Evaluate individual aggregations
    for index, (agg_name, agg_func) in enumerate(aggregations.items(), start=1):
        result = evaluator.evaluate_aggregation(df, agg_func)
        result_list.append(f"agg{index}: {result}")
    
    # Retrieve list of all columns used in the queries
    columns_used = evaluator.get_columns_used()
    
    return columns_used, aggregations, expression

def userQuery_TPCH_Q7(qua, size):
    query_num = 1
    #getting dataframe
    input = Dataframe()

    df_lineitem, df_nation, df_part, df_partsupp, df_region, df_supplier, dataName, dataSize = input.getDataframe_TPCH(size)
    op = SQL_operators()
    predAttRanges = attributesRanges()

    # Perform the join operations
    # Merge all tables, including lineitem
    merged_df = pd.merge(
        pd.merge(
            pd.merge(
                pd.merge(
                    pd.merge(df_part, df_partsupp, left_on='p_partkey', right_on='ps_partkey'),
                    df_supplier, left_on='ps_suppkey', right_on='s_suppkey'
                ),
                df_nation, left_on='s_nationkey', right_on='n_nationkey'
            ),
            df_region, left_on='n_regionkey', right_on='r_regionkey'
        ),
        df_lineitem, left_on=['p_partkey', 'ps_suppkey'], right_on=['l_partkey', 'l_suppkey']
    )
    merged_df = merged_df.sample(n= size, replace=True, random_state=42)  # You can change the value of n as needed
    # Save the merged DataFrame to a CSV file
    #output_file = 'merged_data.csv'
    #merged_df.to_csv(output_file, index=False)

    merged_df1 = op.filter("UQ", merged_df, "p_size", ">=", 10)
    merged_df2 = op.filter("UQ", merged_df1, "p_type", "==", 20)
    merged_df3 = op.filter("UQ", merged_df2, "r_name", "==", 4)

    all_pred_possible_values = predAttRanges.generatePossibleValues(merged_df, op.get_predicates_attributes())

    return merged_df, merged_df3, all_pred_possible_values, op, dataName, dataSize, query_num

def constraint5_TPCH(df, constraint):
    const_num = 5
    result_list = []
    evaluator = ExpressionEvaluator1()
    aggregations = {
        "agg1": 'sum("Revenue")',
        "agg2": 'min("Revenue all")'
    }
    expression = [f"{constraint[0]} <= (agg1 / agg2) <= {constraint[1]}"]

    # Evaluate individual aggregations
    for index, (agg_name, agg_func) in enumerate(aggregations.items(), start=1):
        result = evaluator.evaluate_aggregation(df, agg_func)
        result_list.append(f"agg{index}: {result}")

    # Retrieve list of all columns used in the queries
    columns_used = evaluator.get_columns_used()

    return columns_used, aggregations, expression, const_num


_NUM_LITERAL = re.compile(
    r'(?<![A-Za-z_])'                 # not immediately preceded by a letter/underscore
    r'(\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)'  # number: int/float with optional exponent
    r'(?![A-Za-z_])'                  # not immediately followed by a letter/underscore
)

def _sanitize_expressions(expr_in: Union[str, List[str]]) -> Union[str, List[str]]:
    """
    Sanitize constraint expressions.
    - If input is a list[str], return a list[str] with each element sanitized.
    - If input is a str, return a sanitized str.

    Converts only standalone numeric literals (e.g., 0.1, 2e-3, 1000) to float strings,
    and does NOT touch identifiers like 'agg1', 'x2', etc.
    """
    def sanitize(expr: str) -> str:
        # remove stray quotes (if any were sent around numbers)
        expr = expr.replace("'", "").replace('"', "")
        # convert numeric literals to canonical float strings
        expr = _NUM_LITERAL.sub(lambda m: str(float(m.group(1))), expr)
        return expr

    if isinstance(expr_in, list):
        return [sanitize(e) for e in expr_in]
    elif isinstance(expr_in, str):
        return sanitize(expr_in)
    else:
        raise TypeError(f"Unsupported type for expression: {type(expr_in)}")


def resolve_constraint(dataName: str, constraint: list | tuple, constraint_def: dict | None):
    """
    Returns (constraint_columns, aggregations, expression, const_num).
    If constraint_def is provided (from frontend), use that directly.
    Otherwise, fall back to dataset-specific default (TPCH only here).
    """
    if constraint_def is not None:
        columns = constraint_def["columns"]
        aggregations = constraint_def["aggregations"]
        expression = _sanitize_expressions(constraint_def["expression"])  # may be str or list
        print("expression::", expression)
        const_num = int(constraint_def.get("const_num", 0))
        return columns, aggregations, expression, const_num

    if dataName == "TPCH":
        low, high = map(float, constraint)
        columns = ["Revenue", "Revenue all"]
        aggregations = {
            "agg1": 'sum("Revenue")',
            "agg2": 'min("Revenue all")',
        }
        # For default case, keep same type convention → use list
        expression = [f"{low} <= (agg1 / agg2) <= {high}"]
        const_num = 5
        return columns, aggregations, expression, const_num

    raise ValueError("constraint_def is required for this dataset.")


def main(dataName: str = "TPCH",
    Top_k: int = 7,
    predicates: list[dict] | None = None ,
     constraint_def: dict | None = None):
    if predicates is None:
        predicates = [
            {"field": "p_size", "op": ">=", "value": 10},
            {"field": "p_type", "op": "==", "value": 20},
            {"field": "r_name", "op": "==", "value": 4},
            ]
    if constraint_def is None:
        constraint_def = {
            "columns": ["Revenue", "Revenue all"],
            "aggregations": {
                "agg1": 'sum("Revenue")',
                "agg2": 'min("Revenue all")'
            },
            # You can bake the numbers in here (single constraint case)…
            "expression": ['0.0014 <= (agg1 / agg2) <= 10000000000000'],
            "const_num": 5
        }

    print("predicates", predicates)
    print("constraints", constraint_def)

    # Define the configurations
    # -----------------------------------------------
    constraints = [[0.0014, 10000000000000]]
    quantize = [1350] #[150, 450, 750, 1050, 1350]
    Top_k = [Top_k] 
    size = 50000
    bucketSize = [15] 
    branchNum = [5] 
    queryNum = 7
    outputDirectory = "C:/Query-Repair-System/efficient-query-repair-demo/query-repair-backend/output"
    # -----------------------------------------------

    for bucket in bucketSize:
        for branch in branchNum:
            for k in Top_k:
                for qua in quantize:
                    df_original, column_names, all_pred_possible_values, sorted_possible_refinments1, predicate_att_list, op = [], [], [], [], [], []
                    # ADD this instead:
                    op = SQL_operators()
                    predAttRanges = attributesRanges()
                    input_loader = Dataframe()

                    # 1) Load per dataset (no filters here)
                    if dataName == "TPCH":
                        df_lineitem, df_nation, df_part, df_partsupp, df_region, df_supplier, dataName, dataSize = \
                            input_loader.getDataframe_TPCH(size)

                        # 2) Build the same join as userQuery_TPCH_Q7 (but DO NOT apply hardcoded filters)
                        merged_df = pd.merge(
                            pd.merge(
                                pd.merge(
                                    pd.merge(
                                        pd.merge(df_part, df_partsupp, left_on='p_partkey', right_on='ps_partkey'),
                                        df_supplier, left_on='ps_suppkey', right_on='s_suppkey'
                                    ),
                                    df_nation, left_on='s_nationkey', right_on='n_nationkey'
                                ),
                                df_region, left_on='n_regionkey', right_on='r_regionkey'
                            ),
                            df_lineitem, left_on=['p_partkey', 'ps_suppkey'], right_on=['l_partkey', 'l_suppkey']
                        )
                        # Optional: sample same as before (keeps downstream behavior identical)
                        merged_df = merged_df.sample(n=size, replace=True, random_state=42)

                        df_original = merged_df

                    elif dataName == "Healthcare":
                        df_original, _, dataSize = input_loader.getDataframe_Healthcare(size)

                    elif dataName == "ACSIncome":
                        df_original, _, dataSize = input_loader.getDataframe_ACSIncome(size)

                    else:
                        raise ValueError(f"Unsupported dataset: {dataName}")

                    # 3) Apply FRONTEND predicates using your existing operator
                    df_userQueryOut = df_original
                    print("df original", df_original)
                    REL_OPS = {"<", "<=", ">", ">="}
                    for pred in (predicates or []):
                         col = pred["field"]
                         op_sym = pred["op"]
                         val = pred["value"]

                        # If operator is relational, coerce both column + value to numeric
                         if op_sym in REL_OPS:
                            # Ensure dataframe column is numeric
                            df_userQueryOut[col] = pd.to_numeric(df_userQueryOut[col], errors="coerce")
                            # Ensure value is numeric too
                            try:
                                val = float(val)
                            except Exception:
                                pass
                        # Expect shape: {"field": "...", "op": "...", "value": ...}
                         df_userQueryOut = op.filter("UQ", df_userQueryOut, pred["field"], pred["op"], pred["value"])

                    # 4) Compute possible values (match your prior behavior per dataset)
                    if dataName == "TPCH":
                        # you previously used 'merged_df' for TPCH
                        all_pred_possible_values = predAttRanges.generatePossibleValues(df_original, op.get_predicates_attributes())
                    else:
                        # you previously used original df for ACS/Healthcare
                        all_pred_possible_values = predAttRanges.generatePossibleValues(df_original, op.get_predicates_attributes())

                    # 5) Provide a dummy query_num (kept for compatibility in logs)
                    query_num = 1

                    # (Optional) debug print—mirrors your old log
                    print("input---", (df_original, df_userQueryOut, all_pred_possible_values, op, dataName, dataSize, queryNum))

                    predicate_att_list = op.getPredicateList()
                    column_names = [item[0] for item in predicate_att_list]     # Extract the column names from the predicate_att_list     
                    PCL_list = brute_force() 
                    possibleValues = predicatesPossibleValues()
                    sorted_possible_refinments1 = possibleValues.generate_possible_refinments_similarity(all_pred_possible_values, op.getPredicateList())
                    combination = len(sorted_possible_refinments1)
                    for constraint in constraints:
                            count = 1
                            while count <= 1:
                                constraint_columns, df_merged, df_constraint, corr_matrix, df_predicate, statistical_tree, cluster_tree, columns = [], [], [], [], [], [], [], []
                                df_predicate = pd.DataFrame(df_original, columns=column_names)      # Convert to a Pandas DataFrame with dynamic column names
                                # constraint_columns, aggregations, expression, const_num = globals()[f"constraint{constraintNum}_{dataName}"](df_original, constraint)
                                constraint_columns, aggregations, expression, const_num = resolve_constraint(dataName, constraint, constraint_def)  
                                print("inputs::----", (constraint_columns, aggregations, expression, const_num))
                                df_constraint = pd.DataFrame(df_original, columns=constraint_columns)    
                                df_merged = pd.concat([df_predicate, df_constraint], axis=1)        # Merging the dataframes (predicates columns with constraints columns) by their index
                                print("df_constraint", df_constraint)
                                print("df_predicate", df_predicate)     # Merging the dataframes (predicates columns with constraints columns) by their index
                                print("df_merged", df_merged)
                                cluster_tree = get_clusters(df_merged.values.tolist(), bucket, branch)
                                stat_start_time = time.time() 
                                statistical_tree = get_statistical_info(cluster_tree, df_merged, aggregations, len(all_pred_possible_values), constraint_columns, dataName, dataSize, query_num)
                                stat_end_time = time.time()
                                print("Number of Combinations: ", combination)
                                print("Time of collecting Statistical information:", round(stat_end_time - stat_start_time, 4))

                                corr_matrix = df_merged.corr()
                                print('\n\nPredicates and Constraints correlation:\n-------------------------------------------------------\n', corr_matrix)

                                
                                print("\n\n---------------------Brute Force--------------------")
                                #calling Possible Candidate Lists to go through all possible refinments
                                #PCL_list.PossibleRef_allCombination(df_merged, sorted_possible_refinments1, dataSize, dataName, k, len(all_pred_possible_values), constraint, query_num, combination) 

                                print("\n\n-------------------------FF------------------------\n")
                                filter_fully = filtered_fully()
                                filter_fully.check_predicates(sorted_possible_refinments1, statistical_tree, expression, dataSize, dataName, k, query_num, const_num, constraint, op.getPredicateList(), combination, outputDirectory, bucket, branch)

                                print("\n\n-------------------------RP------------------------\n")
                                ranges = attributesRanges1()
                                
                                #filter_ranges_partial = filtered_with_Ranges_generalize_topK1_norm()
                                #all_pred_possible_Ranges= ranges.generatePossibleValues_equalWidth2(df_original, op.getPredicateList(), sorted_possible_refinments1)  
                                all_pred_possible_Ranges= ranges.generatePossibleValues_equalWidth1(df_original, op.getPredicateList(), sorted_possible_refinments1)                                  
                                filter_ranges_partial = filtered_with_Ranges_generalize_topK1()
                                filter_ranges_partial.check_predicates(statistical_tree, all_pred_possible_Ranges, sorted_possible_refinments1, expression, dataSize, dataName, k, op.getPredicateList(), query_num, const_num, constraint, combination, outputDirectory)
                                
                                print("\n\n-----------------------------------------\n")


                                # Generate a unique ID based on configuration
                                config_id = f"size{size}_constr{constraint[0]}-{constraint[1]}"

                                # Log the results
                                print("----------------------------------------------------------------------------\n")
                                print(f"Completed run with Running configuration Id: {config_id}, size={size}, branch= {branch}, bucket= {bucket}, constraints={constraint}, top-K={k}\n")
                                print("*********************************************************************************************\n")

                                count +=1
    
    ''' 
    # To generate Graphs
    directory_path = '/Users/Shatha/Downloads/Query_Refinment_Shatha/sh_Final2/Time_vs_Constraints_H'  # Update this to your directory path
    
    graph = genGraph(directory_path)
    Measures = ['Time', 'Checked Num', 'Access Num']
    
    inv_graphs = investigation_graphs()
    for m in Measures:
        #inv_graphs.Generate_Time_vs_Constraints(m) #bruteForce
        graph.Generate_Time_vs_factors(m, "BranchNum", "ACSIncome") #Either BranchNum, BucketSize, CombinationNum and TopK
        #graph.Generate_Time_vs_DataSize(m, "DataSize", "ACSIncome")
        #graph.Generate_Time_vs_Constraints(m, "ACSIncome")
        #inv_graphs.plot_time_by_constraint_Distance(m, "ACSIncome")
    #inv_graphs.Generate_Time_vs_Constraints_Erica('Search Time', 'Preprocessing Time')
    ''' 
      
if __name__ == '__main__':

    main()


