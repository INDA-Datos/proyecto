from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# Cargar datos desde un archivo
def load_data(file_path):
    return pd.read_json(file_path)

# Calcular los KPIs
def calculate_kpis(data):
    total_rows = data.shape[0]
    total_columns = data.shape[1]
    missing_values = data.isnull().sum().sum()
    percentage_missing = (missing_values / (total_rows * total_columns)) * 100
    duplicate_rows = data.duplicated().sum()
    complete_rows = total_rows - data.isnull().any(axis=1).sum()

    return {
        "Total Filas": int(total_rows),
        "Total Columnas": int(total_columns),
        "Valores Faltantes": int(missing_values),
        "Porcentaje Valores Faltantes": round(percentage_missing, 2),
        "Filas Duplicadas": int(duplicate_rows),
        "Filas Completas": int(complete_rows),
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_data', methods=['POST'])
def process_data():
    try:
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = f"data/{uploaded_file.filename}"
            uploaded_file.save(file_path)

            # Cargar datos y calcular KPIs
            data = load_data(file_path)
            kpis = calculate_kpis(data)

            return jsonify(kpis)

        return jsonify({"error": "No se subió ningún archivo"}), 400
    except Exception as e:
        print("Error procesando datos:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
