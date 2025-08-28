from unittest import skip
import pandas as pd
import re
import numpy as np
from .ExpressionNode import ExpressionNode
from decimal import Decimal, InvalidOperation
import math


class constraint_evaluation_other:
    # Method to extract boundary values from the expression
    def extract_boundary_values(self, expression):
        # Regex pattern to match floating-point numbers or integers in the expression
        #pattern = r'[-+]?\d*\.\d+|\d+'
        pattern = r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'
        matches = re.findall(pattern, expression)

        if len(matches) < 2:
            raise ValueError("Expression must contain at least two boundary values (e.g., '0.0 <= expression <= 0.2')")
        # Convert matches to floats and return them
        lower_bound = Decimal(matches[0])
        upper_bound = Decimal(matches[-1])
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
    
    def apply_arithmetic_operation(self, operand1, operand2, operator):
        """Performs basic arithmetic operations safely."""
        if operator == "+":
            return operand1 + operand2
        elif operator == "-":
            return operand1 - operand2
        elif operator == "*":
            return operand1 * operand2
        elif operator == "/":
            return self.safe_div(operand1, operand2)
        else:
            raise ValueError(f"Unknown operator {operator}")

    def sum_values(self, values):
        """Helper function to sum values, handling possible multi-dimensional arrays."""
        if isinstance(values[0], (np.ndarray, list)):
            # If the values are arrays or lists, flatten them first and sum the result
            return sum([np.sum(val) for val in values])
        else:
            # Otherwise, sum scalar values normally
            return np.sum(values)

    def safe_div(self, x, y):
        """A helper function for safe division to avoid ZeroDivisionError."""
        if y != 0:
            result =  x / y 
        else: 
            result = 0
        return result  

    def parse_and_evaluate_expression(self, filtered_df, expression):
        """Evaluates the expression with proper handling of parentheses."""
        def evaluate(tokens):
            """Helper function to evaluate tokens list without parentheses."""
            stack = []
            current_value = None

            idx = 0
            while idx < len(tokens):
                token = tokens[idx]
                if token in ['+', '-', '*', '/']:
                    operator_token = token
                    #print("operator_token", operator_token)
                else:
                    if token in filtered_df.columns:
                        #print("token", token)
                        col_values = filtered_df[token].values
                        #print("col_values", col_values)

                        if token == "agg2":
                            token_value = col_values[0]
                            #print("token_value", token, token_value)
                        else:
                            token_value = self.sum_values(col_values)
                            #print("token_value", token, token_value)
                    else:
                        token_value = float(token)


                    if current_value is None:
                        current_value = token_value
                    else:
                        current_value = self.apply_arithmetic_operation(current_value, token_value, operator_token)
                
                idx += 1
            
            return current_value

        # Tokenizing the expression and handling parentheses
        def tokenize_expression(expr):
            """Tokenizes the arithmetic expression, handling parentheses."""
            tokens = re.findall(r'[\w\.]+|[\+\-\*/\(\)]', expr)
            return tokens
        
        tokens = tokenize_expression(expression)
        stack = []

        # Process the tokens with a stack to evaluate expressions inside parentheses first
        output = []
        for token in tokens:
            if token == "(":
                stack.append(output)
                output = []
            elif token == ")":
                result = evaluate(output)
                output = stack.pop()
                output.append(str(result))
            else:
                output.append(token)
        
        # Finally evaluate the expression outside parentheses
        return evaluate(output)
    
    def safe_decimal(self, value):
       """Convert value to Decimal, handling NaN."""
       try:
           return Decimal(str(value)) if not math.isnan(value) else None
       except (InvalidOperation, ValueError, TypeError):
           return None
 
    def evaluate_constraint1(self, filtered_df, expression, conditions, agg_counter, similarity, type, concrete_values=None):
        #print(conditions)
        satisfied = []
        Not_satisfied = False
        result = []
        np.seterr(invalid='ignore')
        satisfies_all = False

        data = pd.DataFrame(filtered_df)
                    
        if data.empty:
            Not_satisfied = True
            return satisfied, agg_counter, Not_satisfied, result
        else:
            try:
                for idx, exp in enumerate(expression):
                    # Extract boundaries
                    lower_bound, upper_bound = self.extract_boundary_values(exp)
                    core_expression = self.extract_core_expression(exp)

                    # Evaluate and append the result
                    result_value = round(self.parse_and_evaluate_expression(data, core_expression), 10)
                    #print(result_value)
                    result.append(result_value)
                    lower_bound = self.safe_decimal(lower_bound)
                    result_value = self.safe_decimal(result_value)
                    upper_bound = self.safe_decimal(upper_bound)
                     
                    # Check boundary conditions
                    if None not in [lower_bound, result_value, upper_bound]:
                       satisfies_all = lower_bound <= result_value <= upper_bound                      
 
                    if satisfies_all == False:
                        break

                # Construct the satisfaction result based on the type and conditions
                agg_counter += 1
                if satisfies_all:
                    if type == "ranges":
                        satisfied = {
                            "conditions": conditions,
                            "Concrete Values": concrete_values,
                            "Result": result,
                            "Similarity": similarity,
                            "Range Satisfaction": "Full"
                        }
                    else:
                        satisfied = {
                            "conditions": conditions,
                            "Result": result,
                            "Similarity": similarity,
                            "Range Satisfaction": "Full"
                        }
                else:
                    Not_satisfied = True    

            except ZeroDivisionError:
                pass

            return satisfied, agg_counter, Not_satisfied, result


    def evaluate_constraint(self, filtered_df, expression, condition1, condition2, condition3, agg_counter, similarity, type, concerete_value1=0, 
    concerete_value2=0, concerete_value3=0):
        satisfied = []
        result = None
        np.seterr(invalid='ignore')

        data = pd.DataFrame(filtered_df)
                
        if data.empty:
            return satisfied, agg_counter
        else:
            try:
                #agg_counter += 1
                # Extract boundary values from the expression
                lower_bound, upper_bound = self.extract_boundary_values(expression)

                # Evaluate the exact result of the expression (SPD or another calculation)
                # Extract the core expression and evaluate it explicitly
                core_expression = self.extract_core_expression(expression)
                result = round(self.parse_and_evaluate_expression(data, core_expression), 4)
                #print("condition1", condition1, "condition2", condition2, "Result:", result) 
            
                # Check if the result satisfies the boundary conditions
                if type == "ranges":
                    if lower_bound <= result <= upper_bound:
                        satisfied = {
                            "condition1": condition1, "Concrete Vlaues1": concerete_value1,
                            "condition2": condition2, "Concrete Vlaues2": concerete_value2,
                            "condition3": condition3, "Concrete Vlaues3": concerete_value3,
                            "Result": result,
                            "Similarity": similarity,
                            "Range Satisfaction": "Full"
                        }
                else:
                    if lower_bound <= result <= upper_bound:
                        satisfied = {
                            "condition1": condition1,
                            "condition2": condition2, 
                            "condition2": condition3, 
                            "Result": result,
                            "Similarity": similarity,
                            "Range Satisfaction": "Full"
                        }

            except ZeroDivisionError:
                pass
            #print("condition1", condition1, "condition2", condition2, "Result:", result) 
            
            return satisfied, agg_counter

    def evaluate_constraint2(self, filtered_df, expression, condition1, condition2, agg_counter, similarity, type, concerete_value1=0, 
        concerete_value2=0, concerete_value3=0):
            satisfied = []
            result = None
            np.seterr(invalid='ignore')

            data = pd.DataFrame(filtered_df)
                    
            if data.empty:
                return satisfied, agg_counter
            else:
                #try:
                    #agg_counter += 1
                    # Extract boundary values from the expression
                    lower_bound, upper_bound = self.extract_boundary_values(expression)

                    # Evaluate the exact result of the expression (SPD or another calculation)
                    # Extract the core expression and evaluate it explicitly
                    core_expression = self.extract_core_expression(expression)
                    result = round(self.parse_and_evaluate_expression(data, core_expression), 4)
                    #print("condition1", condition1, "condition2", condition2, "Result:", result) 
                
                    # Check if the result satisfies the boundary conditions
                    if type == "ranges":
                        if lower_bound <= result <= upper_bound:
                            satisfied = {
                                "condition1": condition1, "Concrete Vlaues1": concerete_value1,
                                "condition2": condition2, "Concrete Vlaues2": concerete_value2,
                                "Result": result,
                                "Similarity": similarity,
                                "Range Satisfaction": "Full"
                            }
                    else:
                        if lower_bound <= result <= upper_bound:
                            satisfied = {
                                "condition1": condition1,
                                "condition2": condition2, 
                                "Result": result,
                                "Similarity": similarity,
                                "Range Satisfaction": "Full"
                            }

                #except ZeroDivisionError:
                    #pass
                #print("condition1", condition1, "condition2", condition2, "Result:", result) 
                
                    return satisfied, agg_counter