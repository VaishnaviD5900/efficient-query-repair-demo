from queue import Empty
from unittest import skip
import numpy as np
import math

class attributesRanges1:

    def generatePossibleValues(self, df_original, predicatesList):
        all_pred_possible_values = []
        for predicate in predicatesList:
            column_name = predicate['column']
            distinct_value = df_original[column_name].unique().tolist()

            # Append predPossibleValues to the multi-dimensional array
            all_pred_possible_values.append({'predicate': predicate, 'values': distinct_value})
        return all_pred_possible_values
    
    def calculate(self, value1, value2):
        return abs(value1 - value2)

    # Function to calculate smallest and largest distance for each range
    def calculate_distances(self, ranges, concrete_values_in_range, pred_value):
        distance_results = []
        for r, concrete_set in zip(ranges, concrete_values_in_range):
            # Find the minimum and maximum concrete values for each range
            #print(r['range'], concrete_set)
            if concrete_set:
                min_distance = min(concrete_set, key=lambda x: x['distance'])['distance']
                max_distance = max(concrete_set, key=lambda x: x['distance'])['distance']
                #min_distance = min(abs(r['range'][0] - pred_value), abs(r['range'][1] - pred_value))
                #max_distance = max(abs(r['range'][0] - pred_value), abs(r['range'][1] - pred_value))

                # Store the results
                distance_results.append({
                    'range': r['range'],
                    'min_distance': min_distance
                    #'max_distance': max_distance
                    #'Concrete Values': concrete_set
                })
        return distance_results

    def generatePossibleValues_equalWidth1(self, df_original, UserpredicateList, sorted_possible_refinments1):
        """
        Generates possible values for each predicate, sorts ranges based on the order of refinements
        in sorted_possible_refinments1, and returns the most similar value, distance, and concrete values
        from sorted_possible_refinments1 for each range.
        """
        # Multi-dimensional array to store predPossibleValues
        all_pred_possible_values = []

        # Generate possible values for each predicate
        for predicate in UserpredicateList:
            column_name = predicate[0]
            operator = predicate[1]
            pred_value = predicate[2]
            data_type = predicate[3]
            pred = df_original[column_name].unique()

            if data_type == 'numerical':
                # Handle numerical data
                min_value = np.min(pred)
                max_value = np.max(pred)

                # Use IQR to determine dynamic range size
                q1 = np.percentile(pred, 25)
                q3 = np.percentile(pred, 75)
                iqr = q3 - q1

                # Determine number of ranges based on spread
                num_values = max(1, int((max_value - min_value) / max(iqr, 1)))
                # Calculate dynamic range size
                range_size = (max_value - min_value) / num_values
                #print(len(pred), range_size)
                # Generate range tuples (start, end)
                predPossibleValues = [
                    {"range": (int(min_value + i * range_size), int(min_value + (i + 1) * range_size) - 1)}
                    for i in range(num_values)
                ]
                # Adjust the last range to include max_value
                if predPossibleValues and predPossibleValues[-1]["range"][1] < max_value:
                    last_range = predPossibleValues[-1]["range"]
                    predPossibleValues[-1]["range"] = (last_range[0], int(max_value))
                #print(predPossibleValues)
                # Sort ranges by proximity to the user predicate value
                predPossibleValues = sorted(
                    predPossibleValues, key=lambda x: abs(x["range"][0] - pred_value)
                )

                # Find concrete values in each range from sorted_possible_refinments1
                concrete_values_in_range = []
                for rng in predPossibleValues:
                    concrete_values = []
                    for refinement in sorted_possible_refinments1:
                        for r in refinement["refinements"]:
                            if (
                                r["column"] == column_name
                                and rng["range"][0] <= r["value"] <= rng["range"][1]
                            ):
                                distance_to_user_query = self.calculate(r["value"], pred_value)
                                new_entry = {
                                    "value": r["value"],
                                    "distance": distance_to_user_query,
                                }
                                if not any(
                                    item["value"] == new_entry["value"] for item in concrete_values
                                ):
                                    concrete_values.append(new_entry)
                    concrete_values_in_range.append(concrete_values)

                # Calculate distances for each range
                predPossibleValues = self.calculate_distances(
                    predPossibleValues, concrete_values_in_range, pred_value
                )

            elif data_type == "categorical":
                # Handle categorical data by using unique values
                predPossibleValues = [{"value": val} for val in sorted(pred)]

                # Sort by proximity to the user predicate value if available
                predPossibleValues = sorted(
                    predPossibleValues,
                    key=lambda x: abs(self.calculate(x["value"], pred_value)),
                )

                # Find concrete values for categorical data
                concrete_values_in_range = []
                for val in predPossibleValues:
                    concrete_values = []
                    for refinement in sorted_possible_refinments1:
                        for r in refinement["refinements"]:
                            if r["column"] == column_name and r["value"] == val["value"]:
                                concrete_values.append(r["value"])
                    concrete_values_in_range.append(list(set(concrete_values)))

            else:
                continue

            # Append generated values to the final output
            if concrete_values_in_range:
                predicate_list = {
                    "operator": operator,
                    "column": column_name,
                    "values": predPossibleValues,
                }
                all_pred_possible_values.append(predicate_list)

        return all_pred_possible_values

    def generatePossibleValues_equalWidth(self, df_original, UserpredicateList, sorted_possible_refinments1):
        """
        Generates possible values for each predicate, sorts ranges based on the order of refinements
        in sorted_possible_refinments1, and returns the most similar value, distance, and concrete values
        from sorted_possible_refinments1 for each range.
        """
        i = 0
        # Multi-dimensional array to store predPossibleValues
        all_pred_possible_values = []
        ccc=1
        # Generate possible values for each predicate
        for predicate in UserpredicateList:
            column_name = predicate[0]
            operator = predicate[1]
            pred_value = predicate[2]
            data_type = predicate[3]
            pred = df_original[column_name].unique()

            if data_type == 'numerical':
                # Handle numerical data
                min_value = np.min(pred)
                max_value = np.max(pred)

                
                num_values = math.ceil((max_value - min_value) / 20)

                if num_values == 0:
                    num_values = 1

                # Calculate range size
                range_size = 20
                print(num_values, range_size)
                # Generate range tuples (start, end) with integer values
                predPossibleValues = []
                for i in range(num_values):
                    start = int(min_value + i * range_size)
                    end = int(min_value + (i + 1) * range_size) - 1

                    if end > max_value:
                        end = max_value
                    if start > max_value:
                        break
                    
                    predPossibleValues.append({"range": (start, end)})
                

                # Adjust the last interval to include the max_value if needed
                if predPossibleValues and 'range' in predPossibleValues[len(predPossibleValues)-1]:
                    # Accessing the last element and updating its range
                    last_range = predPossibleValues[-1]['range']
                    if last_range[1] < max_value:
                        predPossibleValues[-1]['range'] = (last_range[0], max_value)

                print(predPossibleValues)                
                # Sort the ranges based on the lower bound of each range and their distance to pred_value
                predPossibleValues = sorted(predPossibleValues, key=lambda x: abs(x['range'][0] - pred_value))
                
                # Find the most similar value in each range and calculate the distance to the user query
                concrete_values_in_range = []
                for rng in predPossibleValues:
                    # Find concrete values from sorted_possible_refinments1 that fall within the range
                    concrete_values = []
                    for refinement in sorted_possible_refinments1:
                        for r in refinement['refinements']:
                            if r['column'] == column_name and rng['range'][0] <= r['value'] <= rng['range'][1]:
                                distance_to_user_query = self.calculate(r['value'], pred_value)
                                
                                new_entry = {"value": r['value'], "distance": distance_to_user_query}

                                # Check if the new entry already exists in concrete_values
                                if not any(item['value'] == new_entry['value'] for item in concrete_values):
                                    concrete_values.append(new_entry)

                    concrete_values_in_range.append(concrete_values)
                
                # Calculate the distances for each range
                predPossibleValues = self.calculate_distances(predPossibleValues, concrete_values_in_range, pred_value)
               
            elif data_type == 'categorical':

                # Handle categorical data by generating fixed value tuples (val, val)
                predPossibleValues = [(val, val) for val in pred]

                # Sort based on the distance to the user predicate if available
                user_pred_value = None
                for user_pred in UserpredicateList:
                    if user_pred[0] == column_name:
                        user_pred_value = user_pred[2]
                        break

                if user_pred_value is not None:
                    predPossibleValues = sorted(predPossibleValues, key=lambda x: self.calculate(x[0], user_pred_value))

                # For categorical values, the most similar value is directly the categorical value itself
                concrete_values_in_range = []

                for val in predPossibleValues:
                    most_similar_value = val[0]  # For categorical, there's only one value in each range (val, val)
                    #distance_to_user_query = self.calculate(most_similar_value, user_pred_value)
                    # Find concrete values from sorted_possible_refinments1 that fall within the range
                    concrete_values = []
                    for refinement in sorted_possible_refinments1:
                        for r in refinement['refinements']:
                            if r['column'] == column_name and r['value'] == most_similar_value:
                                concrete_values.append(r['value'])

                    # Remove duplicates by converting the list to a set and back to a list
                    concrete_values = list(set(concrete_values))
                    concrete_values_in_range.append(concrete_values)
            else:
                continue  
                
            # Append predPossibleValues and most similar values to the multi-dimensional array
            if concrete_values_in_range != []:
                predicate_list = {
                        'operator': operator,
                        'column' : column_name,
                        'values': predPossibleValues
                    }
            all_pred_possible_values.append(predicate_list)

        return all_pred_possible_values

    def generatePossibleValues_equalWidth2(self, df_original, UserpredicateList, sorted_possible_refinments1):
        """
        Generates possible values for each predicate, sorts ranges based on normalized distance,
        and returns the most similar value, distance, and concrete values from sorted_possible_refinments1.
        """
        # Multi-dimensional array to store predPossibleValues
        all_pred_possible_values = []

        # Generate possible values for each predicate
        for predicate in UserpredicateList:
            column_name = predicate[0]
            operator = predicate[1]
            pred_value = predicate[2]
            data_type = predicate[3]
            pred = df_original[column_name].unique()

            if data_type == 'numerical':
                # Normalize values
                normalized_values = self.normalize_values(pred)
                normalized_pred_value = normalized_values.get(pred_value, 0)

                # Handle numerical data
                min_value = np.min(pred)
                max_value = np.max(pred)

                # Use IQR to determine dynamic range size
                q1 = np.percentile(pred, 25)
                q3 = np.percentile(pred, 75)
                iqr = q3 - q1

                # Determine number of ranges based on spread
                num_values = max(1, int((max_value - min_value) / max(iqr, 1)))
                range_size = (max_value - min_value) / num_values

                # Generate range tuples (start, end)
                predPossibleValues = [
                    {"range": (int(min_value + i * range_size), int(min_value + (i + 1) * range_size) - 1)}
                    for i in range(num_values)
                ]
                # Adjust the last range to include max_value
                if predPossibleValues and predPossibleValues[-1]["range"][1] < max_value:
                    last_range = predPossibleValues[-1]["range"]
                    predPossibleValues[-1]["range"] = (last_range[0], int(max_value))

                # Sort ranges by proximity to the user predicate value
                predPossibleValues = sorted(
                    predPossibleValues, key=lambda x: abs(normalized_values.get(x["range"][0], 0) - normalized_pred_value)
                )

                # Find concrete values in each range from sorted_possible_refinments1
                concrete_values_in_range = []
                for rng in predPossibleValues:
                    concrete_values = []
                    for refinement in sorted_possible_refinments1:
                        for r in refinement["refinements"]:
                            if (
                                r["column"] == column_name
                                and rng["range"][0] <= r["value"] <= rng["range"][1]
                            ):
                                # Calculate distance for normalized values
                                normalized_value = normalized_values.get(r["value"], 0)
                                distance_to_user_query = round(self.calculate(normalized_value, normalized_pred_value),6)

                                new_entry = {
                                    "value": r["value"],
                                    "distance": distance_to_user_query,
                                }
                                if not any(item["value"] == new_entry["value"] for item in concrete_values):
                                    concrete_values.append(new_entry)
                    concrete_values_in_range.append(concrete_values)

                # Calculate distances for each range
                predPossibleValues = self.calculate_distances(
                    predPossibleValues, concrete_values_in_range, normalized_pred_value
                )

            # Append generated values to the final output
            if concrete_values_in_range:
                predicate_list = {
                    "operator": operator,
                    "column": column_name,
                    "values": predPossibleValues,
                    "norm_values": normalized_values,
                    "norm_pred_value": normalized_pred_value
                }
                all_pred_possible_values.append(predicate_list)
        return all_pred_possible_values

    def normalize_values(self, values):
        """
        Normalize values to the range [0, 1].
        """
        min_val = min(values)
        max_val = max(values)
        if max_val == min_val:  # Prevent division by zero
            return {val: 0.5 for val in values}  # If all values are the same, set them to the midpoint
        return {val: (val - min_val) / (max_val - min_val) for val in values}
