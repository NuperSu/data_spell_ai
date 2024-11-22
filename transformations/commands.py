import pandas as pd
from typing import List

def filter_data(df: pd.DataFrame, predicate: str) -> pd.DataFrame:
    return df.query(predicate)

def select_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    return df[columns]

def add_column(df: pd.DataFrame, column_name: str, formula: str) -> pd.DataFrame:
    exec(formula)
    return df

# Mapping of command names to functions
COMMANDS = {
    "filter": filter_data,
    "select": select_columns,
    "add_column": add_column,
}
