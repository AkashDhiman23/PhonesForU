
import os
import psycopg2
from flask import Flask, render_template, request,session, redirect, url_for, jsonify,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from model import ProductCategory, ProductList, db, User,MerchantUser

from datetime import datetime as dt

app = Flask(__name__, static_url_path='/static')

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:dhiman223@localhost:5432/ecommercedb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['STATIC_FOLDER'] = 'static'
migrate = Migrate(app, db)
db.init_app(app)
PRODUCT_PIC_UPLOAD_FOLDER = 'static/img/product_img/'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


app.config['SECRET_KEY'] = 'thisissecret'
app.config['PRODUCT_IMAGE_UPLOAD_FOLDER'] = 'static/img/product_images'


def save_file(file, upload_folder):
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        dt_now = dt.now().strftime("%Y%m%d%H%M%S%f")
        file_extension = get_file_extension(filename)
        filename_to_save = f"{dt_now}_{filename}"
        file_path = os.path.join(upload_folder, filename_to_save)
        file.save(file_path)
        return file_path
    return None
def allowed_file(filename):
   
    print("Here??")
    file_name_split = filename.rsplit('.', 1)
    print("Here too??")
    file_extension = file_name_split[1]
    print(file_extension)
    if file_extension in ALLOWED_EXTENSIONS:
        return True
    else:
        return False
    '''

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           '''

# function to get the file extension
def get_file_extension(filename):
    print("Here??")
    file_name_split = filename.rsplit('.', 1)
    print("Here too??")
    file_extension = file_name_split[1]
    print(file_extension)
    return file_extension


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
    session.pop('username', None)
    return render_template('admin.html')

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
        # Handle the POST request to add a new product
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

        main_image_path = save_file(product_main_image, app.config['PRODUCT_IMAGE_UPLOAD_FOLDER'])
        secondary_image1_path = save_file(product_secondary_image1, app.config['PRODUCT_IMAGE_UPLOAD_FOLDER']) if product_secondary_image1 else None
        secondary_image2_path = save_file(product_secondary_image2, app.config['PRODUCT_IMAGE_UPLOAD_FOLDER']) if product_secondary_image2 else None

        # Handle file upload for profile picture
        # ...

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
            return render_template('addnewproduct.html', category=category, error_message="An error occurred. Please try again.")
    else:
        return render_template('addnewproduct.html', product_category=category)

@app.route('/viewproducts/<int:category_id>')
def viewproducts(category_id):
    products = ProductList.query.filter_by(category_id=category_id).all()
    product_category = ProductCategory.query.get(category_id)  # Fetch the product category
    return render_template('viewproducts.html', products=products, product_category=product_category)


@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = ProductList.query.get(product_id)
    category_id = None  # Initialize category_id outside the if-else block
    if product:
        category_id = product.category_id
        product_category = ProductCategory.query.get(category_id)  # Fetch the product category
        if request.method == 'POST':
            # Logic to update the product based on the form data
            
            # Assuming the product has been successfully updated
            flash('Product updated successfully!', 'success')
            # Redirect to viewproducts route with category_id
            return redirect(url_for('viewproducts', category_id=category_id))
        else:
            return render_template('edit_product.html', product=product, product_category=product_category)
    else:
        flash('Product not found!', 'error')
        # Redirect to viewproducts route without specifying category_id
        return redirect(url_for('viewproducts'))

@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    product = ProductList.query.get(product_id)
    if product:
        # Update product details based on form data
        product.product_name = request.form['product_name']
        product.product_code = request.form['product_code']
        product.product_title = request.form['product_title']
        product.product_description = request.form['product_description']
        product.product_price = request.form['product_price']
        product.product_quantity = request.form['product_quantity']
        # Add more fields to update as needed
        
        db.session.commit()
        
        # Redirect to the viewproducts route with the correct category_id
        return redirect(url_for('viewproducts', category_id=product.category_id))
    else:
        flash('Product not found!', 'error')
        return redirect(url_for('viewproducts',category_id=product.category_id))  # Redirect to viewproducts without category_id




if __name__ == '__main__':
    app.run(debug=True)

