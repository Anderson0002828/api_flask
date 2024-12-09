from models.models import MarketechProductVisited, MarketechProduct
from database.database import db
import pandas as pd

def get_popularity_matrix():
    visits_data = db.session.query(MarketechProductVisited.product_id, MarketechProductVisited.user_id).all()

    visits_df = pd.DataFrame(visits_data, columns=["product_id", "user_id"])

    popularity_df = visits_df.groupby('product_id').size().reset_index(name='popularity')

    popularity_df = popularity_df.sort_values(by='popularity', ascending=False)

    return popularity_df

def get_recommendations_html_popularity():
    popularity_df = get_popularity_matrix()

    recommended_products = []
    for product_id in popularity_df['product_id'].head(8):
        product = MarketechProduct.query.filter_by(id=product_id).first()
        recommended_products.append(product.to_dict())

    recommendations_html = "<h3>Top 8 Most Popular Products</h3>"
    for product in recommended_products:
        recommendations_html += f"""
        <div>
            <h4>{product['product_name']}</h4>
            <p>{product['product_description']}</p>
            <p>Price: ${product['product_price']}</p>
            <p>ID del producto: {product['id']}</p>
        </div>
        """

    return recommendations_html

def get_recommended_product_ids_popularity():
    popularity_df = get_popularity_matrix()

    top_products = popularity_df.head(8)

    return top_products['product_id'].tolist()