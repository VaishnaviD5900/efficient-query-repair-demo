import pandas as pd
from SQL_operators import SQL_operators
from itertools import product, chain, combinations
import matplotlib.pyplot as plt
#from Manhattan_distance import Manhattan_distance
import time
from itertools import product
from operators import operators
from constraint_evaluation import constraint_evaluation
import os
import itertools





class brute_force:
    def __init__(self):
        self.applyOperator = operators()

    def calculate_combinations(self, all_pred_possible_values):
        # Extract information about each predicate
        predicates = [{'predicate': pred_info['predicate'], 'values': pred_info['values']} for pred_info in all_pred_possible_values]
        # Extract just the values for each predicate
        predicate_values = [predicate['values'] for predicate in predicates]

        # Generate all combinations (Cartesian product) of the predicate values
        combinations = itertools.product(*predicate_values)

        # Remove duplicates by sorting the values in each combination and using a set
        unique_combinations = {tuple(sorted(comb)) for comb in combinations}

        # Number of unique combinations
        num_combinations = len(unique_combinations)

        print("Number of Combinations: ", unique_combinations)

        return num_combinations

    def calculate(self, value1, value2):
        return abs(value1 - value2)
    
    def filter_data(self, filtered_df, filtered_data, conditions, operators, columns, counter):
        
        for index, row in filtered_df.iterrows():
            fully_satisfies = True

            # Loop through each condition and operator
            for idx, (condition, operator, column) in enumerate(zip(conditions, operators, columns)):
                # If any condition is not satisfied, mark as False and break
                counter += 1
                if not self.applyOperator.apply_operator_bruteForce(row[column], condition, operator):
                    fully_satisfies = False
                    break

                # If all conditions are satisfied, mark the cluster as "Full"
            if fully_satisfies:
                filtered_data.append(row)

        return filtered_data, counter
        
    def PossibleRef_allCombination(self, filtered_df, sorted_possible_refinments, datasize, dataName, result_num, predicate_num, constraint, query_num, combination):
        satisfied_conditions = []
        op = SQL_operators()
        counter = 0
        found = False
        check_counter = 0
        refinement_counter = 0   
        
        filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated()]
        # Slice the array starting from predicates_number to get constraint points
        #predicate_df = filtered_df.iloc[:, :predicate_num]

        start_time = time.time()
        
        for refinement in sorted_possible_refinments:
            if found == True:
                break
            conditions = []
            operators = []
            columns = []
            filtered_data = []
            
            # Loop over each condition in the refinement dictionary
            for ref in refinement['refinements']:
                conditions.append(ref['value'])
                operators.append(ref['operator'])
                columns.append(ref['column'])

            similarity = refinement['distance']

            # Apply each predicate to the DataFrame
            filtered_data, counter = self.filter_data(filtered_df, filtered_data, conditions, operators, columns, counter)

            satisfied, check_counter, counter = self.custom_agg_func(op, filtered_data, counter, check_counter, conditions , similarity, constraint)
            if satisfied != []:
                refinement_counter += 1
                satisfied_conditions.append(satisfied)
                if len(satisfied_conditions) == result_num:
                    found = True
                    break
                
            #directory = '/Users/Shatha/Downloads/Query_Refinment_Shatha/running_files'
            #filename = f'filtered_BruteForce_combination_{conditions}_modified.csv'
            #filename = filename.replace(" ", "_").replace(",", "_")
            # Join the directory and file name to create the full path
            #full_path = os.path.join(directory, filename)
            # Save to CSV
            #filtered_df.to_csv(full_path, index=False)
            
        end_time = time.time()  

        satisfied_conditions_df = pd.DataFrame(satisfied_conditions)
        satisfied_conditions_df.to_csv("satisfied_conditions_BruteForce.csv", index=False)
        elapsed_time = end_time - start_time

        info = []
        refinement_info = {
            "Data Name": dataName,
            "Data Size": datasize,
            "Query Num": query_num,
            "Type": "BruteForce",
            "Top-K": result_num,
            "Combinations Num": combination,
            "Distance":" ",
            "Access Num": counter,
            "Checked Num": check_counter,
            "Refinement Num": refinement_counter,
            "Time": round(elapsed_time, 3)
        }
        info.append(refinement_info)
        # Save info to CSV
        info_df = pd.DataFrame(info)
        output_directory = "/home/dbgroup/shatha/pp/Final_Exp2"
        # Ensure the directory exists
        os.makedirs(output_directory, exist_ok=True)

        # Define the full file path including the directory
        file_path = os.path.join(output_directory, f"Run_info_{dataName}_size{datasize}_H_brute.csv")

        write_header = not os.path.exists(file_path)  # Write header only if the file does not exist

        # Write to CSV with appropriate header setting
        info_df.to_csv(file_path, mode='a', index=False, header=write_header)

        print("Number of data access: ", counter)
        print("Number of checked", check_counter)
        print("Number of refinments", refinement_counter)
        print("Time taken Overall:", round(elapsed_time, 3), "seconds") 
        #print("Number of Aggregation calculated: ", agg_counter)
        

    # Define a custom aggregation function
    def custom_agg_func(self, op, filtered_df, counter, check_counter, conditions, similarity, constraint):
        satisfied = []

        filtered_df = pd.DataFrame(filtered_df)
        
        if filtered_df.empty:
            #print("*************************", refinement_values)
            return satisfied, check_counter, counter
        else:
            counter += 6
            ''' 
            # For ACSIncome -------------------------------------------------------------------------

            male_positive_tuples_sex = op.filter("WhyN", filtered_df, "SEX", "==", 1.0) 
            male_positive_tuples = op.filter("WhyN", male_positive_tuples_sex, "PINCP", ">=", 20000.0) 
            female_positive_tuples_sex = op.filter("WhyN", filtered_df, "SEX", "==", 2.0)
            female_positive_tuples = op.filter("WhyN", female_positive_tuples_sex, "PINCP", ">=", 20000.0) 
            male_count_tuples = op.filter("WhyN", filtered_df, "SEX", "==", 1.0) #count with filter condition
            female_count_tuples = op.filter("WhyN", filtered_df, "SEX", "==", 2.0) #count with filter condition

            male_positive = len(male_positive_tuples)
            female_positive = len(female_positive_tuples)
            male_count = len(male_count_tuples)
            female_count = len(female_count_tuples) 
            
            property_num = 2 # -0.3 <= float(SPD) <= 0.2       
            male_positive_tuples_sex = op.filter("WhyN", filtered_df, "RAC1P", "==", 1.0) 
            male_positive_tuples = op.filter("WhyN", male_positive_tuples_sex, "PINCP", ">=", 50000.0) 
            female_positive_tuples_sex = op.filter("WhyN", filtered_df, "RAC1P", "==", 2.0)
            female_positive_tuples = op.filter("WhyN", female_positive_tuples_sex, "PINCP", ">=", 50000.0) 
            male_count_tuples = op.filter("WhyN", filtered_df, "RAC1P", "==", 1.0) #count with filter condition
            female_count_tuples = op.filter("WhyN", filtered_df, "RAC1P", "==", 2.0) #count with filter condition

            male_positive = len(male_positive_tuples)
            female_positive = len(female_positive_tuples)
            male_count = len(male_count_tuples)
            female_count = len(female_count_tuples) 
            '''   
            
            #For Healthcare -------------------------------------------------------------------------

            male_positive_tuples_sex = op.filter("WhyN", filtered_df, "race", "==", 1) 
            male_positive_tuples = op.filter("WhyN", male_positive_tuples_sex, 'label', "==", 1) 
 

            female_positive_tuples_sex = op.filter("WhyN", filtered_df, "race", "==", 2)
            female_positive_tuples = op.filter("WhyN", female_positive_tuples_sex, "label", "==", 1) 

            male_count_tuples = op.filter("WhyN", filtered_df, "race", "==", 1) #count with filter condition
            female_count_tuples = op.filter("WhyN", filtered_df, "race", "==", 2) #count with filter condition
            
            male_positive = len(male_positive_tuples)
            female_positive = len(female_positive_tuples)
            male_count = len(male_count_tuples)
            female_count = len(female_count_tuples)
            
            '''
            property_num = 2 #-0.3 <= float(SPD) <= 0.2
            male_positive_tuples_sex = op.filter("WhyN", filtered_df, "age-group", "==", "group1") 
            male_positive_tuples = op.filter("WhyN", male_positive_tuples_sex, 'label', "==", True) 
 

            female_positive_tuples_sex = op.filter("WhyN", filtered_df, "age-group", "==", "group2")
            female_positive_tuples = op.filter("WhyN", female_positive_tuples_sex, "label", "==", True) 

            male_count_tuples = op.filter("WhyN", filtered_df, "age-group", "==", "group1") #count with filter condition
            female_count_tuples = op.filter("WhyN", filtered_df, "age-group", "==", "group2") #count with filter condition
            
            male_positive = len(male_positive_tuples)
            female_positive = len(female_positive_tuples)
            male_count = len(male_count_tuples)
            female_count = len(female_count_tuples)   
            
            # End Health ---------------------------------------------------------------------------
            
            # For TPC-H ----------------------------------------------------------------------------
            
            property_num = 1
            sum_supplier = sum(filtered_df['s_acctbal']) 
            count_supplier = len(filtered_df['s_suppkey']) 
            try:
                constraint = round(sum_supplier/count_supplier, 5)
                if 2000 <= constraint <= 5000:
                    possibleRefinments.append({'combination': combination, 'constraint': constraint})
            except ZeroDivisionError:
                pass
            
            property_num = 2
            sum_supplier = sum(filtered_df['s_acctbal']) 
            count_supplier = len(filtered_df['s_suppkey']) 
            try:
                constraint = round(sum_supplier/count_supplier, 5)
                if constraint <= 7000:
                    possibleRefinments.append({'combination': combination, 'constraint': constraint})
            except ZeroDivisionError:
                pass
            # ---------------------------------------------------------------------------------------
            '''
            check_counter+=1
            if (male_count == 0 and female_count != 0):
                SPD = round(0 - (female_positive / female_count), 4) #arithmatic expression
            elif (female_count ==0 and male_count != 0):
                SPD = round((male_positive / male_count) - 0, 4) #arithmatic expression
            elif (female_count ==0 and male_count == 0):
                SPD = 0
            else:
            
            #try:
                SPD = round((male_positive / male_count) - (female_positive / female_count), 4) #arithmatic expression
            if constraint[0] <= SPD <= constraint[1]: 
                satisfied = ({'combination': conditions, 'SPD': SPD, "Similarity": similarity})
            #except ZeroDivisionError:
                #pass
        return satisfied, check_counter, counter
