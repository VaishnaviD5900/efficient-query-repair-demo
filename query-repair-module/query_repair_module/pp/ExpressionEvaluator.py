import re

class ExpressionEvaluator:

    def __init__(self):
        self.column_set = set()  # This will store all unique column names accessed

    def evaluate_aggregation(self, df, expression):
        # Helper function to parse and evaluate conditions
        def eval_cond(df, cond):
            cond = cond.replace('"', '')  # Remove quotes for direct column access
            
            # Attempt to find all column names using a simple regex pattern
            columns = re.findall(r'\b\w+\b(?=\s*==|\s*>=|\s*<=|\s*!=|\s*<|\s*>)', cond)
            unique_columns = list(set(columns))  # Remove duplicates
            self.column_set.update(unique_columns)  # Update the class-wide column set

            return df.query(cond), unique_columns 

        # Define aggregation mappings
        aggregation_functions = {
            'count': lambda x: eval_cond(df, x)[0].shape[0],
            'sum': lambda x, col: eval_cond(df, x)[0][col].sum(),
            'mean': lambda x, col: eval_cond(df, x)[0][col].mean(),
            # Add more aggregation functions as needed
        }
        
        # Parse the expression to find which aggregation to apply
        # This is a simplistic parser, assumes format func("condition") or func("condition", "column")
        parts = expression.split('(')
        func_name = parts[0].strip()
        args = parts[1].strip()[:-1]  # remove trailing ")"
        args = [arg.strip() for arg in args.split(',')]

        if len(args) == 1:
            result = aggregation_functions[func_name](args[0])
        elif len(args) == 2:
            args[1] = args[1].replace('"', '').strip()  # clean up column name
            result = aggregation_functions[func_name](*args)

        return result
    
    
    def get_columns_used(self):
        return list(self.column_set)  # Return a list of all unique columns used

    

    


