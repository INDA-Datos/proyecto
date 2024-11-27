from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy import stats

app = Flask(__name__)

GRAPH_FOLDER = "static/graphs/"
os.makedirs(GRAPH_FOLDER, exist_ok=True)

# Función para cargar datos
def load_data(file_path):
    return pd.read_json(file_path)

# Calcular KPIs
def calculate_kpis(data):
    total_rows = int(data.shape[0])
    total_columns = int(data.shape[1])
    missing_values = int(data.isnull().sum().sum())
    percentage_missing = round((missing_values / (total_rows * total_columns)) * 100, 2)
    duplicate_rows = int(data.duplicated().sum())
    complete_rows = int(total_rows - data.isnull().any(axis=1).sum())

    return {
        "Total Filas": total_rows,
        "Total Columnas": total_columns,
        "Valores Faltantes": missing_values,
        "Porcentaje Valores Faltantes": percentage_missing,
        "Filas Duplicadas": duplicate_rows,
        "Filas Completas": complete_rows,
    }

# Calcular valores atípicos
def calculate_outliers(data):
    numeric_columns = data.select_dtypes(include='number').columns
    z_scores = data[numeric_columns].apply(lambda x: stats.zscore(x, nan_policy='omit'))
    outliers = (z_scores > 3) | (z_scores < -3)
    return {col: int(count) for col, count in outliers.sum().items()}

# Generar gráficos básicos
def generate_graphs(data):
    graphs = []

    # Gráfico 1: Histograma de ventas
    if 'sales' in data.columns:
        plt.figure(figsize=(6, 4))
        sns.histplot(data['sales'], kde=True, color='blue')
        plt.title('Distribución de Ventas')
        plt.xlabel('Ventas')
        plt.ylabel('Frecuencia')
        hist_path = os.path.join(GRAPH_FOLDER, 'sales_histogram.png')
        plt.savefig(hist_path)
        plt.close()
        graphs.append(hist_path)

    # Gráfico 2: Heatmap de correlaciones
    numeric_columns = data.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) > 1:
        plt.figure(figsize=(6, 4))
        sns.heatmap(data[numeric_columns].corr(), annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Mapa de Correlaciones')
        heatmap_path = os.path.join(GRAPH_FOLDER, 'correlation_heatmap.png')
        plt.savefig(heatmap_path)
        plt.close()
        graphs.append(heatmap_path)

    return graphs

# Generar gráficos adicionales
def generate_additional_graphs(data):
    graphs = []

    # Gráfico 3: Histograma de edades
    if 'age' in data.columns:
        plt.figure(figsize=(6, 4))
        sns.histplot(data['age'], kde=False, bins=20, color='teal')
        plt.title('Distribución de Edades')
        plt.xlabel('Edad')
        plt.ylabel('Frecuencia')
        age_hist_path = os.path.join(GRAPH_FOLDER, 'hist_age.png')
        plt.savefig(age_hist_path)
        plt.close()
        graphs.append(age_hist_path)

    # Gráfico 4: Ventas por país
    if 'country' in data.columns and 'sales' in data.columns:
        plt.figure(figsize=(6, 4))
        country_sales = data.groupby('country')['sales'].sum().sort_values(ascending=False)
        country_sales[:10].plot(kind='bar', color='orange')
        plt.title('Ventas por País (Top 10)')
        plt.xlabel('País')
        plt.ylabel('Ventas Totales')
        country_sales_path = os.path.join(GRAPH_FOLDER, 'sales_country.png')
        plt.savefig(country_sales_path)
        plt.close()
        graphs.append(country_sales_path)

    # Gráfico 5: Proporción de género
    if 'gender' in data.columns:
        plt.figure(figsize=(6, 4))
        gender_counts = data['gender'].value_counts()
        gender_counts.plot(kind='pie', autopct='%1.1f%%', colors=['skyblue', 'pink'], startangle=90)
        plt.title('Proporción de Género')
        gender_pie_path = os.path.join(GRAPH_FOLDER, 'gender_pie.png')
        plt.savefig(gender_pie_path)
        plt.close()
        graphs.append(gender_pie_path)

    return graphs

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/machine_learning')
def machine_learning():
    return render_template('machine_learning.html')

@app.route('/LimpiezaDatos')
def LimpiezaDatos():
     return render_template('LimpiezaDatos.html')


@app.route('/process_data', methods=['POST'])
def process_data():
    try:
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = f"data/{uploaded_file.filename}"
            os.makedirs("data", exist_ok=True)
            uploaded_file.save(file_path)

            # Cargar datos
            data = load_data(file_path)

            # Calcular KPIs
            kpis = calculate_kpis(data)

            # Calcular valores atípicos
            outliers = calculate_outliers(data)

            # Generar gráficos básicos y adicionales
            basic_graphs = generate_graphs(data)
            additional_graphs = generate_additional_graphs(data)
            all_graphs = basic_graphs + additional_graphs
            graph_urls = [f"/{path}" for path in all_graphs]

            return jsonify({"kpis": kpis, "outliers": outliers, "graphs": graph_urls})

        return jsonify({"error": "No se subió ningún archivo"}), 400
    except Exception as e:
        print("Error procesando datos:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    plt.switch_backend('agg')
    app.run(debug=True)