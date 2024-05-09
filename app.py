
import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from model import db, User,MerchantUser


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:dhiman223@localhost:5432/ecommercedb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['STATIC_FOLDER'] = 'static'
migrate = Migrate(app, db)
db.init_app(app)

# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['POST'])
def signup():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    mobile = request.form['mobile']

    existing_user = User.query.filter_by(email_address=email).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Email address is already registered.'})
    
    password_hash = generate_password_hash(password)

    new_user = User(user_firstname=firstname, user_lastname=lastname, email_address=email, password_hash=password_hash, mobile=mobile)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Signup successful!'})

@app.route('/login', methods=['GET','POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email_address=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid email or password'}), 401

    return jsonify({'message': 'Logged in successfully'}), 200


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/user')
def user():
    return render_template('user.html')


@app.route('/signupmerchant', methods=['POST'])
def signupmerchant():
    data = request.form
    print("DATA IS:")
    print(data)
    existing_user = MerchantUser.query.filter_by(company_emailaddress=data['email']).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Email address is already registered.'}), 400
    
    password_hash = generate_password_hash(data['password'])
    new_merchantuser = MerchantUser(
        firstname=data['firstname'],
        lastname=data['lastname'],
        company_name=data['companyname'],
        company_emailaddress=data['email'],
        company_address=data['companyaddress'],
        company_mobile=data['mobile'],
        company_postcode=data['companypostcode'],
        company_registrationno=data['companyregisterno'],
        company_password_hash=password_hash
    )
    print(new_merchantuser)
    db.session.add(new_merchantuser)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Merchant signup successful!'})




@app.route('/loginmerchant', methods=['POST'])
def loginmerchant():
    email = request.form['email']
    password = request.form['password']

    userMerchant = MerchantUser.query.filter_by(company_emailaddress=email).first()
    if not userMerchant or not check_password_hash(userMerchant.company_password_hash, password):
        return jsonify({'message': 'Invalid email or password'}), 401

    return jsonify({'message': 'Logged in successfully'}), 200
if __name__ == '__main__':
    app.run(debug=True)

