from datetime import datetime
import re
#import pandas as pd

class SQL_operators:
    def __init__(self):
        self.predicatesList = []
        self.whyNotList = []
        self.predAttrList = []

    '''def filter(self, type, df1, column1, condition1, column2 = None, condition2 = None):
        pattern = r'([><=]=?)\s+([A-Za-z\d.]+)'
        date_pattern = r'(\d{4}-\d{2}-\d{2})'

        if(condition2 == None):
            #if re.match(pattern, condition1):
            #elif re.match(date_pattern, condition1):
            #match = re.match(date_pattern, condition1)
            #matched_date_str = match.group(1)
            # Convert the matched date string to a datetime object
            #value = pd.to_datetime(matched_date_str)
            match = re.match(pattern, condition1)
            operator = match.group(1) # Extract the operator (e.g., '>=', '>', '<=')
            value = match.group(2)
            if match:  
                if isinstance(value, (int, float)):
                    print("The value is a number.")
                    value = float(value)
                elif isinstance(value, str):
                    print("The value is a string.")
                    value = str(value) 
                    if(operator != '==' and operator != '!='):
                        #value = float(match.group(2)) # Extract the value as an integer
                        if operator == '>=':
                            df = df1[df1[column1] >= value] 
                        elif operator == '<=':
                            df = df1[df1[column1] <= value] 
                        elif operator == '>':
                            df = df1[df1[column1] > value] 
                        elif operator == '<':
                            df = df1[df1[column1] < value] 
                        if type == "UQ":
                            self.setPredicateList("numerical", column1, operator, value)
                            self.set_predicates_attributes("numerical", operator, column1)
                        elif type == "WhyN":
                            self.setUserWhyNot(column1, operator, value)
                    else:
                        #value = str(match.group(2)) # Extract the value as a string
                        if operator == '==':
                            df = df1[df1[column1]== value]
                        elif operator == '!=':
                            df = df1[df1[column1]== value] 
                        if type == "UQ":
                            self.setPredicateList("categorical", column1, operator, value)
                            self.set_predicates_attributes("categorical", operator, column1)   
                        elif type == "WhyN":
                            self.setUserWhyNot(column1, operator, value)      
        else:
            match1 = re.match(pattern, condition1)
            match2 = re.match(pattern, condition2)
            operator1 = match1.group(1) # Extract the operator (e.g., '>=', '>', '<=')
            operator2 = match2.group(1)
            value1 = str(match1.group(2)) # Extract the value as an integer
            value2 = str(match2.group(2)) 
            if match1 and match2:  
                if (operator1 or operator2) == '==':
                    df = df1[(df1[column1] == value1) & (df1[column2] == value2)]
                elif (operator1 or operator2) == '!=':
                    df = df1[(df1[column1] == value1) & (df1[column2] == value2)]
                if (operator2) == '>=':
                    df = df[df[column2] >= int(value2)] 
                
            
                if type == "UQ":
                    self.setPredicateList("categorical", column1, operator1, value1, "categorical", column2, operator2, value2)  
                    self.set_predicates_attributes("categorical", operator1, column1) 
                if type == "WhyN":
                    self.setUserWhyNot(column1, operator1, value1, column2, operator2, value2)

        return df
    ''' 
    def filter(self, type, df1, column1, operator1, value1, value2 = None, value3 = None):


        if(value2 is None):
                if isinstance(value1, (int, float)):
                    value = float(value1)
                elif isinstance(value1, str):
                    value = str(value1) 
                elif isinstance(value1, datetime):
                    value = datetime(value1)

                if operator1 == '>=':
                    df = df1[df1[column1] >= value] 
                elif operator1 == '<=':
                    df = df1[df1[column1] <= value] 
                elif operator1 == '>':
                    df = df1[df1[column1] > value] 
                elif operator1 == '<':
                    df = df1[df1[column1] < value] 
                elif operator1 == '==':
                    df = df1[df1[column1] == value] 
                elif operator1 == '!=':
                    df = df1[df1[column1] != value] 
                if type == "UQ":
                    if isinstance(value, (int, float)):
                        self.setPredicateList("numerical", column1, operator1, value)
                        self.set_predicates_attributes("numerical", operator1, column1)
                    if isinstance(value1, str):
                        self.setPredicateList("categorical", column1, operator1, value)
                        self.set_predicates_attributes("categorical", operator1, column1)  
                    if isinstance(value1, datetime):
                        self.setPredicateList("Datetime", column1, operator1, value)
                        self.set_predicates_attributes("Datetime", operator1, column1)  

                elif type == "WhyN":
                    self.setUserWhyNot(column1, operator1, value)
                        
                    
        elif (value2 is not None):
                if isinstance(value1, (int, float)):
                    value1 = float(value1)
                elif isinstance(value1, str):
                    value1 = str(value1) 
                if isinstance(value2, (int, float)):
                    value2 = float(value2)
                elif isinstance(value2, str):
                    value2 = str(value2) 

                if (operator1) == '==':
                    df = df1[(df1[column1] == value1) | (df1[column1] == value2) | (df1[column1] == value3)]
                elif (operator1) == '!=':
                    df = df1[(df1[column1] == value1) | (df1[column1] == value2) | (df1[column1] == value3)]
                if (operator1) == '>=':
                    df = df[df[column1] >= int(value2)] 
                
            
                if type == "UQ":
                    if isinstance(value1, (int, float)):
                        self.setPredicateList("numerical", column1, operator1, value1, value2, value3)  
                        self.set_predicates_attributes("numerical", operator1, column1) 
                    if isinstance(value1, str):
                        self.setPredicateList("categorical", column1, operator1, value1, value2, value3)  
                        self.set_predicates_attributes("categorical", operator1, column1) 
                if type == "WhyN":
                    self.setUserWhyNot(column1, operator1, value1, value2, value3)


        return df


    def setPredicateList(self, type, column1, operator1, value1, value2 = None, value3 = None):
        if value2 == None:
           self.predicatesList += [[column1, operator1, value1, type]] 
        else:
            self.predicatesList += [[column1, operator1, value1, type, value2, value3]]

    def getPredicateList(self):
        return self.predicatesList

    def setUserWhyNot(self, column1, operator1, value1, value2 = None, value3 = None):
        self.whyNotList += [[column1, operator1, value1, value2, value3]]

    def set_predicates_attributes(self, type, operator, column):
        self.predAttrList += [{'type': type, 'operator': operator, 'column': column}]
    
    def get_predicates_attributes(self):
        return self.predAttrList

    def getUserWhyNot(self):
        return self.whyNotList



