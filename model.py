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
    password_hash = db.Column(db.String(1000), nullable=False)
    
    
    def __repr__(self):
        return f"User( '{self.user_firstname},{self.user_lastname}', '{self.email_address}')"
    
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

 