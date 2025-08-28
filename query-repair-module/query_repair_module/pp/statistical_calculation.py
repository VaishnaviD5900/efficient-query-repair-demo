import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import re
import os

class statistical_calculation:
    def __init__(self):
        self.column_set = set()


    def evaluate_aggregation1(self, df, expression):
        """
        Evaluate aggregation expressions, supporting both conditions and column-based aggregations.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            expression (str): The aggregation expression in the format func("condition") 
                              or func("condition", "column"), or func("column").

        Returns:
            result: The result of the aggregation.
        """
        def eval_cond(df, cond):
            """
            Evaluate a condition and return the filtered DataFrame.
            """
            cond = cond.replace('"', '')  # Remove quotes for direct column access
            # Split condition by logical operators (and/or)
            conditions = re.split(r'\s+(and|or)\s+', cond)
            mask = np.ones(len(df), dtype=bool)
            
            # Define operator mappings
            operators = {
                '==': lambda col, val: df[col].to_numpy() == float(val),
                '>=': lambda col, val: df[col].to_numpy() >= float(val),
                '<=': lambda col, val: df[col].to_numpy() <= float(val),
                '!=': lambda col, val: df[col].to_numpy() != float(val),
                '>': lambda col, val: df[col].to_numpy() > float(val),
                '<': lambda col, val: df[col].to_numpy() < float(val),
            }

            logical_operator = None

            # Apply conditions and handle logical operators
            for condition in conditions:
                if condition.strip() in ['and', 'or']:
                    logical_operator = condition.strip()
                    continue

                for operator, func in operators.items():
                    if operator in condition:
                        col_name, value = condition.split(operator)
                        col_name = col_name.strip()
                        value = value.strip()
                        
                        # Add column to set for tracking
                        self.column_set.add(col_name)

                        if logical_operator == 'and' or logical_operator is None:
                            mask &= func(col_name, value)
                        elif logical_operator == 'or':
                            mask |= func(col_name, value)

                        break

            return df[mask]

        # Define aggregation mappings
        aggregation_functions = {
            'count': lambda cond=None, col=None: len(df[col]) if col else eval_cond(df, cond).shape[0],
            'sum': lambda cond=None, col=None: df[col].sum() if col and not cond else eval_cond(df, cond)[col].sum(),
            'mean': lambda cond=None, col=None: df[col].mean() if col and not cond else eval_cond(df, cond)[col].mean(),
            'min': lambda cond=None, col=None: df[col].min() if col and not cond else eval_cond(df, cond)[col].min(),
            'max': lambda cond=None, col=None: df[col].max() if col and not cond else eval_cond(df, cond)[col].max(),
        }
        # Parse the expression
        parts = expression.split('(')
        func_name = parts[0].strip()
        args = parts[1].strip()[:-1]  # Remove trailing ")"
        args = [arg.strip().replace('"', '') for arg in args.split(',')]

        # Evaluate based on number of arguments
        if len(args) == 1:
            # Single argument (e.g., sum("p_retailprice"))
            if args[0] in df.columns:  # If argument is a column
                self.column_set.add(args[0])  # Track column usage
                result = aggregation_functions[func_name](col=args[0])
            else:  # If argument is a condition
                result = aggregation_functions[func_name](cond=args[0])
        elif len(args) == 2:
            # Two arguments (e.g., sum("condition", "column"))
            self.column_set.add(args[1])  # Track column usage
            result = aggregation_functions[func_name](cond=args[0], col=args[1])
        else:
            raise ValueError(f"Invalid aggregation expression: {expression}")

        return result

    def evaluate_aggregation(self, df, expression):
        # Optimized condition parsing using vectorized operations with NumPy
        def eval_cond(df, cond):
            cond = cond.replace('"', '')  # Remove quotes for direct column access

            # Split condition by logical operators (and/or)
            conditions = re.split(r'\s+(and|or)\s+', cond)

            # Boolean mask for DataFrame filtering (using NumPy for faster operations)
            mask = np.ones(len(df), dtype=bool)

            operators = {
                '==': lambda col, val: df[col].to_numpy() == float(val),
                '>=': lambda col, val: df[col].to_numpy() >= float(val),
                '<=': lambda col, val: df[col].to_numpy() <= float(val),
                '!=': lambda col, val: df[col].to_numpy() != float(val),
                '>': lambda col, val: df[col].to_numpy() > float(val),
                '<': lambda col, val: df[col].to_numpy() < float(val),
            }

            logical_operator = None

            # Apply conditions vectorized and handle logical operators
            for condition in conditions:
                if condition.strip() in ['and', 'or']:
                    logical_operator = condition.strip()
                    continue  # Skip logical operators for now

                for operator, func in operators.items():
                    if operator in condition:
                        col_name, value = condition.split(operator)
                        col_name = col_name.strip()
                        value = value.strip()

                        if logical_operator == 'and' or logical_operator is None:
                            mask &= func(col_name, value)
                        elif logical_operator == 'or':
                            mask |= func(col_name, value)

                        break

            return df[mask]

        # Define aggregation mappings with more vectorization
        aggregation_functions = {
            'count': lambda x: eval_cond(df, x).shape[0],
            'sum': lambda x, col: eval_cond(df, x)[col].sum(),
            'mean': lambda x, col: eval_cond(df, x)[col].mean(),
        }

        # Parse the expression to find which aggregation to apply
        parts = expression.split('(')
        func_name = parts[0].strip()
        args = parts[1].strip()[:-1]  # Remove trailing ")"
        args = [arg.strip() for arg in args.split(',')]

        if len(args) == 1:
            result = aggregation_functions[func_name](args[0])
        elif len(args) == 2:
            args[1] = args[1].replace('"', '').strip()  # Clean up column name
            result = aggregation_functions[func_name](*args)

        return result

    def statistical_calculation(self, cluster_tree, df, aggregations, predicates_number, constraint_columns, dataName, dataSize, query_num):
        statistical_tree = []

        # Define the dynamic file name
        file_name = f"statistical_info_Q{query_num}_{dataName}_{dataSize}.csv"

        # Check if the file exists'''
        '''
        if os.path.exists(file_name):
            print(f"File '{file_name}' already exists. Reading from the file...")
            df_statistical_info = pd.read_csv(file_name)
            return df_statistical_info
        '''
        # Parallelize processing using ThreadPoolExecutor
        def process_cluster(clusters):
            data_points_array = np.array(clusters['Data points'])

            # Slice the array starting from predicates_number to get constraint points
            sliced_data_points_array = data_points_array[:, predicates_number:]
            df_sliced = pd.DataFrame(sliced_data_points_array, columns=constraint_columns)

            box = self.points_bounds(data_points_array)
            count = self.count(len(clusters['Data points']))

            calculation_info = {
                'Predicates points': data_points_array,
                'Level': clusters['Level'],
                'Cluster Id': clusters['Cluster Id'],
                'Parent level': clusters['Parent level'],
                'Parent cluster': clusters['Parent cluster'],
                'Data_Min': box['min'],
                'Data_Max': box['max'],
                'Count': count['count'],
            }

            # Evaluate each aggregation for this cluster
            for idx, (agg_name, agg_expr) in enumerate(aggregations.items(), start=1):
                result = self.evaluate_aggregation1(df_sliced, agg_expr)
                calculation_info[f'agg{idx}'] = round(result, 2)

            return calculation_info

        # Use ThreadPoolExecutor for parallel processing of clusters
        with ThreadPoolExecutor() as executor:
            statistical_tree = list(executor.map(process_cluster, cluster_tree))

        # Create and save DataFrame (delaying I/O to optimize performance)
        df_statistical_info = pd.DataFrame(statistical_tree)

        # Write the DataFrame to a CSV file with the dynamic file name
        df_statistical_info.to_csv(file_name, index=False)

        return statistical_tree

    def points_bounds(self, cluster_points):
        np_data = np.array(cluster_points)
        return {'min': np.min(np_data, axis=0).tolist(), 'max': np.max(np_data, axis=0).tolist()}

    def count(self, num_points):
        return {'count': num_points}

