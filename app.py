from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy import stats
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Configuración de carpetas
GRAPH_FOLDER = "static/graphs/"
CLEANED_FOLDER = "static/cleaned/"
os.makedirs(GRAPH_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)

# Función para cargar datos
def load_data(file_path):
    try:
        return pd.read_json(file_path)
    except ValueError as e:
        raise ValueError(f"Error al cargar el archivo JSON: {e}")

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

# Función para limpiar datos
def clean_data(data):
    # Convertir la columna 'age' a numérica y manejar valores no válidos
    data['age'] = pd.to_numeric(data['age'], errors='coerce')

    # Filtrar valores fuera de rango en 'age'
    age_outliers = data[(data['age'] < 0) | (data['age'] > 120) | data['age'].isna()]
    num_outliers = len(age_outliers)

    # Eliminar valores NaN en 'age'
    data.dropna(subset=['age'], inplace=True)

    # Convertir 'age' a entero
    data['age'] = data['age'].astype(int)

    # Eliminar columnas específicas
    columnas_a_eliminar = ['accessed_Ffom', 'network_protocol']
    columnas_eliminadas = [col for col in columnas_a_eliminar if col in data.columns]
    data = data.drop(columns=columnas_eliminadas, errors='ignore')

    # Convertir 'accessed_date' a formato de fecha si existe
    if 'accessed_date' in data.columns:
        data['accessed_date'] = pd.to_datetime(data['accessed_date'], errors='coerce')

    # Guardar datos limpios
    cleaned_file_path = os.path.join(CLEANED_FOLDER, "cleaned_data.json")
    data.to_json(cleaned_file_path, orient='records', lines=True)

    return {
        "outliers": num_outliers,
        "columns_removed": columnas_eliminadas,
        "cleaned_file": cleaned_file_path
    }



# Función para entrenar modelos de Machine Learning
def train_models(data):
    # Manejar valores nulos
    data.fillna(0, inplace=True)

    # Preparar datos para clasificación
    X_classification = pd.get_dummies(
        data[['duration_(secs)', 'bytes', 'age', 'gender', 'country', 'membership', 'language', 'pay_method']],
        drop_first=True
    )
    y_classification = data['returned'].apply(lambda x: 1 if x == 'Yes' else 0)
    X_train_class, X_test_class, y_train_class, y_test_class = train_test_split(
        X_classification, y_classification, test_size=0.3, random_state=42
    )

    # Entrenar modelo de Árbol de Decisión
    tree_model = DecisionTreeClassifier(max_depth=5, random_state=42)
    tree_model.fit(X_train_class, y_train_class)
    y_pred_class = tree_model.predict(X_test_class)
    class_accuracy = accuracy_score(y_test_class, y_pred_class)
    class_report = classification_report(y_test_class, y_pred_class, output_dict=True)

    # Preparar datos para regresión
    X_regression = pd.get_dummies(
        data[['duration_(secs)', 'bytes', 'age', 'sales', 'gender', 'country', 'membership', 'language', 'pay_method']],
        drop_first=True
    )
    y_regression = data['returned_amount']
    X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
        X_regression, y_regression, test_size=0.3, random_state=42
    )
    scaler = StandardScaler()
    X_train_reg = scaler.fit_transform(X_train_reg)
    X_test_reg = scaler.transform(X_test_reg)

    # Entrenar modelo de Red Neuronal
    nn_model = MLPRegressor(hidden_layer_sizes=(100,), max_iter=500, random_state=42)
    nn_model.fit(X_train_reg, y_train_reg)
    y_pred_reg = nn_model.predict(X_test_reg)
    reg_mse = mean_squared_error(y_test_reg, y_pred_reg)
    reg_r2 = r2_score(y_test_reg, y_pred_reg)

    return {
        "classification": {
            "accuracy": class_accuracy,
            "report": class_report,
        },
        "regression": {
            "mse": reg_mse,
            "r2": reg_r2,
        }
    }

# Endpoint para procesar modelos de Machine Learning
@app.route('/process_models', methods=['POST'])
def process_models():
    try:
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = f"data/{uploaded_file.filename}"
            os.makedirs("data", exist_ok=True)
            uploaded_file.save(file_path)

            # Cargar datos
            data = load_data(file_path)

            # Entrenar modelos
            results = train_models(data)

            return jsonify(results)

        return jsonify({"error": "No se subió ningún archivo"}), 400
    except Exception as e:
        print("Error durante el procesamiento de modelos:", e)
        return jsonify({"error": str(e)}), 500


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

            # Generar gráficos
            graphs = generate_graphs(data)
            graph_urls = [f"/{path}" for path in graphs]

            return jsonify({"kpis": kpis, "outliers": outliers, "graphs": graph_urls})

        return jsonify({"error": "No se subió ningún archivo"}), 400
    except Exception as e:
        print("Error procesando datos:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/process_cleaning', methods=['POST'])
def process_cleaning():
    try:
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = f"data/{uploaded_file.filename}"
            os.makedirs("data", exist_ok=True)
            uploaded_file.save(file_path)

            # Cargar datos
            data = load_data(file_path)

            # Limpiar datos
            cleaning_results = clean_data(data)

            return jsonify({
                "message": "Limpieza completada",
                "outliers": cleaning_results["outliers"],
                "columns_removed": cleaning_results["columns_removed"],
                "cleaned_file": cleaning_results["cleaned_file"]
            })

        return jsonify({"error": "No se subió ningún archivo"}), 400
    except Exception as e:
        print("Error durante la limpieza:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", default=5000))
