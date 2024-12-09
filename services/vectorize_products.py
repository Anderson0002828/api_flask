from sentence_transformers import SentenceTransformer
from models.models import MarketechProduct
from database.database import init_app
from flask import Flask
import pandas as pd
import numpy as np

def get_product_data():
    # Consulta los productos de la base de datos
    products = MarketechProduct.query.all()
    return [
        {
            "id": product.id,
            "product_name": product.product_name,
            "product_description": product.product_description,
            "product_mark": product.product_mark,
            "product_model": product.product_model,
            "category": product.category,
            "subcategory": product.subcategory,
            "product_price": product.product_price,
            "product_discount": product.product_discount,
            "product_quantity": product.product_quantity
        }
        for product in products
    ]

def vectorize_products():
    # Cargar el modelo de embeddings
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Obtener datos de los productos
    product_data = get_product_data()
    if not product_data:
        print("No hay productos disponibles en la base de datos.")
        return

    # Combinar datos relevantes en una descripción única para cada producto
    product_descriptions = [
        (
            f"Producto: {p['product_name']} - "
            f"Descripción: {p['product_description']} - "
            f"Marca: {p['product_mark']} - "
            f"Modelo: {p['product_model']} - "
            f"(Categoría: {p['category']}, Subcategoría: {p['subcategory']}) - "
            f"Precio: {p['product_price']} - "
            f"Descuento: {p['product_discount']} - "
            f"Cantidad: {p['product_quantity']} - "
        )
        for p in product_data
    ]

    # Generar embeddings para las descripciones
    product_vectors = model.encode(product_descriptions)

    # Guardar los vectores y los metadatos
    np.save("utils/product_vectors.npy", product_vectors)
    pd.DataFrame(product_data).to_csv("utils/product_metadata.csv", index=False)
    print("¡Vectorización completada!")

if __name__ == "__main__":
    # Inicializar la aplicación Flask
    app = Flask(__name__)
    init_app(app)

    # Ejecutar dentro del contexto de la aplicación
    with app.app_context():
        vectorize_products()