from unittest import skip
import pandas as pd
import re
import numpy as np
from ExpressionNode import ExpressionNode



class constraint_evaluation1:
    def __init__(self):
        self.precedence = {
            '+': 1,
            '-': 1,
            '*': 2,
            '/': 2
        }
    # Method to extract boundary values from the expression
    def extract_boundary_values(self, expression):

        # Regex pattern to match floating-point numbers or integers in the expression
        pattern = r'[-+]?\d*\.\d+|\d+'
        matches = re.findall(pattern, expression)

        if len(matches) < 2:
            raise ValueError("Expression must contain at least two boundary values (e.g., '0.0 <= expression <= 0.2')")
        
        # Convert matches to floats and return them
        lower_bound = float(matches[0])
        upper_bound = float(matches[-1])
        return lower_bound, upper_bound

    # Function to extract and evaluate the core part of the expression (e.g., agg1 / agg2 - agg3 / agg4)
    def extract_core_expression(self, expression):
        # Extract the core part of the expression (inside parentheses or arithmetic expressions)
        match = re.search(r'<=\s*(.*)\s*<=', expression)
        if match:
            return match.group(1)
        else:
            # If there's no comparison in the expression, return the full expression
            return expression
    def sum_values(self, values):
        """Helper function to sum values, handling possible multi-dimensional arrays."""
        if isinstance(values[0], (np.ndarray, list)):
            # If the values are arrays or lists, flatten them first and sum the result
            return sum([np.sum(val) for val in values])
        else:
            # Otherwise, sum scalar values normally
            return np.sum(values)


    def extract_column_names_from_expression(self, expression):
        # Use regex to find all occurrences of 'agg' followed by numbers (e.g., 'agg1', 'agg2', etc.)
        pattern = r'agg\d+'
        # Find all matches in the expression
        matches = re.findall(pattern, expression)
        # Return the list of unique column/aggregation names
        return list(set(matches))

    def calculate_expression_partially(self, filtered_df, conditions, agg_counter, expression, type, similarity, most_similar_values=0):
        satisfied = []  
        not_satisfied = False
        #print(conditions)

        data = pd.DataFrame(filtered_df)

        if data.empty:
            not_satisfied = True
            return satisfied, agg_counter, not_satisfied, " "
        else:
            agg_counter += 1
            # Initialize dictionaries for lower and upper bounds
            lower_bounds = {}
            upper_bounds = {}

            # Extract boundary values from the expression
            lower_bound_value, upper_bound_value = self.extract_boundary_values(expression)

            # Dynamically extract aggregation column names from the expression
            agg_columns = self.extract_column_names_from_expression(expression)

            # Initialize lower and upper bounds for each aggregation column
            for agg in agg_columns:
                lower_bounds[agg] = 0
                upper_bounds[agg] = 0

            # Iterate over each row in the DataFrame
            for _, row in data.iterrows():
                if row['Satisfy'] == 'Full':
                    # Use the values as both lower and upper bounds
                    for agg in agg_columns:
                        lower_bounds[agg] += row[agg]
                        upper_bounds[agg] += row[agg]
                elif row['Satisfy'] == 'Partial':
                    # Use values as upper bounds, and 0 as lower bounds
                    for agg in agg_columns:
                        upper_bounds[agg] += row[agg]
            #print(lower_bounds, upper_bounds)

            #try: 
            core_expression = self.extract_core_expression(expression)
            # Parse the expression into a tree
            expression_tree = self.parse_expression_to_tree(core_expression)
            
            # Evaluate the expression tree using interval arithmetic
            result_lower, result_upper = self.evaluate_expression_tree(expression_tree, lower_bounds, upper_bounds)  
            result_lower = round(result_lower,4)
            result_upper = round(result_upper,4)
            Range_Result = [round(result_lower, 4), round(result_upper, 4)]
            #print(Range_Result)
            # Evaluate whether the result satisfies the condition
            #if result_lower != None and result_upper != None:
            if type == "ranges":
                # Check if the result satisfies the boundary condition fully
                if lower_bound_value <= result_lower and result_upper <= upper_bound_value:
                    satisfied = {
                        "Result": [round(result_lower, 4), round(result_upper, 4)],  # Store result as a list
                        "Range Satisfaction": "Full",
                    }
                    concrete_counts = 1
                    # Dynamically add each condition and corresponding most_similar concrete values
                    for i in range(len(conditions)):
                        satisfied[f"condition{i + 1}"] = conditions[i]['range']

                    satisfied["concrete_counts"]= concrete_counts
                elif (
                    (lower_bound_value <= result_lower <= upper_bound_value and upper_bound_value < result_upper) or
                    (lower_bound_value <= result_upper <= upper_bound_value and lower_bound_value > result_lower) or
                    (result_lower <= lower_bound_value and lower_bound_value < result_upper <= upper_bound_value) or
                    (result_lower <= lower_bound_value and result_upper >= upper_bound_value)
                ):
                    satisfied = {
                        "Result": [round(result_lower, 4), round(result_upper, 4)],  # Store result as a list
                        "Range Satisfaction": "Partial"
                    }
                    concrete_counts = 1
                    # Dynamically add each condition and corresponding most_similar concrete values
                    for i in range(len(conditions)):
                        satisfied[f"condition{i + 1}"] = conditions[i]['range']
                else:
                    not_satisfied = True
                        
            #except ZeroDivisionError:
                #pass

            return satisfied, agg_counter, not_satisfied, Range_Result

    def calculate_expression_partially1(self, filtered_df, condition1, condition2, agg_counter, expression, type, similarity, most_similar1=0, most_similar2=0):
        satisfied = []  

        data = pd.DataFrame(filtered_df)

        if data.empty:
            return satisfied, agg_counter
        else:
            #agg_counter += 1
            # Initialize dictionaries for lower and upper bounds
            lower_bounds = {}
            upper_bounds = {}

            # Extract boundary values from the expression
            lower_bound_value, upper_bound_value = self.extract_boundary_values(expression)

            # Dynamically extract aggregation column names from the expression
            agg_columns = self.extract_column_names_from_expression(expression)

            # Initialize lower and upper bounds for each aggregation column
            for agg in agg_columns:
                lower_bounds[agg] = 0
                upper_bounds[agg] = 0

            # Iterate over each row in the DataFrame
            for _, row in data.iterrows():
                if row['Satisfy'] == 'Full':
                    # Use the values as both lower and upper bounds
                    for agg in agg_columns:
                        lower_bounds[agg] += row[agg]
                        upper_bounds[agg] += row[agg]
                elif row['Satisfy'] == 'Partial':
                    # Use values as upper bounds, and 0 as lower bounds
                    for agg in agg_columns:
                        upper_bounds[agg] += row[agg]
            #print(lower_bounds, upper_bounds)

            #try: 
            core_expression = self.extract_core_expression(expression)
            # Parse the expression into a tree
            expression_tree = self.parse_expression_to_tree(core_expression)
            
            # Evaluate the expression tree using interval arithmetic
            result_lower, result_upper = self.evaluate_expression_tree(expression_tree, lower_bounds, upper_bounds)  
            result_lower = round(result_lower,4)
            result_upper = round(result_upper,4)

            #print("[", condition1, "]", condition2, "Result: [", round(result_lower,4), round(result_upper,4), "]") 

            # Evaluate whether the result satisfies the condition
            #if result_lower != None and result_upper != None:
            if type == "partial":
                if lower_bound_value <= result_lower and result_upper <= upper_bound_value:
                    satisfied = {
                        "condition1": condition1,
                        "condition2": condition2, 
                        "Result": [round(result_lower,4), round(result_upper,4)],  # Store as a list
                        "Range Satisfaction": "Full"
                    }  
                    #print("condition1", condition1, "condition2", condition2, "Result: [", round(result_lower,4), round(result_upper,4), "]", "Full") 
                elif (lower_bound_value <= result_lower <= upper_bound_value and upper_bound_value < result_upper) or(
                    lower_bound_value <= result_upper <= upper_bound_value and lower_bound_value > result_lower) or (
                    result_lower <= lower_bound_value and lower_bound_value < result_upper <= upper_bound_value) or (
                    result_lower <= lower_bound_value and  result_upper >= upper_bound_value):
                    satisfied = {
                        "condition1": condition1, 
                        "condition2": condition2, 
                        #"condition3": condition3, 
                        "Result": [round(result_lower,4), round(result_upper,4)],  # Store as a list
                        "Range Satisfaction": "Partial"
                    }
                    #print("condition1", condition1, "condition2", condition2, "Result: [", round(result_lower,4), round(result_upper,4), "]", "Partial")   
                #else:
                    #print("condition1", condition1, "condition2", condition2, "Result: [", round(result_lower,4), round(result_upper,4), "]", "Not")   

            elif type == "ranges":
                if lower_bound_value <= result_lower and result_upper <= upper_bound_value:
                    satisfied = {
                        "condition1": condition1, "Concrete Vlaues1": most_similar1,
                        "condition2": condition2, "Concrete Vlaues2": most_similar2,
                        #"condition3": condition3, "Concrete Vlaues3": most_similar3,
                        "Result": [round(result_lower,4), round(result_upper,4)],  # Store as a list
                        "Range Satisfaction": "Full"
                    }  
                    #print("condition1", condition1, "condition2", condition2, "Result: [", round(result_lower,4), round(result_upper,4), "]", "Full") 
                elif (lower_bound_value <= result_lower <= upper_bound_value and upper_bound_value < result_upper) or(
                    lower_bound_value <= result_upper <= upper_bound_value and lower_bound_value > result_lower) or(
                    result_lower <= lower_bound_value and lower_bound_value < result_upper <= upper_bound_value) or (
                    result_lower <= lower_bound_value and  result_upper >= upper_bound_value):
                    satisfied = {
                        "condition1": condition1, "Concrete Vlaues1": most_similar1,
                        "condition2": condition2, "Concrete Vlaues2": most_similar2,
                        #"condition3": condition3, "Concrete Vlaues3": most_similar3,
                        "Result": [round(result_lower,4), round(result_upper,4)],  # Store as a list
                        "Range Satisfaction": "Partial"
                    } 
                    #print("condition1", condition1, "condition2", condition2, "Result: [", round(result_lower,4), round(result_upper,4), "]", "Partial") 
                #else:
                    #print("condition1", condition1, "condition2", condition2, "Result: [", round(result_lower,4), round(result_upper,4), "]", "Not")   
                          

            #except ZeroDivisionError:
                #pass

            return satisfied, agg_counter

    def parse_expression_to_tree(self, expression):
        """
        Parses a mathematical expression string into a binary expression tree.
        Supports +, -, *, / operators and parentheses ().
        """
        # Tokenize the expression while keeping operators and parentheses
        tokens = re.findall(r'\d+\.\d+|\d+|[+\-*/()]|agg\d+', expression.replace(' ', ''))
        return self.build_tree_from_tokens(tokens)

    def build_tree_from_tokens(self, tokens):
        def parse_tokens_to_expression(tokens):
            # Stack to store the operands (ExpressionNodes)
            operand_stack = []
            # Stack to store operators and their precedence
            operator_stack = []

            def apply_operator():
                """Helper function to apply the operator at the top of the stack."""
                operator = operator_stack.pop()
                right = operand_stack.pop()  # Ensure right operand is popped first
                left = operand_stack.pop()   # Then pop the left operand
                # Create an ExpressionNode with the operator and operands in correct order
                operand_stack.append(ExpressionNode(operator, left, right))

            i = 0
            while i < len(tokens):
                token = tokens[i]

                if token.isdigit() or re.match(r'agg\d+', token):  # Operand (number or aggX)
                    operand_stack.append(ExpressionNode(token))

                elif token == '(':
                    # Find the matching closing parenthesis and recurse
                    depth = 1
                    j = i + 1
                    while j < len(tokens) and depth > 0:
                        if tokens[j] == '(':
                            depth += 1
                        elif tokens[j] == ')':
                            depth -= 1
                        j += 1
                    # Recur for the expression inside parentheses
                    operand_stack.append(parse_tokens_to_expression(tokens[i + 1:j - 1]))
                    i = j - 1  # Skip over the entire parenthesis expression

                elif token in self.precedence:
                    # Process operator based on precedence
                    while (operator_stack and operator_stack[-1] in self.precedence and
                        self.precedence[operator_stack[-1]] >= self.precedence[token]):
                        apply_operator()
                    operator_stack.append(token)  # Push the current operator

                i += 1

            # Apply remaining operators in the stack
            while operator_stack:
                apply_operator()

            return operand_stack[0]  # The final expression tree is the last operand

        return parse_tokens_to_expression(tokens)


    def evaluate_expression_tree(self, node, local_env_lower, local_env_upper):
        """
        Recursively evaluates an expression tree with interval arithmetic.
        """
        if node is None:
            return None, None

        # If the node is a leaf (it contains a variable like 'agg1'), return the corresponding values from the environment
        if node.left is None and node.right is None:  # Leaf node (operand)
            if node.value in local_env_lower:
                return local_env_lower[node.value], local_env_upper[node.value]
            else:
                raise ValueError(f"Unknown operand: {node.value}")

        # Otherwise, this is an operator node, so we need to evaluate the left and right children
        left_lower, left_upper = self.evaluate_expression_tree(node.left, local_env_lower, local_env_upper)
        right_lower, right_upper = self.evaluate_expression_tree(node.right, local_env_lower, local_env_upper)
        # Apply interval arithmetic at this node based on the operator
        return self.apply_interval_arithmetic(left_lower, left_upper, right_lower, right_upper, node.value)

    def evaluate_interval_expression(self, expression, local_env_lower, local_env_upper):
        # Split the expression into operands and operators
        # For simplicity, we assume the expression contains only basic arithmetic (e.g., "agg1 / agg2 - agg3 / agg4")
        tokens = re.split(r'([+\-*/])', expression)
        operands = [token.strip().replace('(', '').replace(')', '') for token in tokens if token.strip() not in '+-*/']
        operators = [token.strip() for token in tokens if token.strip() in '+-*/']
        
        lower_values = [local_env_lower[operand] for operand in operands]
        
        upper_values = [local_env_upper[operand] for operand in operands]
        
        # Initialize the first sub-expression result with the first two operands
        lower_result, upper_result = lower_values[0], upper_values[0]

        # Process each operator in sequence, combining the results step-by-step
        for i, operator in enumerate(operators):
            # Apply interval arithmetic between lower and upper bounds for each operator
            lower_result, upper_result = self.apply_interval_arithmetic(lower_result, upper_result, lower_values[i + 1], upper_values[i + 1], operator)

        return lower_result, upper_result

    def apply_interval_arithmetic(self, lower1, upper1, lower2, upper2, operator):
        if operator == '+':
            lower_result = lower1 + lower2
            upper_result = upper1 + upper2

        elif operator == '-':
            lower_result = lower1 - upper2
            upper_result = upper1 - lower2

        elif operator == '*':
            #If numbers are positive this is correct
            lower_result = lower1 * lower2
            upper_result = upper1 * upper2
            #If negative it will be different, Fix it
            

        elif operator == '/':
            if lower2 == 0 and upper2 ==0:
                upper_result = 0
                lower_result = 0
            
            if lower2 <= 0 and upper2 >=0: #Fairness 
                upper_result = 1
                lower_result = 0
            
            #elif lower2 == 0: #Others
                #upper_result =  upper1 
                #lower_result = lower1 / upper2 
            #elif upper2 ==0:
                #lower_result = lower1
                #upper_result = upper1 / lower2
            else:
                upper_result = upper1 / lower2
                lower_result = lower1 / upper2                       

        return lower_result, upper_result
