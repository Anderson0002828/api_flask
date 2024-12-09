from flask import Blueprint, jsonify
from database.database import db

products_route = Blueprint("products", __name__)

@products_route.route("/", methods=["GET"])
def get_products():
    try:
        result = db.session.execute("SELECT * FROM marketech_products")
        products = [dict(row) for row in result.fetchall()]
        return jsonify(products), 200

    except Exception as e:
        return jsonify({"error": f"Error al obtener los productos: {str(e)}"}), 500
