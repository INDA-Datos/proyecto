import pandas as pd

def load_data(file_path):
    return pd.read_json(file_path)

def calculate_kpis(data):
    total_rows = data.shape[0]
    total_columns = data.shape[1]
    missing_values = data.isnull().sum().sum()
    percentage_missing = (missing_values / (total_rows * total_columns)) * 100
    duplicate_rows = data.duplicated().sum()
    complete_rows = total_rows - data.isnull().any(axis=1).sum()

    return {
        "Total Filas": total_rows,
        "Total Columnas": total_columns,
        "Valores Faltantes": missing_values,
        "Porcentaje Valores Faltantes": round(percentage_missing, 2),
        "Filas Duplicadas": duplicate_rows,
        "Filas Completas": complete_rows
    }
