import re

class ExpressionEvaluator1:

    def __init__(self):
        self.column_set = set()  # This will store all unique column names accessed

    def evaluate_aggregation(self, df, expression):
        """
        Evaluate the given aggregation expression on the provided DataFrame.

        Args:
            df (pd.DataFrame): DataFrame containing the data.
            expression (str): Aggregation expression in the format:
                              func("condition") or func("condition", "column").

        Returns:
            result: The result of the aggregation.
        """
        # Helper function to parse and evaluate conditions
        def eval_cond(df, cond):
            cond = cond.replace('"', '')  # Remove quotes for direct column access
            # Extract column names using a regex pattern
            columns = re.findall(r'\b\w+\b', cond)
            unique_columns = [col for col in columns if col in df.columns]  # Validate columns
            self.column_set.update(unique_columns)  # Update column set
            return df.query(cond), unique_columns

        # Define aggregation function mappings
        aggregation_functions = {
            'count': lambda cond=None, col=None: df[col].count() if col else eval_cond(df, cond)[0].shape[0],
            'sum': lambda cond=None, col=None: df[col].sum() if col else eval_cond(df, cond)[0][col].sum(),
            'mean': lambda cond=None, col=None: df[col].mean() if col else eval_cond(df, cond)[0][col].mean(),
            'min': lambda cond=None, col=None: df[col].min() if col else eval_cond(df, cond)[0][col].min(),
            'max': lambda cond=None, col=None: df[col].max() if col else eval_cond(df, cond)[0][col].max(),        
       }

        # Parse the expression
        match = re.match(r'(\w+)\((.*?)\)', expression)
        if not match:
            raise ValueError(f"Invalid aggregation expression: {expression}")

        func_name, args = match.groups()
        func_name = func_name.strip()  # Extract function name
        args = [arg.strip().replace('"', '') for arg in args.split(',')]  # Clean arguments

        # Handle different argument lengths
        if len(args) == 1:
            # Single argument (e.g., sum("p_retailprice"))
            if args[0] in df.columns:
                self.column_set.add(args[0])  # Add column directly
                result = aggregation_functions[func_name](col=args[0])  # Apply directly to column
            else:
                result = aggregation_functions[func_name](cond=args[0])  # Apply conditionally
        elif len(args) == 2:
            # Two arguments (e.g., sum("condition", "column"))
            self.column_set.add(args[1])  # Add the second argument as it's the column
            result = aggregation_functions[func_name](cond=args[0], col=args[1])
        else:
            raise ValueError(f"Invalid aggregation expression: {expression}")

        return result

    def get_columns_used(self):
        """
        Retrieve all unique column names accessed during evaluations.

        Returns:
            list: List of unique column names.
        """
        return sorted(self.column_set)  # Return a sorted list for consistency

