from itertools import product
#from turtle import distance
#from Manhattan_distance import Manhattan_distance
from itertools import product

class predicatesPossibleValues:

    def calculate_combinations(self, predicates):
        num_combinations = 1
        for predicate in predicates:
            num_combinations *= len(predicate['values'])
        return num_combinations

    def numerical_att_dist(self, possible_refinements, user_predicate_list):
        # Example Manhattan distance calculation
        updated_refinements = []
        
        for refinement in possible_refinements:
            # Ensure that refinement is a dictionary
            if isinstance(refinement, dict):
                distance = 0
                # Iterate through each predicate in the refinement and compare with user predicates
                for pred in refinement.get('refinements', []):  # Ensures 'refinements' key exists
                    for user_pred in user_predicate_list:
                        if pred['column'] == user_pred['column']:
                            distance += self.calculate(pred['value'], user_pred['value'])
                # Create a new dictionary including the distance
                refinement_with_distance = {
                    **refinement,  # Spread the existing refinement dictionary
                    'distance': distance  # Add the new distance key
                }
                updated_refinements.append(refinement_with_distance)
            else:
                raise TypeError("Refinement should be a dictionary")

        return updated_refinements

    def calculate(self, value1, value2):
        return abs(value1 - value2)

    def generate_possible_refinments_similarity(self, all_pred_possible_values, UserpredicateList):
        possible_refinements = []

        # Extract information about each predicate
        predicates = [{'predicate': pred_info['predicate'], 'values': pred_info['values']} for pred_info in all_pred_possible_values]

        # Generate all combinations of values for all predicates
        combinations = product(*[predicate['values'] for predicate in predicates])

        # Construct possible refinements based on combinations
        for combination in combinations:
            refinement = {
            'refinements': [],
            'distance': 0  # Initialize distance
            }
            for pred_info, val in zip(predicates, combination):
                predicate_info = pred_info['predicate']
                refinement['refinements'].append ({
                    'column': predicate_info['column'],
                    'operator': predicate_info['operator'],
                    'value': val
                })


            # For demonstration, just add up differences between matched user predicates
            for pred in refinement['refinements']:
                for user_pred in UserpredicateList:
                    if pred['column'] == user_pred[0]:
                        pred_distance = self.calculate(pred['value'], user_pred[2])
                        refinement['distance'] += pred_distance
        
            possible_refinements.append(refinement)

        # Sort possible refinements by distance
        sorted_possible_refinements = sorted(
        possible_refinements,
        key=lambda x: [x['distance']] + [refinement['value'] for refinement in x['refinements']])

        return sorted_possible_refinements

    def normalize_values(self, all_values):
        """
        Normalize values to a range [0, 1].
        """
        min_val = min(all_values)
        max_val = max(all_values)
        if max_val == min_val:  # Prevent division by zero
            return {val: 0.5 for val in all_values}  # If all values are the same, set them to the midpoint
        return {val: (val - min_val) / (max_val - min_val) for val in all_values}

    def generate_possible_refinments_similarity1(self, all_pred_possible_values, UserpredicateList):
        possible_refinements = []

        # Extract information about each predicate
        predicates = [{'predicate': pred_info['predicate'], 'values': pred_info['values']} for pred_info in all_pred_possible_values]

        # Normalize values for each predicate
        normalized_values = {}
        for predicate in predicates:
            column_name = predicate['predicate']['column']
            normalized_values[column_name] = self.normalize_values(predicate['values'])

        # Generate all combinations of values for all predicates
        combinations = product(*[predicate['values'] for predicate in predicates])

        # Construct possible refinements based on combinations
        for combination in combinations:
            refinement = {
                'refinements': [],
                'distance': 0  # Initialize distance
            }
            for pred_info, val in zip(predicates, combination):
                predicate_info = pred_info['predicate']
                refinement['refinements'].append({
                    'column': predicate_info['column'],
                    'operator': predicate_info['operator'],
                    'value': val
                })

            # Calculate the normalized distance for the refinement
            for pred in refinement['refinements']:
                for user_pred in UserpredicateList:
                    if pred['column'] == user_pred[0]:
                        # Normalize the user predicate value
                        normalized_user_value = normalized_values[pred['column']].get(user_pred[2], 0)
                        # Get the normalized value of the current refinement
                        normalized_refinement_value = normalized_values[pred['column']].get(pred['value'], 0)
                        # Calculate normalized distance
                        pred_distance = self.calculate(normalized_refinement_value, normalized_user_value)
                        refinement['distance'] += pred_distance

            possible_refinements.append(refinement)

        # Sort possible refinements by distance
        sorted_possible_refinements = sorted(
            possible_refinements,
            key=lambda x: [x['distance']] + [refinement['value'] for refinement in x['refinements']]
        )

        return sorted_possible_refinements



