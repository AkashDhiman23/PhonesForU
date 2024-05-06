
import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from model import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:dhiman223@localhost:5432/ecommercedb"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
        return 'Email address already exists!'
    
    password_hash = generate_password_hash(password)

    new_user = User(user_firstname=firstname, user_lastname=lastname, email_address=email, password_hash=password_hash, mobile=mobile)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email_address=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return 'Invalid email or password'

    return 'Logged in successfully'

if __name__ == '__main__':
    app.run(debug=True)
