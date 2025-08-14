import pandas as pd
import numpy as np
from scipy.stats import norm, uniform, expon, beta

class Dataframe:
    def __init__(self, seed=42):
        np.random.seed(seed)  # Set the random seed for reproducibility

    def getDataframe_TPCH(self, size):
        dataName= "TPCH"

        df_customer = pd.read_csv('C:/Query-Repair-System/Datasets/tpch_0_1/customer.csv')
        df_lineitem = pd.read_csv('C:/Query-Repair-System/Datasets/tpch_0_1/lineitem.csv')
        df_nation = pd.read_csv('C:/Query-Repair-System/Datasets/tpch_0_1/nation.csv')
        df_orders = pd.read_csv('C:/Query-Repair-System/Datasets/tpch_0_1/orders.csv')
        df_part = pd.read_csv('C:/Query-Repair-System/Datasets/tpch_0_1/part.csv')
        df_partsupp = pd.read_csv('C:/Query-Repair-System/Datasets/tpch_0_1/partsupp.csv')
        df_region = pd.read_csv('C:/Query-Repair-System/Datasets/tpch_0_1/region.csv')
        df_supplier = pd.read_csv('C:/Query-Repair-System/Datasets/tpch_0_1/supplier.csv')

        return df_lineitem, df_nation, df_part, df_partsupp, df_region, df_supplier, dataName, size


    def getDataframe_ACSIncome(self, size):
        dataName= "ACSIncome"
        df_original = pd.read_csv(f'C:/Query-Repair-System/Datasets/ACSIncome_state_number1.csv')

        df = df_original.sample(n= size, random_state=42)  # You can change the value of n as needed

        return df, dataName, size

    def getDataframe_Healthcare(self, size):
        dataName= "Healthcare"
        df_original = pd.read_csv('C:/Query-Repair-System/Datasets/healthcare_800_numerical.csv')

        df = df_original.sample(n=size, replace=True, random_state=42)  # You can change the value of n as needed

        return df, dataName, size