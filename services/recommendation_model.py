from models.models import MarketechProduct, MarketechProductVisited
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from datetime import datetime
import pandas as pd

def apply_temporal_weighting(user_visited_df):
    # Aplica un factor de ponderación temporal para los productos visitados.
    current_time = datetime.utcnow()
    user_visited_df['visited_at'] = pd.to_datetime(user_visited_df['visited_at'], errors='coerce')
    user_visited_df = user_visited_df.dropna(subset=['visited_at'])

    user_visited_df['time_diff'] = (current_time - user_visited_df['visited_at']).dt.total_seconds()
    max_time_diff = user_visited_df['time_diff'].max()
    if max_time_diff > 0:
        user_visited_df['weight'] = 1 - (user_visited_df['time_diff'] / max_time_diff)
    else:
        user_visited_df['weight'] = 1.0

    return user_visited_df

def get_user_recent_visited_products(user_id, max_records=16):
    # Obtiene los productos visitados por un usuario ordenados por fecha de visita,
    # limitando el número de registros a un máximo.
    visited_records = (
        MarketechProductVisited.query.filter_by(user_id=user_id)
        .order_by(MarketechProductVisited.visited_at.desc())
        .limit(max_records)
        .all()
    )
    
    visited_products = [
        {
            "id": record.product_id,
            "visited_at": record.visited_at,
            "product_name": record.product.product_name,
            "product_description": record.product.product_description,
            "category": record.product.category,
            "subcategory": record.product.subcategory,
            "product_mark": record.product.product_mark,
            "product_model": record.product.product_model,
        }
        for record in visited_records
    ]
    return pd.DataFrame(visited_products)

def get_all_products():
    # Obtiene todos los productos en la base de datos.
    all_products = MarketechProduct.query.all()
    if not all_products:
        return pd.DataFrame()
    
    product_list = [product.to_dict() for product in all_products if product]
    return pd.DataFrame(product_list)

def generate_recommendations(user_id, max_records=16, focus_records=6):
    # Genera una lista ordenada de productos recomendados para el usuario.
    # Se enfoca en los últimos `focus_records` productos visitados para mayor precisión.
    # Obtener productos visitados recientemente
    user_visited_df = get_user_recent_visited_products(user_id, max_records=max_records)
    if user_visited_df.empty:
        return []

    # Aplicar ponderación temporal
    user_visited_df = apply_temporal_weighting(user_visited_df)

    # Filtrar los `focus_records` productos con mayor peso
    user_visited_df = user_visited_df.nlargest(focus_records, 'weight')

    # Obtener todos los productos
    all_products_df = get_all_products()
    if all_products_df.empty:
        return []

    # Combinar características relevantes
    all_products_df['combined_features'] = (
        all_products_df['product_mark'].fillna('') + " " +
        all_products_df['category'].fillna('') + " " +
        all_products_df['subcategory'].fillna('') + " " +
        all_products_df['product_model'].fillna('') + " " +
        all_products_df['product_description'].fillna('')
    )

    # Vectorización usando TF-IDF
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(all_products_df['combined_features'])

    # Calculamos similitud coseno
    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
    indices = pd.Series(all_products_df.index, index=all_products_df['id']).drop_duplicates()

    recommendations = pd.DataFrame()
    for _, row in user_visited_df.iterrows():
        product_id = row['id']
        weight = row['weight']

        if product_id in indices:
            idx = indices[product_id]
            sim_scores = list(enumerate(cosine_similarities[idx] * weight))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

            # Obtener hasta 5 productos similares por cada producto visitado
            product_indices = [i[0] for i in sim_scores[1:6]]
            recommendations = pd.concat([recommendations, all_products_df.iloc[product_indices]])

    # Filtro: Eliminar productos ya visitados
    recommendations = recommendations.drop_duplicates(subset='id')
    recommendations = recommendations[~recommendations['id'].isin(user_visited_df['id'])]

    # Priorizar productos de categorías similares
    if not recommendations.empty:
        visited_categories = user_visited_df['category'].dropna().unique()
        recommendations['category_match'] = recommendations['category'].apply(
            lambda x: x in visited_categories
        )
        recommendations = recommendations.sort_values(by=['category_match', 'created_at'], ascending=[False, False])

    # Limitar recomendaciones
    return recommendations.head(max_records).to_dict(orient='records')

def get_recommendations_html(user_id):
    # Genera una página HTML con recomendaciones para el usuario.
    recommendations = generate_recommendations(user_id)

    if not recommendations:
        return "<h3>No se encontraron recomendaciones.</h3>"

    html = f"<h2>Recomendaciones para el usuario {user_id}</h2><ul>"
    for product in recommendations:
        html += "<li>"
        html += f"<strong>Nombre:</strong> {product['product_name']}<br>"
        html += f"<strong>Descripción:</strong> {product['product_description']}<br>"
        html += f"<strong>Precio:</strong> ${product['product_price']}<br>"
        html += f"<strong>Categoría:</strong> {product['category']}<br>"
        html += f"<strong>Subcategoría:</strong> {product['subcategory']}<br>"
        html += f"<strong>Marca:</strong> {product['product_mark']}<br>"
        html += f"<strong>Modelo:</strong> {product['product_model']}<br>"
        html += f"<strong>ID:</strong> {product['id']}<br>"
        html += "</li>"
    html += "</ul>"
    return html

def get_recommended_product_ids(user_id, max_records=16):
    #Retorna las IDs de los productos recomendados para el usuario en el mismo orden que las recomendaciones HTML.
    recommendations = generate_recommendations(user_id, max_records)
    return [product['id'] for product in recommendations]