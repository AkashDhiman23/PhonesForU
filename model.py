from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# User Model
class User(db.Model):
    __tablename__ = 'user'
    
    user_id = db.Column(db.Integer, primary_key=True)
    user_firstname = db.Column(db.String(1000))
    user_lastname = db.Column(db.String(1000))
    email_address = db.Column(db.String(500))
    mobile = db.Column(db.String(30))
    password_hash = db.Column(db.String(1000), nullable=False)
    
    # Relationships
    cart_items = relationship('Cart', back_populates='user', cascade='all, delete-orphan')
    payments = relationship('Payment', back_populates='user', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"User('{self.user_firstname}, {self.user_lastname}', '{self.email_address}')"

# Payment Model
class Payment(db.Model):
    __tablename__ = 'payment'
    
    transaction_id = db.Column(db.String(255), primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # Define foreign key
    
    # Relationships
    user = relationship("User", back_populates="payments")
    order = relationship("Order", back_populates="payment")
    
    def __repr__(self):
        return f"<Payment {self.transaction_id}>"


# Other models remain unchanged for consistency and completeness
# MerchantUser, ProductCategory, ProductList, Cart, Order, OrderItem

class MerchantUser(db.Model):
    __tablename__ = 'MerchantUser'
    company_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(1000))
    lastname = db.Column(db.String(1000))
    company_name = db.Column(db.String(1000))
    company_emailaddress = db.Column(db.String(500))
    company_address = db.Column(db.String(500))
    company_mobile = db.Column(db.String(30))
    company_postcode = db.Column(db.String(500))
    company_registrationno = db.Column(db.String(500))
    company_password_hash = db.Column(db.String(1000))  
    
    def __repr__(self):
        return f"MerchantUser('{self.firstname}, {self.lastname}', '{self.company_emailaddress}')"


class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True)
    product_category_name = db.Column(db.String(255), unique=True, nullable=False)
    product_category_code = db.Column(db.String(50), unique=True, nullable=False)
    products = relationship('ProductList', back_populates='category')

    def __repr__(self):
        return f"<ProductCategory id={self.id}, name='{self.product_category_name}'>"


class ProductList(db.Model):
    __tablename__ = 'Product'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    product_title = db.Column(db.String(255), nullable=False)
    product_description = db.Column(db.String(1000), nullable=False)
    product_price = db.Column(db.Numeric(10, 2), nullable=False)  # Decimal with 2 decimal places
    product_quantity = db.Column(db.Integer, nullable=False)
    product_main_image = db.Column(db.String(255), nullable=False)
    product_secondary_image1 = db.Column(db.String(255))
    product_secondary_image2 = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('product_category.id'), nullable=False)
    
    # Relationships
    category = relationship('ProductCategory', back_populates='products')
    cart_items = relationship('Cart', back_populates='product', cascade='all, delete-orphan')
    order_items = relationship('OrderItem', back_populates='product', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<ProductList id={self.id}, name='{self.product_name}'>"


class Cart(db.Model):
    __tablename__ = 'cart'
    cart_item_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    # Relationships
    user = relationship('User', back_populates='cart_items')
    product = relationship('ProductList', back_populates='cart_items')
    
    def __repr__(self):
        return f"<Cart cart_item_id={self.cart_item_id}, user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity}>"


class Order(db.Model):
    __tablename__ = 'orders'
    
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user_first_name = db.Column(db.String, nullable=False)
    user_last_name = db.Column(db.String, nullable=False)
    user_email_address = db.Column(db.String, nullable=False)
    user_mobile = db.Column(db.String, nullable=False)
    shipping_address = db.Column(db.String, nullable=False)
    shipping_city = db.Column(db.String, nullable=False)
    shipping_state = db.Column(db.String, nullable=False)
    shipping_zip = db.Column(db.String, nullable=False)
    shipping_country = db.Column(db.String, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", uselist=False, back_populates="order")
    
    def __repr__(self):
        return f"<Order {self.order_id}>"


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id'), nullable=False)
    product_name = db.Column(db.String, nullable=False)
    product_price = db.Column(db.Numeric(10, 2), nullable=False)
    product_quantity = db.Column(db.Integer, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("ProductList", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem {self.order_item_id}>"
