from unittest import skip
import numpy as np
import math

class attributesRanges:
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


    def generatePossibleValues_equalWidth1(self, df_original, UserpredicateList, sorted_possible_refinments1):
            """
            Generates possible values for each predicate, sorts ranges based on the order of refinements
            in sorted_possible_refinments1, and returns the most similar value, distance, and concrete values
            from sorted_possible_refinments1 for each range.
            """
            i = 0
            # Multi-dimensional array to store predPossibleValues
            all_pred_possible_values = []

            # Generate possible values for each predicate
            for predicate in UserpredicateList:
                column_name = predicate[0]
                operator = predicate[1]
                data_type = predicate[3]
                pred = df_original[column_name].unique()

                if data_type == 'numerical':

                    # Define number of ranges for numerical attributes
                    num_values = 7


                    # Handle numerical data
                    min_value = np.min(pred)
                    max_value = np.max(pred)

                    # Calculate range size
                    range_size = math.ceil(((max_value) - (min_value)) / num_values)

                    # Generate range tuples (start, end) with integer values
                    predPossibleValues = []
                    for i in range(num_values):
                        start = int(min_value + i * range_size)
                        end = int(min_value + (i + 1) * range_size) - 1

                        if end > max_value:
                            end = max_value
                        if start > max_value:
                            break

                        predPossibleValues.append((start, end))

                    # Adjust the last interval to include the max_value
                    if predPossibleValues and predPossibleValues[-1][1] < max_value:
                        predPossibleValues[-1] = (predPossibleValues[-1][0], max_value)

                    # Sort the ranges based on the order in sorted_possible_refinments1
                    def index_of_closest_refinement(rng, refinements, column_name):
                        # Find the index of the first refinement where the value falls within the range
                        for idx, refinement in enumerate(refinements):
                            for r in refinement['refinements']:
                                if r['column'] == column_name and r['value'] >= rng[0] and r['value'] <= rng[1]:
                                    return idx  # Return the index of the refinement
                        return float('inf')  # Return a large value if no match found

                    # Sort based on the index of refinements in sorted_possible_refinments1
                    predPossibleValues = sorted(
                        predPossibleValues,
                        key=lambda rng: index_of_closest_refinement(rng, sorted_possible_refinments1, column_name)
                    )

                    # Find the most similar value in each range and calculate the distance to the user query
                    concrete_values_in_range = []
                    for rng in predPossibleValues:
                        user_pred_value = None
                        for user_pred in UserpredicateList:
                            if user_pred[0] == column_name:
                                user_pred_value = user_pred[2]
                                break

                        # The most similar value will either be the start or end of the range, whichever is closer
                        most_similar_value = min([rng[0], rng[1]], key=lambda x: self.calculate(x, user_pred_value))
                        distance_to_user_query = self.calculate(most_similar_value, user_pred_value)
                        
                        # Find concrete values from sorted_possible_refinments1 that fall within the range
                        concrete_values = []
                        for refinement in sorted_possible_refinments1:
                            for r in refinement['refinements']:
                                if r['column'] == column_name and rng[0] <= r['value'] <= rng[1]:
                                    concrete_values.append(r['value'])

                        # Remove duplicates by converting the list to a set and back to a list
                        concrete_values = list(set(concrete_values))

                        concrete_values_in_range.append(concrete_values)#{
                            #'range': rng,
                            #'Most similar value': most_similar_value,
                            #'Distance': distance_to_user_query,
                            #'Concrete values': concrete_values  # Add the concrete values
                        #})

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
                        distance_to_user_query = self.calculate(most_similar_value, user_pred_value)
                                        # Find concrete values from sorted_possible_refinments1 that fall within the range
                        concrete_values = []
                        for refinement in sorted_possible_refinments1:
                            for r in refinement['refinements']:
                                if r['column'] == column_name and r['value'] == most_similar_value:
                                    concrete_values.append(r['value'])

                        # Remove duplicates by converting the list to a set and back to a list
                        concrete_values = list(set(concrete_values))
                        concrete_values_in_range.append(concrete_values)
                        '''
                        concrete_values_in_range.append({
                            #'Most similar value': most_similar_value,
                            #'Distance': distance_to_user_query,
                            'Concrete values': concrete_values  # Add the concrete values
                        })
                        '''

                else:
                    continue
                
                
                # Append predPossibleValues and most similar values to the multi-dimensional array

                predicate_list = {
                        'operator': operator,
                        'values': predPossibleValues,
                        'Concrete Vlaues': concrete_values_in_range
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

        # Generate possible values for each predicate
        for predicate in UserpredicateList:
            column_name = predicate[0]
            operator = predicate[1]
            data_type = predicate[3]
            pred = df_original[column_name].unique()

            if data_type == 'numerical':

                # Define number of ranges for numerical attributes
                num_values = 7


                # Handle numerical data
                min_value = np.min(pred)
                max_value = np.max(pred)

                # Calculate range size
                range_size = math.ceil(((max_value) - (min_value)) / num_values)

                # Generate range tuples (start, end) with integer values
                predPossibleValues = []
                for i in range(num_values):
                    start = int(min_value + i * range_size)
                    end = int(min_value + (i + 1) * range_size) - 1

                    if end > max_value:
                        end = max_value
                    if start > max_value:
                        break

                    predPossibleValues.append((start, end))

                # Adjust the last interval to include the max_value
                if predPossibleValues and predPossibleValues[-1][1] < max_value:
                    predPossibleValues[-1] = (predPossibleValues[-1][0], max_value)

                # Sort the ranges based on the smallest value (start)
                predPossibleValues = sorted(predPossibleValues, key=lambda x: x[0])

                # Find the corresponding user predicate for this column
                user_pred_value = None
                for user_pred in UserpredicateList:
                    if user_pred[0] == column_name:
                        user_pred_value = user_pred[2]  # User predicate value
                        break

                # Sort based on distance to user predicate value if available
                if user_pred_value is not None:
                    predPossibleValues = sorted(predPossibleValues, key=lambda x: self.calculate(x[0], user_pred_value))

                print(predPossibleValues)

                # Find the most similar value in each range and calculate the distance to the user query
                concrete_values_in_range = []
                for rng in predPossibleValues:
                    user_pred_value = None
                    for user_pred in UserpredicateList:
                        if user_pred[0] == column_name:
                            user_pred_value = user_pred[2]
                            break

                    # The most similar value will either be the start or end of the range, whichever is closer
                    most_similar_value = min([rng[0], rng[1]], key=lambda x: self.calculate(x, user_pred_value))
                    distance_to_user_query = self.calculate(most_similar_value, user_pred_value)
                    
                    # Find concrete values from sorted_possible_refinments1 that fall within the range
                    concrete_values = []
                    for refinement in sorted_possible_refinments1:
                        for r in refinement['refinements']:
                            if r['column'] == column_name and rng[0] <= r['value'] <= rng[1]:
                                concrete_values.append(r['value'])

                    # Remove duplicates by converting the list to a set and back to a list
                    concrete_values = list(set(concrete_values))

                    concrete_values_in_range.append(concrete_values)#{
                        #'range': rng,
                        #'Most similar value': most_similar_value,
                        #'Distance': distance_to_user_query,
                        #'Concrete values': concrete_values  # Add the concrete values
                    #})

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
                    distance_to_user_query = self.calculate(most_similar_value, user_pred_value)
                                    # Find concrete values from sorted_possible_refinments1 that fall within the range
                    concrete_values = []
                    for refinement in sorted_possible_refinments1:
                        for r in refinement['refinements']:
                            if r['column'] == column_name and r['value'] == most_similar_value:
                                concrete_values.append(r['value'])

                    # Remove duplicates by converting the list to a set and back to a list
                    concrete_values = list(set(concrete_values))
                    concrete_values_in_range.append(concrete_values)
                    '''
                    concrete_values_in_range.append({
                        #'Most similar value': most_similar_value,
                        #'Distance': distance_to_user_query,
                        'Concrete values': concrete_values  # Add the concrete values
                    })
                    '''

            else:
                continue
            
            
            # Append predPossibleValues and most similar values to the multi-dimensional array

            predicate_list = {
                    'operator': operator,
                    'values': predPossibleValues,
                    'Concrete Vlaues': concrete_values_in_range
                }
            all_pred_possible_values.append(predicate_list)
        
        return all_pred_possible_values

    '''
    def generatePossibleValues(self, df_original, predicatesList):

        all_pred_possible_values = []
        for predicate in predicatesList:
            column_name = predicate['column']
            distinct_value = df_original[column_name].unique().tolist()
            #ppend predPossibleValues to the multi-dimensional array
            all_pred_possible_values.append({'predicate': predicate, 'values': distinct_value}) 

        #print(all_pred_possible_values,"\n\n")
        return all_pred_possible_values
    
    def calculate(self, value1, value2):
        return abs(value1 - value2)

    def generatePossibleValues_equalWidth(self, df_original, UserpredicateList):
        """
        Generates possible values for each predicate and sorts them based on 
        Manhattan distance to the user predicate.
        """
        # Define number of ranges for numerical attributes
        num_values = 15

        # Multi-dimensional array to store predPossibleValues
        all_pred_possible_values = []

        # Generate possible values for each predicate
        for predicate in UserpredicateList:
            column_name = predicate[0]
            operator = predicate[1]
            data_type = predicate[3]
            pred = df_original[column_name].unique()

            if data_type == 'numerical':
                # Handle numerical data
                min_value = np.min(pred)
                max_value = np.max(pred)

                # Calculate range size
                range_size = math.ceil(((max_value) - (min_value)) / num_values)

                # Generate range tuples (start, end) with integer values
                predPossibleValues = []
                for i in range(num_values):
                    start = int(min_value + i * range_size)
                    end = int(min_value + (i + 1) * range_size) - 1

                    if end > max_value:
                        end = max_value
                    if start > max_value:
                        break

                    predPossibleValues.append((start, end))

                # Adjust the last interval to include the max_value
                if predPossibleValues and predPossibleValues[-1][1] < max_value:
                    predPossibleValues[-1] = (predPossibleValues[-1][0], max_value)

                # Sort the ranges based on the smallest value (start)
                predPossibleValues = sorted(predPossibleValues, key=lambda x: x[0])

                # Find the corresponding user predicate for this column
                user_pred_value = None
                for user_pred in UserpredicateList:
                    if user_pred[0] == column_name:
                        user_pred_value = user_pred[2]  # User predicate value
                        break

                # Sort based on distance to user predicate value if available
                if user_pred_value is not None:
                    predPossibleValues = sorted(predPossibleValues, key=lambda x: self.calculate(x[0], user_pred_value))

            elif data_type == 'categorical':
                # Handle categorical data by generating fixed value tuples (val, val)
                predPossibleValues = [(val, val) for val in pred]

                # For categorical, sort based on the distance to the user predicate if available
                user_pred_value = None
                for user_pred in UserpredicateList:
                    if user_pred[0] == column_name:
                        user_pred_value = user_pred[2]
                        break

                if user_pred_value is not None:
                    predPossibleValues = sorted(predPossibleValues, key=lambda x: self.calculate(x[0], user_pred_value))

            else:
                continue

            # Append predPossibleValues to the multi-dimensional array
            predicate_list = {'operator': operator, 'values': predPossibleValues}
            all_pred_possible_values.append(predicate_list)

        return all_pred_possible_values
    '''
    




        


            


