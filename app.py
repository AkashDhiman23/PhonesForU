import os
import psycopg2
from flask import Flask, render_template, request,session, redirect, url_for, jsonify,flash,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from model import ProductCategory, ProductList, db, User,MerchantUser,Cart
from sqlalchemy.sql.expression import func
from sqlalchemy import Column, Integer, ForeignKey
from datetime import datetime as dt
import json
from fastapi.encoders import jsonable_encoder

app = Flask(__name__)

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
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


def calculate_total_price(cart):
    total_price = 0
    for item in cart:
        product = item.get('product')
        if product:
            total_price += product.get('price', 0) * item.get('quantity', 0)
    return total_price

# Routes
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


@app.route('/')
def index():
    try:
        random_products = get_random_products(6)
        categories = ProductCategory.query.all()
        # Ensure cart is defined
        cart = session.get('cart', [])
        return render_template('index.html', random_products=random_products, categories=categories, cart=cart)
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

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email_address=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid email or password', 'success': False}), 401
    else:
        session["name"] = user.user_id  # Set the user's ID in session
        session["user_info"] = jsonable_encoder(user)  # Store user info in session if needed
        
        # Load cart from database
        cart_items = Cart.query.filter_by(user_id=user.user_id).all()
        cart = [{'product_id': item.product_id, 'quantity': item.quantity} for item in cart_items]
        session['cart'] = cart
        
        return jsonify({'message': 'Logged in successfully', 'success': True}), 200



@app.route('/admin')
def admin():
    return render_template('admin.html')



@app.route('/user-home', methods=['GET'])
def user_home():
    if 'user_id' in session:
        user_id = session['user_id']
        current_user = User.query.get(user_id)
    else:
        current_user = None

    products = ProductList.query.all()
    categories = ProductCategory.query.all()
    # Ensure cart is defined
    cart = session.get('cart', [])

    return render_template('user_home.html', current_user=current_user, products=products, categories=categories, cart=cart)

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
    
@app.route('/loginmerchant', methods=['POST', 'GET'])
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
        session["merchant_firstname"] = userMerchant["firstname"]
        session["merchant_lastname"] = userMerchant["lastname"]
        return jsonify({'message': 'Logged in successfully', 'success': True}), 200

    
@app.route('/logoutmerchant')
def logout_merchant():
    if session.get("merchant_name") is not None:
        session.pop('merchant_name', None)
        session.pop('merchant_user_info', None)  # Change this to match the session key for merchant user info
    return redirect("/admin", code=302)




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

@app.route('/showcategories')
def showcategories():
    categories = ProductCategory.query.all()
    return render_template('showcategories.html', categories=categories)






@app.route('/categories', methods=['GET', 'POST'])
def categories():
    merchant_name = session.get('merchant_name')
    merchant_password = session.get('merchant_password')
    
    if request.method == 'POST':
        category_name = request.form['product_category_name']
        category_code = request.form['product_category_code']
        
        # Check if category name already exists
        existing_category = ProductCategory.query.filter_by(product_category_name=category_name).first()
        if (existing_category):
            flash('Category name already exists. Please use a different name.', 'error')
            return redirect(url_for('categories'))
        
        new_category = ProductCategory(product_category_name=category_name, product_category_code=category_code)
        try:
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
        
        return redirect(url_for('categories'))  # Redirect to the categories page after adding a category
    
    categories = ProductCategory.query.all()
    return render_template('categories.html', categories=categories, merchant_name=merchant_name, merchant_password=merchant_password)






# @app.route('/categories', methods=['GET'])
# def productCategory():
#     categories = ProductCategory.query.all()
#     return render_template('categories.html', categories=categories)

@app.route('/logout')
def logout():
    if 'name' in session:
        user_id = session['name']
        cart = session.get('cart', [])
        
        # Clear existing cart items for the user
        Cart.query.filter_by(user_id=user_id).delete()
        
        # Add current cart items to the database
        for item in cart:
            new_cart_item = Cart(user_id=user_id, product_id=item['product_id'], quantity=item['quantity'])
            db.session.add(new_cart_item)
        
        db.session.commit()
        
        # Clear session
        session.pop('name', None)
        session.pop('user_info', None)
        session.pop('cart', None)
        session.pop('cart_quantities', None)
    
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

@app.route('/add_to_cart/<int:product_id>', methods=['GET'])
def add_to_cart(product_id):
    if 'name' not in session:
        return redirect(url_for('login'))
    
    user_id = session['name']
    cart = session.get('cart', [])
    
    # Check if the product_id is already in the cart
    index = next((i for i, item in enumerate(cart) if item['product_id'] == product_id), None)
    
    if index is not None:
        # If the product is already in the cart, increment its quantity
        cart[index]['quantity'] += 1
        # Update the quantity in the database
        cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
        cart_item.quantity = cart[index]['quantity']
    else:
        # If the product is not in the cart, add it with quantity 1
        cart.append({'product_id': product_id, 'quantity': 1})
        # Add new cart item to the database
        new_cart_item = Cart(user_id=user_id, product_id=product_id, quantity=1)
        db.session.add(new_cart_item)
    
    db.session.commit()
    session['cart'] = cart
    
    return redirect(url_for('user_home'))


@app.route('/remove_from_cart/<int:product_id>', methods=['GET'])
def remove_from_cart(product_id):
    if 'name' not in session:
        return jsonify(success=False, message='User not logged in')

    user_id = session['name']
    cart = session.get('cart', [])

    index = next((i for i, item in enumerate(cart) if item['product_id'] == product_id), None)

    if index is not None:
        cart.pop(index)
        # Remove the item from the database
        Cart.query.filter_by(user_id=user_id, product_id=product_id).delete()

        db.session.commit()
        session['cart'] = cart

        return redirect(url_for('user_home'))

    return jsonify(success=False, message='Product not found in cart')

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    if 'name' not in session:
        return redirect(url_for('login'))
    
    user_id = session['name']
    
    # Clear cart in the database
    Cart.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    # Clear cart in the session
    session.pop('cart', None)
    session.pop('cart_quantities', None)
    
    return jsonify(success=True)


@app.route('/update_cart_quantity/<int:product_id>/<string:action>', methods=['GET'])
def update_cart_quantity(product_id, action):
    if 'name' not in session:
        return jsonify(success=False, message='User not logged in')

    user_id = session['name']
    cart = session.get('cart', [])

    # Find the item in the cart
    index = next((i for i, item in enumerate(cart) if item['product_id'] == product_id), None)

    if index is not None:
        if action == 'increase':
            cart[index]['quantity'] += 1
        elif action == 'decrease' and cart[index]['quantity'] > 1:
            cart[index]['quantity'] -= 1
        
        # Update the quantity in the database
        cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
        cart_item.quantity = cart[index]['quantity']

        db.session.commit()
        session['cart'] = cart

        return redirect(url_for('user_home'))

    return jsonify(success=False, message='Product not found in cart')

@app.route('/user-cart', methods=['GET', 'POST'])
def user_cart():
    if 'name' not in session:
        return redirect(url_for('login'))
    
    user_id = session['name']
    
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    cart = []
    
    # Iterate over cart items and construct the cart data
    for cart_item in cart_items:
        product = {
            'cart_item_id': cart_item.cart_item_id,
            'product_id': cart_item.product_id,
            'product_name': cart_item.product.product_name,
            'product_main_image': cart_item.product.product_main_image,
            'product_price': cart_item.product.product_price,
            'quantity': cart_item.quantity,
            'item_total_price': cart_item.product.product_price * cart_item.quantity
        }
        cart.append(product)
    
    # Calculate total quantity and total price based on cart data
    total_quantity = sum(item['quantity'] for item in cart)
    total_price = sum(item['item_total_price'] for item in cart)
    
    return render_template('user_cart.html', cart=cart, total_quantity=total_quantity, total_price=total_price)


@app.route('/update-cart-item', methods=['POST'])
def update_cart_item():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    data = request.get_json()
    cart_item_id = data.get('cart_item_id')
    new_quantity = data.get('quantity')

    # Retrieve the cart item from the database
    cart_item = Cart.query.filter_by(cart_item_id=cart_item_id, user_id=session['user_id']).first()
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404

    # Update the quantity of the cart item
    cart_item.quantity = new_quantity
    db.session.commit()

    # Calculate new item total price
    new_item_total_price = cart_item.product.product_price * new_quantity

    return jsonify({
        'message': 'Cart item quantity updated successfully',
        'new_item_total_price': new_item_total_price
    }), 200



@app.route('/checkout')
def checkout():
    # Check if user is logged in
    if 'name' not in session:
        return redirect(url_for('login'))  # Redirect to login page if user is not logged in
    
    user_id = session['name']
    user = User.query.get(user_id)

    if not user:
        return "User not found"  # Handle case where user does not exist (optional)

    # Retrieve cart items for the current user
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    # Calculate total price from cart items
    total_price = sum(item.product.product_price * item.quantity if item.product else 0 for item in cart_items)

    return render_template('checkout.html', user=user, cart_items=cart_items, total_price=total_price)

@app.route('/place-order', methods=['POST'])
def place_order():
    # Fetch form data
    shipping_address = request.form.get('shipping_address')
    shipping_city = request.form.get('shipping_city')
    shipping_state = request.form.get('shipping_state')
    shipping_zip = request.form.get('shipping_zip')
    shipping_country = request.form.get('shipping_country')

    billing_address = request.form.get('billing_address')
    billing_city = request.form.get('billing_city')
    billing_state = request.form.get('billing_state')
    billing_zip = request.form.get('billing_zip')
    billing_country = request.form.get('billing_country')

    # Check if the billing address is the same as shipping address
    if request.form.get('same_as_shipping'):
        billing_address = shipping_address
        billing_city = shipping_city
        billing_state = shipping_state
        billing_zip = shipping_zip
        billing_country = shipping_country

    # Process the order and store the details (implementation needed)

    # Redirect to a confirmation page or handle further actions
    return redirect(url_for('order_confirmation'))




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
    
@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.user_firstname = request.form['firstname']
        user.user_lastname = request.form['lastname']
        user.email_address = request.form['email']
        user.mobile = request.form['mobile']
       
        
        
        db.session.commit()
        flash('User details updated successfully!', 'success')
        return redirect(url_for('user_details', user_id=user_id))
    
    return render_template('user_details.html', user=user)

@app.route('/change_password/<int:user_id>', methods=['GET', 'POST'])
def change_password(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Input validation
        if not new_password or not confirm_password:
            flash('All fields are required.', 'error')
            return redirect(url_for('change_password', user_id=user_id))
        
        # Check if new password and confirm password match
        if new_password != confirm_password:
            flash('New password and confirm password do not match.', 'error')
            return redirect(url_for('change_password', user_id=user_id))
        
        # Update the user's password hash directly in the database
        hashed_password = generate_password_hash(new_password)
        db.session.query(User).filter(User.user_id == user_id).update({User.password_hash: hashed_password})
        db.session.commit()  # Commit the changes to the database
        
        flash('Password updated successfully.', 'success')
        return redirect(url_for('change_password', user_id=user_id))
    
    return render_template('user_changepassword.html', user=user)


@app.route('/editmerchant/<int:company_id>', methods=['GET', 'POST'])
def edit_merchant(company_id):
    print("Company ID from URL:", company_id)
    try:
        # Find merchant user by company ID
        merchant_user = MerchantUser.query.get(company_id)
        if not merchant_user:
            return jsonify({'success': False, 'message': 'Merchant user not found.'}), 404
        
        if request.method == 'POST':
            # Get form data from request
            data = request.form

            print("Form Data:", data)
            # Validate required fields
            required_fields = ['firstname', 'lastname', 'company_name', 'company_emailaddress', 'company_address', 'company_mobile', 'company_postcode', 'company_registrationno']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'message': f'Missing or empty field: {field}'}), 400

            # Update merchant user details
            merchant_user.firstname = data['firstname']
            merchant_user.lastname = data['lastname']
            merchant_user.company_name = data['company_name']
            merchant_user.company_emailaddress = data['company_emailaddress']
            merchant_user.company_address = data['company_address']
            merchant_user.company_mobile = data['company_mobile']
            merchant_user.company_postcode = data['company_postcode']
            merchant_user.company_registrationno = data['company_registrationno']

            # Commit changes to the database
            db.session.commit()

            flash('Merchant details updated successfully!', 'success')
            # Redirect back to the edit page after successful update
            return redirect(url_for('edit_merchant', company_id=company_id))
        
        # Render the template with merchant details for GET request
        return render_template('merchant_user_details.html', merchant_user=merchant_user)

    except Exception as e:
        # Log error
        app.logger.error(f"Error occurred during merchant details update: {str(e)}")
        flash('An error occurred while updating merchant details.', 'error')
        return redirect(url_for('edit_merchant', company_id=company_id))


if __name__ == '__main__':
    app.run(debug=True)
