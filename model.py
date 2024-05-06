from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
# Create A Model For Table
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    user_firstname = db.Column(db.String(1000))
    user_lastname = db.Column(db.String(1000))
    email_address = db.Column(db.String(500))
    mobile = db.Column(db.String(30))
    
    
    def __repr__(self):
        return f"User( '{self.user_firstname},{self.user_lastnamename}', '{self.email_address}')"



 