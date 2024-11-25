from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            # Leer el archivo JSON
            df = pd.read_json(uploaded_file)

            # Procesar los datos (ejemplo básico)
            processed = process_data(df)
            
            # Guardar datos procesados para descarga
            output_path = 'data/processed_output.json'
            processed.to_json(output_path, orient="records", indent=4)

            # Generar un gráfico y guardarlo
            graph_path = 'static/graph.png'
            generate_graph(df, graph_path)

            # Responder con estadísticas y ruta de descarga
            stats = processed.describe().to_dict()
            return jsonify({
                "message": "Archivo procesado con éxito",
                "stats": stats,
                "download_url": "/download",
                "graph_url": "/static/graph.png"
            })
        
        return jsonify({"error": "No se subió ningún archivo"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['GET'])
def download():
    output_path = 'data/processed_output.json'
    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True, download_name="processed_output.json")
    return jsonify({"error": "El archivo no está disponible"}), 404

def process_data(df):
    # Limpieza y transformación de datos
    df.dropna(subset=['age'], inplace=True)  # Eliminar valores nulos en 'age'
    df['valor_por_segundo'] = df['sales'] / df['duration_(secs)']  # Agregar columna derivada
    return df

def generate_graph(df, path):
    # Ejemplo: Generar un gráfico de barras para 'sales'
    plt.figure(figsize=(10, 6))
    df['sales'].head(10).plot(kind='bar', color='blue')
    plt.title('Top 10 Ventas')
    plt.xlabel('Índice')
    plt.ylabel('Ventas')
    plt.savefig(path)
    plt.close()
    plt.show()

if __name__ == '__main__':
    app.run(debug=True)
