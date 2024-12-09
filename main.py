from models.models import MarketechUser, MarketechProduct, MarketechProductVisited, MarketechSearchHistory, MarketechWishList, MarketechShoppingCart
from services.recommendation_by_popularity import get_recommendations_html_popularity, get_recommended_product_ids_popularity
from services.recommendation_model import get_recommendations_html, get_recommended_product_ids
from flask import Flask, Blueprint, jsonify, request, render_template
from services.product_popularity import render_popularity_page
from database.database import db, init_app
from flask_cors import CORS, cross_origin
from services.chat import chatbot_route
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost"}})
init_app(app)

app.register_blueprint(chatbot_route, url_prefix="/chat")
popularity_bp = Blueprint('popularity', __name__)

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = MarketechUser.query.get(user_id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({'error': 'User not found'}), 404

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = MarketechProduct.query.get(product_id)
    if product:
        return jsonify(product.to_dict())
    return jsonify({'error': 'Product not found'}), 404

@app.route('/product_visited/<int:user_id>', methods=['GET'])
def get_visited_product(user_id):
    visited_items= MarketechProductVisited.query.filter_by(user_id=user_id).all()
    if visited_items:
        return jsonify([item.to_dict() for item in visited_items])
    return jsonify({'error': 'Product visit not found'}), 404

@app.route('/search_history/<int:user_id>', methods=['GET'])
def get_search_history(user_id):
    search_history = MarketechSearchHistory.query.filter_by(user_id=user_id).all()
    if search_history:
        return jsonify([item.to_dict() for item in search_history])
    return jsonify({'error': 'Search history not found'}), 404

@app.route('/wishlist/<int:user_id>', methods=['GET'])
def get_wish_list(user_id):
    wish_list_items = MarketechWishList.query.filter_by(user_id=user_id).all()
    if wish_list_items:
        return jsonify([item.to_dict() for item in wish_list_items])
    return jsonify({'error': 'No wish list found for this user'}), 404

@app.route('/shoppingcart/<int:user_id>', methods=['GET'])
def get_shopping_cart(user_id):
    cart_items = MarketechShoppingCart.query.filter_by(user_id=user_id).all()
    if cart_items:
        return jsonify([item.to_dict() for item in cart_items])
    return jsonify({'error': 'No shopping cart found for this user'}), 404

@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    recommendations_html = get_recommendations_html(user_id)
    return recommendations_html

@app.route('/recommendations_ids/<int:user_id>', methods=['GET'])
@cross_origin()
def get_recommended_product_ids_route(user_id):
    recommended_product_ids = get_recommended_product_ids(user_id)
    if not recommended_product_ids:
        return jsonify({'message': 'No se encontraron recomendaciones.'}), 404
    recommended_product_ids = [int(product_id) for product_id in recommended_product_ids]
    return jsonify(recommended_product_ids)

@app.route('/recommendations_popularity_html', methods=['GET'])
def get_popularity_recommendations_html():
    recommendations_html = get_recommendations_html_popularity()
    return recommendations_html

@app.route('/popularity')
def popularity():
    return render_popularity_page()

@app.route('/recommendations_popularity_ids', methods=['GET'])
@cross_origin()
def get_popularity_recommended_product_ids_route():
    recommended_product_ids = get_recommended_product_ids_popularity()
    if not recommended_product_ids:
        return jsonify({'message': 'No se encontraron recomendaciones populares.'}), 404
    return jsonify(recommended_product_ids)

@app.route('/chat', methods=['GET', 'POST'])
def chat_page():
    chatbot_response = None

    if request.method == 'POST':
        user_question = request.form.get('question', '').strip()

        if user_question:
            try:
                url = "http://127.0.0.1:5000/chat/"
                headers = {"Content-Type": "application/json"}
                response = requests.post(url, json={"question": user_question}, headers=headers)
                response_data = response.json()

                if response_data.get("success"):
                    chatbot_response = response_data.get("response")
                else:
                    chatbot_response = "Lo siento, no pude encontrar una respuesta adecuada."
            except Exception as e:
                chatbot_response = f"Error al conectarse con el chatbot: {str(e)}"

    return render_template('chat.html', chatbot_response=chatbot_response)

@app.route("/")
def index():
    return render_template("welcome.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)