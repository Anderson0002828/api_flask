from models.models import MarketechProduct, MarketechProductVisited
from flask import render_template
from database.database import db
import matplotlib.pyplot as plt
import pandas as pd
import os

def get_popularity_matrix():
    visits_data = db.session.query(MarketechProductVisited.product_id).all()
    visits_df = pd.DataFrame(visits_data, columns=["product_id"])
    popularity_df = visits_df.groupby('product_id').size().reset_index(name='popularity')
    popularity_df = popularity_df.sort_values(by='popularity', ascending=False)
    return popularity_df

def generate_popularity_graph():
    popularity_df = get_popularity_matrix()

    plt.figure(figsize=(10, 6))
    plt.bar(popularity_df['product_id'].astype(str), popularity_df['popularity'], color='skyblue')
    plt.xlabel('Product ID')
    plt.ylabel('Popularity (Number of Visits)')
    plt.title('Top Product Popularity')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    static_folder = 'static'
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)

    img_path = os.path.join(static_folder, 'popularity_chart.png')
    plt.savefig(img_path)
    plt.close()

    return img_path, popularity_df

def render_popularity_page():
    img_path, popularity_df = generate_popularity_graph()

    product_details = []
    for product_id in popularity_df['product_id']:
        product = MarketechProduct.query.filter_by(id=product_id).first()
        if product:
            product_data = {
                "id": product.id,
                "name": product.product_name,
                "description": product.product_description,
                "price": product.product_price,
                "popularity": popularity_df[popularity_df['product_id'] == product_id]['popularity'].values[0]
            }
            product_details.append(product_data)

    return render_template("popularity.html", products=product_details, img_path=img_path)