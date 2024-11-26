import matplotlib.pyplot as plt

def generate_graph(df, output_path):
    # Gráfico de los productos más vendidos
    plt.figure(figsize=(10, 6))
    top_products = df.groupby('product_name')['total_sales'].sum().sort_values(ascending=False).head(10)
    top_products.plot(kind='bar', color='skyblue')
    plt.title('Top 10 Productos Más Vendidos')
    plt.xlabel('Producto')
    plt.ylabel('Ingresos Totales')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
