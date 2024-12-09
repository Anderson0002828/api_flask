from sentence_transformers import SentenceTransformer
from flask import Blueprint, request, jsonify
from scipy.spatial.distance import cdist
from flask_cors import cross_origin
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import openai
import os

# Cargar variables de entorno
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Cargar modelo y datos preprocesados
model = SentenceTransformer('all-MiniLM-L6-v2')
product_vectors = np.load("utils/product_vectors.npy")
product_metadata = pd.read_csv("utils/product_metadata.csv")

if "product_name" not in product_metadata.columns or "product_description" not in product_metadata.columns:
    raise ValueError("El archivo 'product_metadata.csv' no tiene las columnas necesarias.")

# Crear el Blueprint para las rutas del chatbot
chatbot_route = Blueprint("chatbot", __name__)

@chatbot_route.route("/", methods=["POST"])
@cross_origin()
def chatbot_response():
    data = request.json
    user_input = data.get("question", "").strip()

    if not user_input:
        return jsonify({"error": "La pregunta no puede estar vacía."}), 400

    try:
        # Paso 1: Clasificar intención con GPT
        intencion = clasificar_intencion_gpt(user_input)

        # Paso 2: Manejar según la intención
        if intencion == "pregunta_general":
            respuesta = manejar_pregunta_general(user_input)
        elif intencion == "busqueda_producto":
            respuesta = manejar_busqueda_producto(user_input)
        elif intencion == "consulta_tienda":
            respuesta = manejar_consulta_tienda(user_input)
        else:
            respuesta = "Lo siento, no entendí tu consulta. ¿Podrías reformularla?"

        return jsonify({"success": True, "response": respuesta})

    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


def clasificar_intencion_gpt(user_input):
    # Usa GPT-4 para clasificar la intención del usuario.
    gpt_prompt = f"""
    Eres un asistente inteligente de MarkeTech. Tu tarea es analizar las consultas de los clientes y clasificarlas en una de las siguientes categorías:
    - "busqueda_producto": si el cliente busca un producto específico o desea información sobre productos disponibles.
    - "consulta_tienda": si el cliente pregunta sobre políticas, envíos, devoluciones u horarios de la tienda.
    - "pregunta_general": si el cliente realiza preguntas generales o de otro tipo.
    
    Consulta del cliente: "{user_input}"
    Responde únicamente con una de las categorías mencionadas: "busqueda_producto", "consulta_tienda" o "pregunta_general".
    """
    try:
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": gpt_prompt}],
        )
        return gpt_response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return "pregunta_general"  # Predeterminado en caso de error

def manejar_pregunta_general(user_input):
    # Genera una respuesta para preguntas generales usando GPT-4.
    gpt_prompt = f"""
    Eres un asistente experto en tecnología. Responde de forma clara y profesional.
    Pregunta del cliente: "{user_input}"
    """
    return generar_respuesta_gpt(gpt_prompt)

def manejar_busqueda_producto(user_input):
    # Genera una respuesta para búsquedas de productos.
    # Vectorizar la consulta del usuario
    user_vector = model.encode([user_input])[0]
    
    # Calcular similitud de coseno con los vectores de productos
    distances = cdist([user_vector], product_vectors, metric="cosine")[0]
    closest_indices = np.argsort(distances)[:5]  # Top 5 productos más similares

    # Obtener productos más relevantes
    relevant_products = product_metadata.iloc[closest_indices]
    if relevant_products.empty:
        return generar_respuesta_gpt(f"No encontré coincidencias para: {user_input}. ¿Puedo ayudarte con otra cosa?")
    
    # Crear lista de productos relevantes
    product_summary = "\n".join([
        f"- {row['product_name']} ({row['product_description']}), Precio: {row.get('product_price', 'No disponible')}"
        for _, row in relevant_products.iterrows()
    ])
    
    gpt_prompt = f"""
    Un cliente busca: "{user_input}".
    Los productos más relevantes son:
    {product_summary}.
    Por favor, ayuda al cliente a elegir el mejor producto para sus necesidades.
    """
    return generar_respuesta_gpt(gpt_prompt)

def manejar_consulta_tienda(user_input):
    # Responde consultas relacionadas con la tienda.
    # Puedes agregar reglas específicas o usar GPT
    gpt_prompt = f"""
    Eres un asistente de MarkeTech especializado en políticas de la tienda.
    Pregunta del cliente: "{user_input}"
    Responde de forma clara y profesional.
    """
    return generar_respuesta_gpt(gpt_prompt)

def generar_respuesta_gpt(gpt_prompt):
    # Llama a la API de GPT-4 para generar una respuesta.
    try:
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": gpt_prompt}],
        )
        return gpt_response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Lo siento, hubo un problema al generar la respuesta: {str(e)}"