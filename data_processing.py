import pandas as pd

def process_data(df):
    # Ejemplo de limpieza: eliminar nulos y columnas innecesarias
    df.dropna(subset=['age'], inplace=True)
    columnas_a_eliminar = ['accessed_Ffom', 'network_protocol']
    df = df.drop(columns=columnas_a_eliminar, errors='ignore')
    
    # Agregar columna derivada
    df['valor_por_segundo'] = df['sales'] / df['duration_(secs)']
    return df
