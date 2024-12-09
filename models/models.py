from database.database import db
from datetime import datetime

class MarketechUser(db.Model):
    __tablename__ = 'marketech_users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    dni = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    region = db.Column(db.String(100))
    province = db.Column(db.String(100))
    district = db.Column(db.String(100))
    reference = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "email": self.email,
            "dni": self.dni,
            "phone": self.phone,
            "address": self.address,
            "region": self.region,
            "province": self.province,
            "district": self.district,
            "reference": self.reference,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class MarketechProduct(db.Model):
    __tablename__ = 'marketech_products'
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('marketech_sellers.id'), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    product_mark = db.Column(db.String(255), nullable=False)
    product_model = db.Column(db.String(255), nullable=False)
    product_description = db.Column(db.Text, nullable=False)
    product_price = db.Column(db.Numeric(10, 2), nullable=False)
    product_discount = db.Column(db.Numeric(10, 2), default=0.00)
    product_quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(255), nullable=False)
    subcategory = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "seller_id": self.seller_id,
            "product_name": self.product_name,
            "product_mark": self.product_mark,
            "product_model": self.product_model,
            "product_description": self.product_description,
            "product_price": float(self.product_price),
            "product_discount": float(self.product_discount),
            "product_quantity": self.product_quantity,
            "category": self.category,
            "subcategory": self.subcategory,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        
        
class MarketechProductVisited(db.Model):
    __tablename__ = 'marketech_products_visited'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('marketech_users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('marketech_products.id'), nullable=False)
    visited_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    user = db.relationship('MarketechUser', backref=db.backref('visited_products', lazy=True))
    product = db.relationship('MarketechProduct', backref=db.backref('user_visits', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'visited_at': self.visited_at,
            'user': {
                'id': self.user.id,
                'name': self.user.name,
                'last_name': self.user.last_name,
                'email': self.user.email,
                'created_at': self.user.created_at
            },
            'product': {
                'id': self.product.id,
                'name': self.product.product_name,
                'description': self.product.product_description,
                'price': float(self.product.product_price),
                "discount": float(self.product.product_discount),
                "quantity": self.product.product_quantity,
                'category': self.product.category,
                "subcategory": self.product.subcategory,
                "mark": self.product.product_mark,
                "model": self.product.product_model,
                "seller_id": self.product.seller_id,
                'created_at': self.product.created_at,
            }
        }
        
class MarketechSearchHistory(db.Model):
    __tablename__ = 'marketech_search_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('marketech_users.id'), nullable=False)
    search_term = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    user = db.relationship('MarketechUser', backref=db.backref('search_history', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'search_term': self.search_term,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': {
                'id': self.user.id,
                'name': self.user.name,
                'last_name': self.user.last_name,
                'email': self.user.email,
                'created_at': self.user.created_at.strftime('%a, %d %b %Y %H:%M:%S GMT') if self.user.created_at else None
            }
        }
        
class MarketechWishList(db.Model):
    __tablename__ = 'marketech_wish_list'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('marketech_users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('marketech_products.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    user = db.relationship('MarketechUser', backref=db.backref('wish_list', lazy=True))
    product = db.relationship('MarketechProduct', backref=db.backref('wish_list_users', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'user': {
                'id': self.user.id,
                'name': self.user.name,
                'last_name': self.user.last_name,
                'email': self.user.email,
                'created_at': self.product.created_at
            },
            'product': {
                'id': self.product.id,
                'name': self.product.product_name,
                'description': self.product.product_description,
                'price': float(self.product.product_price),
                "discount": float(self.product.product_discount),
                "quantity": self.product.product_quantity,
                'category': self.product.category,
                "subcategory": self.product.subcategory,
                "mark": self.product.product_mark,
                "model": self.product.product_model,
                "seller_id": self.product.seller_id,
                'created_at': self.product.created_at,
            }
        }
        
class MarketechShoppingCart(db.Model):
    __tablename__ = 'marketech_shopping_cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('marketech_users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('marketech_products.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    cantidad = db.Column(db.Integer, nullable=False, default=1)

    user = db.relationship('MarketechUser', backref=db.backref('shopping_cart', lazy=True))
    product = db.relationship('MarketechProduct', backref=db.backref('cart_users', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'cantidad': self.cantidad,
            'user': {
                'id': self.user.id,
                'name': self.user.name,
                'last_name': self.user.last_name,
                'email': self.user.email,
                'created_at': self.user.created_at
            },
            'product': {
                'id': self.product.id,
                'name': self.product.product_name,
                'description': self.product.product_description,
                'price': float(self.product.product_price),
                "discount": float(self.product.product_discount),
                "quantity": self.product.product_quantity,
                'category': self.product.category,
                "subcategory": self.product.subcategory,
                "mark": self.product.product_mark,
                "model": self.product.product_model,
                "seller_id": self.product.seller_id,
                'created_at': self.product.created_at,
            }
        }