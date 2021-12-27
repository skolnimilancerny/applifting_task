import uuid
from functools import wraps
from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Products, Offers, Users
from app import app, db, URL, headers
import datetime
import time
import threading
import requests
import jwt


# EVERY 60s UPDATES OFFERS FROM OFFERS MS
def update_offers_db():
    """
    Checks for all product ids in database and then updates offers for each product from Offers MS.
    After committing changes to database sleeps for 60s and runs again.
    :return: None
    """
    while True:
        product_ids = [row.id for row in Products.query.all()]
        for product_id in product_ids:
            Offers.query.filter_by(product_id=product_id).delete()
            offers = requests.get(f"{URL}/products/{product_id}/offers", headers=headers).json()
            for offer in offers:
                new_offer = Offers(id=offer['id'], price=offer['price'],
                                   items_in_stock=offer['items_in_stock'], product_id=product_id)
                db.session.add(new_offer)
            db.session.commit()
            print(f"Updated offers for product id: {product_id}")
        time.sleep(60)


# STARTS BACKGROUND JOB TO GET NEW OFFERS FROM OFFERS MS
@app.before_first_request
def start_job():
    thread = threading.Thread(target=update_offers_db)
    thread.start()


# WRAPPER CHECKS FOR VALID JWT
def token_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
        if not token:
            return jsonify(success=False, error='No token provided'), 401
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify(success=False, error='Invalid token'), 401
        return f(*args, **kwargs)
    return wrapped


# CREATE A NEW USER
@app.route('/register', methods=['POST'])
def register():
    username = request.args.get('username')
    hashed_password = generate_password_hash(request.args.get('password'), method='sha256')
    new_user = Users(public_id=str(uuid.uuid4()), username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(success=True, message=f'Welcome {username}! Your account has been created.'), 201


# DELETE EXISTING USER
@app.route('/users/delete', methods=['DELETE'])
@token_required
def delete_key():
    public_id = request.args.get('id')
    user_to_delete = Users.query.filter(Users.public_id == public_id).first()
    if user_to_delete and public_id:
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify(success=True, message=f'User {user_to_delete.username} has been deleted.'), 200
    return jsonify(success=False, message='No user with that ID.'), 200


# SHOW ALL USERS IN DB
@app.route('/users/all')
@token_required
def get_all_users():
    all_users = Users.query.all()
    users = [user.to_dict() for user in all_users]
    if users:
        return jsonify(success=True, all_users=users), 200
    else:
        return jsonify(success=True, message="No users to show."), 200


# LOGIN WITH EXISTING CREDENTIALS
@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Verification failed', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

    user = Users.query.filter(Users.username == auth.username).first()
    if check_password_hash(user.password, auth.get('password')):
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            app.config['SECRET_KEY'], "HS256")
        return jsonify({'token': token}), 200

    return make_response('Verification failed', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})


#  CREATE A NEW PRODUCT
@app.route('/products/create', methods=['POST'])
@token_required
def create_product():
    """
    Checks fot all required args and optional id. Then creates a new product with these args.
    This new product is then registered in Offers MS.
    :return: None
    """
    name = request.args.get('name')
    description = request.args.get('description')
    optional_id = request.args.get('id')
    product_ids = [value.id for value in Products.query.all()]
    if name is not None and description is not None:
        if optional_id:
            if optional_id not in product_ids:
                product_to_add = Products(id=int(optional_id), name=name, description=description)
            else:
                return jsonify(success=False, error="Product id already exists")
        else:
            product_to_add = Products(name=name, description=description)

        db.session.add(product_to_add)
        db.session.commit()
        params = {"id": product_to_add.id,
                  "name": product_to_add.name,
                  "description": product_to_add.description
                  }
        requests.post(f"{URL}/products/register", headers=headers, params=params)
        return jsonify(success=True, message=f"{name} was added to Products.", product_id=product_to_add.id), 201
    else:
        return jsonify(success=False, error="Please provide all arguments."), 400


# READ ALL PRODUCTS
@app.route('/products/all')
@token_required
def get_all_products():
    all_products = Products.query.all()
    products = [product.to_dict() for product in all_products]
    if products:
        return jsonify(success=True, all_products=products), 200
    else:
        return jsonify(success=True, message="No products to show."), 200


# READ PRODUCT BY ID
@app.route('/products/get')
@token_required
def get_product():
    product_id = request.args.get('id')
    product = Products.query.get(product_id)
    if product:
        return jsonify(success=True, product=product.to_dict()), 200
    elif product_id is None:
        return jsonify(success=False, error="Please provide a Product ID."), 400
    else:
        return jsonify(success=False, error="Invalid product ID."), 400


# SEARCH FOR PRODUCT BY NAME
@app.route('/products/search')
@token_required
def search_product():
    name = request.args.get('name')
    products_found = Products.query.filter(Products.name == name).all()
    if products_found:
        products = [product.to_dict() for product in products_found]
        return jsonify(success=True, found_products=products), 200
    elif name is None:
        return jsonify(success=False, error="Please provide a name to search."), 400
    else:
        return jsonify(success=False, error="No products match this name"), 400


# UPDATE A PRODUCT NAME AND DESCRIPTION
@app.route('/products/update', methods=['PUT'])
@token_required
def update_product():
    product_id = request.args.get('id')
    name = request.args.get('name')
    description = request.args.get('description')
    product_to_update = Products.query.get(product_id)

    if product_id is None or name is None or description is None or product_id is None:
        return jsonify(success=False, error="Please provide all arguments."), 400
    elif product_to_update is None:
        return jsonify(success=False, error="Invalid product ID."), 400
    else:
        product_to_update.name = name
        product_to_update.description = description
        db.session.commit()
        return jsonify(success=True, message="Product updated"), 200


# DELETE A PRODUCT AND ITS OFFERS
@app.route('/products/delete', methods=['DELETE'])
@token_required
def delete_product():
    product_id = request.args.get('id')
    product_to_delete = Products.query.get(product_id)
    if product_to_delete:
        Offers.query.filter_by(product_id=product_id).delete()
        db.session.delete(product_to_delete)
        db.session.commit()
        return jsonify(success=True, message=f"{product_to_delete.name} was deleted."), 200
    elif product_id is None:
        return jsonify(success=False, error="Please provide a Product ID."), 400
    else:
        return jsonify(success=False, error="Invalid product ID."), 400


# VIEW ALL PRODUCT OFFERS FROM OFFERS MS
@app.route('/products/offers')
@token_required
def get_offers():
    product_id = request.args.get('id')
    product = Products.query.get(product_id)
    product_offers = Offers.query.filter(Offers.product_id == product_id).all()
    if product:
        offers_json = [offer.to_dict() for offer in product_offers]
        return jsonify(success=True, offers=offers_json, product_name=product.name), 200
    elif not product_id:
        return jsonify(success=False, error="Please provide a Product ID."), 400
    else:
        return jsonify(success=False, error="Invalid product ID."), 400
