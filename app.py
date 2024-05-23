
import os
import psycopg2
from flask import Flask, render_template, request,session, redirect, url_for, jsonify,flash,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from model import ProductCategory, ProductList, db, User,MerchantUser
from sqlalchemy.sql.expression import func

from datetime import datetime as dt
import json
from fastapi.encoders import jsonable_encoder

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:dhiman223@localhost:5432/ecommercedb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['STATIC_FOLDER'] = 'static'
migrate = Migrate(app, db)
db.init_app(app)
PRODUCT_IMAGE_UPLOAD_FOLDER = 'static/img/product_images/'



app.config['SECRET_KEY'] = 'thisissecret'
app.config['STATIC_FOLDER'] = 'static'
app.config['PRODUCT_IMAGE_UPLOAD_FOLDER'] = 'static/img/product_images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, upload_folder):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        dt_now = dt.now().strftime("%Y%m%d%H%M%S%f")
        file_extension = filename.rsplit('.', 1)[1].lower()
        filename_to_save = f"{dt_now}_{filename}"
        file_path = os.path.join(upload_folder, filename_to_save)
        file.save(file_path)
        return file_path
    return None

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()



def get_random_products(limit):
    return ProductList.query.order_by(func.random()).limit(limit).all()

# Routes
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(directory='static', filename='favicon.ico')

@app.route('/')
def index():
    try:
        random_products = get_random_products(6)
        categories = ProductCategory.query.all()
        if not categories:
            print("No categories found.")
        else:
            print(f"Categories found: {[category.product_category_name for category in categories]}")
        if not random_products:
            print("No random products found.")
        else:
            for product in random_products:
                print(f"Random Product: {product.product_main_image}")
        
        # Render the index template with the fetched data
        return render_template('index.html', random_products=random_products, categories=categories)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template('error.html', message="An error occurred while loading the page.")


# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/userproduct/<int:category_id>')
def get_products_by_category(category_id):
    # Query the database to get products for the given category ID
    products = ProductList.query.filter_by(category_id=category_id).all()
   
    return render_template('userproduct.html', products=products)

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
        return jsonify({'message': 'Invalid email or password', 'success':False}), 401
    else:
        user = jsonable_encoder(user)
        print(user)
        print(type(user))
        session["name"] = user["user_id"]
        session["user_info"] = user
        return jsonify({'message': 'Logged in successfully','success':True}), 200


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/user-home')
def user_home():
    # Retrieve the user details of the currently logged-in user
    if 'user_id' in session:
        user_id = session['user_id']
        current_user = User.query.get(user_id)
    else:
        current_user = None
    
    # Fetch products and categories for display
    products = ProductList.query.all()
    categories = ProductCategory.query.all()
    
    # Pass the user details and other necessary data to the template context
    return render_template('user_home.html', current_user=current_user, products=products, categories=categories)

@app.route('/merchantsignup', methods=['GET'])
def show_merchantsignup_form():
    return render_template('merchantsignup.html')


@app.route('/signupmerchant', methods=['POST'])
def process_merchantsignup_form():
    try:
        # Get form data from request
        data = request.form

        # Validate required fields
        required_fields = ['firstname', 'lastname', 'companyregisterno', 'email', 'companyaddress', 'companypostcode', 'mobile', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'message': f'Missing or empty field: {field}'}), 400
        
        # Check if email address is already registered
        existing_user = MerchantUser.query.filter_by(company_emailaddress=data['email']).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'Email address is already registered.'}), 400
        
        # Generate password hash
        password_hash = generate_password_hash(data['password'])
        
        # Create new MerchantUser object
        new_merchantuser = MerchantUser(
            firstname=data['firstname'],
            lastname=data['lastname'],
            company_name=data.get('companyname', ''),  # Optional field, use data.get to handle missing key
            company_emailaddress=data['email'],
            company_address=data['companyaddress'],
            company_mobile=data['mobile'],
            company_postcode=data['companypostcode'],
            company_registrationno=data['companyregisterno'],
            company_password_hash=password_hash
        )

        # Add new user to the database
        db.session.add(new_merchantuser)
        db.session.commit()  # Commit changes to the database
        
        # Return success response
        return jsonify({'success': True, 'message': 'Merchant signup successful!'})

    except Exception as e:
        # Log error
        app.logger.error(f"Error occurred during signup: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while signing up.'}), 500

@app.route('/loginmerchant', methods=['POST','GET'])
def loginmerchant():
    try:
        email = request.form['email']
        password = request.form['password']
    except KeyError:
        return jsonify({'message': 'Email or password field is missing', 'success': False}), 400

    userMerchant = MerchantUser.query.filter_by(company_emailaddress=email).first()
    if not userMerchant or not check_password_hash(userMerchant.company_password_hash, password):
        return jsonify({'message': 'Invalid email or password', 'success': False}), 401
    else:
        userMerchant = jsonable_encoder(userMerchant)
        session["merchant_name"] = userMerchant["company_id"]
        session["merchant_user_info"] = userMerchant
        return jsonify({'message': 'Logged in successfully', 'success': True}), 200
    
@app.route('/logoutmerchant')
def logout_merchant():
    if session.get("merchant_name") is not None:
        session.pop('merchant_name', None)
        session.pop('merchant_user_info', None)  # Change this to match the session key for merchant user info
    return redirect("/admin", code=302)


@app.route('/addnewcategory', methods=['GET','POST'])
def product_category():
    if request.method == 'POST':
        category_name = request.form['product_category_name']
        category_code = request.form['product_category_code']
        
        new_category = ProductCategory(product_category_name=category_name, product_category_code=category_code)
        db.session.add(new_category)
        db.session.commit()
        
        return redirect(url_for('categories'))  # Redirect to a page after adding category
    
    categories = ProductCategory.query.all()
    return render_template('addnewcategory.html', categories=categories)


@app.route('/delete-proceed/<id>/', methods=['POST'])
def deleteproceed(id):
    output_msg = ""
    success = False

    try:
        # Check if the contact to delete does not exist in the database
        category_to_delete = ProductCategory.query.filter_by(id=id).first()
        if not category_to_delete:
            output_msg = "Sorry, this user no longer exists in our system. Just cancel and reload the page."
        # Do this if the contact to delete is existing in the database
        else:
            # grab static url of image of category to delete
            # get the full url path

            db.session.delete(category_to_delete)

            # delete the image in the url path
            db.session.commit()
            success = True
            output_msg = "This user has successfully been removed from the system"
    except:
        output_msg = "Whoops something went wrong while performing this deletion. Please reload page and try again"    
    return jsonify({'output_msg': output_msg, 'success': success})

@app.route('/delete-product/<int:id>/', methods=['POST'])
def delete_product(id):
    output_msg = ""
    success = False

    try:
        # Check if the product to delete exists in the database
        product_to_delete = ProductList.query.get(id)
        if not product_to_delete:
            output_msg = "Sorry, this product no longer exists in our system. Please reload the page."
        else:
            # Delete the product from the database
            db.session.delete(product_to_delete)
            db.session.commit()
            success = True
            output_msg = "This product has been successfully removed from the system"
    except Exception as e:
        output_msg = f"An error occurred while deleting the product: {str(e)}"

    return jsonify({'output_msg': output_msg, 'success': success})

@app.route('/categories')
def categories():
    categories = ProductCategory.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/categories', methods=['GET'])
def productCategory():
    categories = ProductCategory.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/logout')
def logout():
    if session.get("name") is not None:
        session.pop('name', None)
        session.pop('user_info', None)
    return redirect("/", code=302)

@app.route('/edit/<int:category_id>')
def edit_category(category_id):
    category = ProductCategory.query.get(category_id)
    if category:
        return render_template('edit_category.html', category=category)
    else:
        return redirect(url_for('categories'))


@app.route('/update_category/<int:category_id>', methods=['POST'])
def update_category(category_id):
    category = ProductCategory.query.get(category_id)
    if category:
        category.product_category_name = request.form['category_name']
        category.product_category_code = request.form['category_code']
        db.session.commit()
        return redirect(url_for('categories'))
    
    else:
        return redirect(url_for('categories'))

@app.route('/addnewproduct/<int:category_id>', methods=['GET', 'POST'])
def add_new_product_route(category_id):
    category = ProductCategory.query.get(category_id)
    if not category:
        return redirect(url_for('categories'))

    if request.method == 'POST':
        # Retrieve form data and handle file uploads
        product_name = request.form['product_name']
        product_code = request.form['product_code']
        product_title = request.form['product_title']
        product_description = request.form['product_description']
        product_price = float(request.form['product_price'])
        product_quantity = int(request.form['product_quantity'])
        product_main_image = request.files['product_main_image']
        product_secondary_image1 = request.files.get('product_secondary_image1')
        product_secondary_image2 = request.files.get('product_secondary_image2')

        # Save the images
        main_image_path = save_file(product_main_image, app.config['PRODUCT_IMAGE_UPLOAD_FOLDER'])
        secondary_image1_path = save_file(product_secondary_image1, app.config['PRODUCT_IMAGE_UPLOAD_FOLDER']) if product_secondary_image1 else None
        secondary_image2_path = save_file(product_secondary_image2, app.config['PRODUCT_IMAGE_UPLOAD_FOLDER']) if product_secondary_image2 else None

        try:
            # Create a new ProductList object and add it to the database
            new_product = ProductList(
                product_name=product_name,
                product_code=product_code,
                product_title=product_title,
                product_description=product_description,
                product_price=product_price,
                product_quantity=product_quantity,
                product_main_image=main_image_path,
                product_secondary_image1=secondary_image1_path,
                product_secondary_image2=secondary_image2_path,
                category_id=category_id
            )
            db.session.add(new_product)
            db.session.commit()
            return redirect(url_for('viewproducts', category_id=category_id))
        except Exception as e:
            print("An error occurred:", e)
            return render_template('addnewproduct.html', product_category=category, error_message="An error occurred. Please try again.")
    else:
        return render_template('addnewproduct.html', product_category=category)


@app.route('/viewproducts/<int:category_id>', methods=['GET', 'POST'])
def viewproducts(category_id):
    products = ProductList.query.filter_by(category_id=category_id).all()
    product_category = ProductCategory.query.get(category_id)  # Fetch the product category
    for product in products:
        print(product.product_main_image)
        product.product_main_image = '/' + product.product_main_image
    return render_template('viewproducts.html', products=products, product_category=product_category)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    try:
        # Fetch the product from the database
        product = ProductList.query.get(product_id)
        if not product:
            flash('Product not found!', 'error')
            return redirect(url_for('viewproducts', category_id=product.category_id))

        # Fetch the product category
        product_category = ProductCategory.query.get(product.category_id)

        if request.method == 'POST':
            # Retrieve form data
            product.product_name = request.form['product_name']
            product.product_code = request.form['product_code']
            product.product_title = request.form['product_title']
            product.product_description = request.form['product_description']
            product.product_price = float(request.form['product_price'])
            product.product_quantity = int(request.form['product_quantity'])

            # Commit changes to the database
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('viewproducts', category_id=product.category_id))

    except Exception as e:
        print(f"An error occurred: {e}")
        flash('An error occurred while updating the product. Please try again.', 'error')

    # Render the edit_product.html template with the product and product category
    return render_template('edit_product.html', product=product, product_category=product_category)



@app.route('/productdescription.html')
def product_description():
    product_id = request.args.get('product_id')
    if product_id:
        product = ProductList.query.get_or_404(product_id)
        # Assuming you want to pass categories to the template as well
        categories = ProductCategory.query.all()
        return render_template('productdescription.html', product=product, categories=categories)


if __name__ == '__main__':
    app.run(debug=True)
