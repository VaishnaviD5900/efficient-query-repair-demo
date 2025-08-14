

class operators:

    def apply_operator_bruteForce(self, row_value, condition_value, operator):
        # Define a dictionary mapping operators to their respective lambda functions
        operators = {
            '<': lambda x, y: x < y,
            '<=': lambda x, y: x <= y,
            '>': lambda x, y: x > y,
            '>=': lambda x, y: x >= y,
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
        }
        
        # Check if the operator is valid and apply the operation
        if operator in operators:
            return operators[operator](row_value, condition_value)
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def apply_operator(self, Min_value, Max_value, condition_value, operator, type):
        # Define a dictionary mapping operators to their respective lambda functions
        operators = {
            '<': lambda x, y: x < y,
            '<=': lambda x, y: x <= y,
            '>': lambda x, y: x > y,
            '>=': lambda x, y: x >= y,
            '==': lambda x, y, z: x == z and y == z, # All points are exactly equal
            '!=': lambda x, y, z: x != z and y != z # All points are not equal
        }

    
        # Check if the operator is valid and apply the operation
        if operator == '>=' and type == "Full":
            return operators[operator](Min_value, condition_value)
        elif operator == '<=' and type == "Full":
            return operators[operator](Max_value, condition_value)
        elif operator == '>' and type == "Full":
            return operators[operator](Min_value, condition_value)
        elif operator == '<' and type == "Full":
            return operators[operator](Max_value, condition_value)
        elif operator == '==' and type == "Full":
            return operators[operator](Min_value, Max_value, condition_value)
        elif operator == '!=' and type == "Full":
            return operators[operator](Min_value, Max_value, condition_value)

        '''
        operators_partial = {
            '==': lambda x_min, x_max, y: (x_min <= y and x_max > y) or (x_min < y and x_max >= y), #one of min and max is == and the other is not
            '!=': lambda x_min, x_max, y: (x_min != y and x_max == y) or (x_min == y and x_max != y)  #one of min and max is != and the other is ==
        }
        if operator == '>=' and type == "Partial":
            return operators[operator](Max_value, condition_value)
        elif operator == '<=' and type == "Partial":
            return operators[operator](Min_value, condition_value)
        elif operator == '>' and type == "Partial":
            return operators[operator](Max_value, condition_value)
        elif operator == '<' and type == "Partial":
            return operators[operator](Min_value, condition_value)

        elif operator == '==' and type == "Partial":
            return operators_partial[operator](Min_value, Max_value, condition_value)
        elif operator == '!=' and type == "Partial":
            return operators[operator](Min_value, Max_value, condition_value)
        
        else:
            raise ValueError("Unsupported operator")
        '''

    def apply_operator_ranges(self, Min_value, Max_value, Min_condition, Max_condition, operator, type):
        # Define a dictionary mapping operators to their respective lambda functions
        operators = {
            '<': lambda x, y: x < y,
            '<=': lambda x, y: x <= y,
            '>': lambda x, y: x > y,
            '>=': lambda x, y: x >= y,
            '==': lambda a, b, x, y: a == b == x == y, #all values from cluster fulfill condition for all values from the range
            '!=': lambda a, b, x, y: (a > y or x > b) #Equivelant to (not(a <= y and x <= b))  
            #no value from the cluster can fulfill the condition for any value from the range

        }
        operators_partial = {
            '==': lambda a, b, x, y: (a <= y and x <= b), #some value from the cluster may fulfill the condition for some value from the range
            '!=': lambda a, b, x, y: (a <= y and x <= b)  #some value from the cluster may not fulfill the condition for some value from the range
        }
    
        # Check if the operator is valid and apply the operation
        if operator == '>=' and type == "Full":
            return operators[operator](Min_value, Max_condition)
        elif operator == '<=' and type == "Full":
            return operators[operator](Max_value, Min_condition)
        elif operator == '>' and type == "Full":
            return operators[operator](Min_value, Max_condition)
        elif operator == '<' and type == "Full":
            return operators[operator](Max_value, Min_condition)
        elif operator == '==' and type == "Full":
            return operators[operator](Min_value, Max_value, Min_condition, Max_condition)
        elif operator == '!=' and type == "Full":
            return operators[operator](Min_value, Max_value, Min_condition, Max_condition)

        if operator == '>=' and type == "Partial":
            return operators[operator](Max_value, Min_condition)
        elif operator == '<=' and type == "Partial":
            return operators[operator](Min_value, Max_condition)
        elif operator == '>' and type == "Partial":
            return operators[operator](Max_value, Min_condition)
        elif operator == '<' and type == "Partial":
            return operators[operator](Min_value, Max_condition)
        elif operator == '==' and type == "Partial":
            return operators_partial[operator](Min_value, Max_value, Min_condition, Max_condition)
        elif operator == '!=' and type == "Partial":
            return operators[operator](Min_value, Max_value, Min_condition, Max_condition)

        else:
            raise ValueError("Unsupported operator")


 
    
    

