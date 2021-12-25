from flask import request, jsonify
from app.models import Products, Offers, Keys
from app import app, db, URL, headers
import time
import threading
import requests
import secrets


# EVERY 60s UPDATES OFFERS FROM OFFERS MS
def update_offers_db():
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


# CHECK IF PROVIDED API KEY IS IN DATABASE
@app.before_request
def check_api_key():
    all_keys = [value.api_key for value in Keys.query.all()]
    api_key = request.headers.get('api_key')
    if api_key in all_keys or request.path == '/register':
        pass
    else:
        return jsonify(success=False, error="Unauthorized"), 401


# GET AN API KEY
@app.route('/register')
def register():
    api_key = secrets.token_urlsafe(16)
    db.session.add(Keys(api_key=api_key))
    db.session.commit()
    return jsonify(success=True, api_key=api_key)


# DELETE EXISTING API KEY
@app.route('/delete_key', methods=['DELETE'])
def delete_key():
    api_key = request.headers.get('api_key')
    key_in_db = Keys.query.filter(Keys.api_key == api_key).first()
    if key_in_db and api_key:
        db.session.delete(key_in_db)
        db.session.commit()
        return jsonify(success=True, message='Key has been deleted'), 200


#  CREATE A NEW PRODUCT
@app.route('/products/create', methods=['POST'])
def create_product():
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
def get_all_products():
    all_products = Products.query.all()
    products = [product.to_dict() for product in all_products]
    if products:
        return jsonify(success=True, all_products=products), 200
    else:
        return jsonify(success=True, message="No products to show."), 200


# READ PRODUCT BY ID
@app.route('/products/get')
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
