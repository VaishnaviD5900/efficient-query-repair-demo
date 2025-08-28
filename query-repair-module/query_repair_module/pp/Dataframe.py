import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import norm, uniform, expon, beta
import os


class Dataframe:
    def __init__(self, seed=42):
        np.random.seed(seed)  
        self.DATASETS_DIR = Path(os.getenv("DATASETS_DIR", "/app/datasets"))

    def getDataframe_TPCH(self, size):
        base = self.DATASETS_DIR
        dataName= "TPCH"
        df_customer = pd.read_csv(base/'tpch_0_1/customer.csv')
        df_lineitem = pd.read_csv(base/'tpch_0_1/lineitem.csv')
        df_nation = pd.read_csv(base/'tpch_0_1/nation.csv')
        df_orders = pd.read_csv(base/'tpch_0_1/orders.csv')
        df_part = pd.read_csv(base/'tpch_0_1/part.csv')
        df_partsupp = pd.read_csv(base/'tpch_0_1/partsupp.csv')
        df_region = pd.read_csv(base/'tpch_0_1/region.csv')
        df_supplier = pd.read_csv(base/'tpch_0_1/supplier.csv')

        return df_lineitem, df_nation, df_part, df_partsupp, df_region, df_supplier, dataName, size


    def getDataframe_ACSIncome(self, size):
        dataName= "ACSIncome"
        csv_path = self.DATASETS_DIR / "ACSIncome_state_number1.csv"
        df_original = pd.read_csv(csv_path)

        df = df_original.sample(n= size, random_state=42)  # You can change the value of n as needed

        return df, dataName, size

    def getDataframe_Healthcare(self, size):
        dataName= "Healthcare"
        csv_path = self.DATASETS_DIR / "healthcare_800_numerical.csv"
        df_original = pd.read_csv(csv_path)

        df = df_original.sample(n=size, replace=True, random_state=42)  # You can change the value of n as needed

        return df, dataName, size