import requests
import random
from requests.auth import HTTPBasicAuth

# ENDPOINT = 'https://apiapplifting.herokuapp.com'
ENDPOINT = 'http://10.0.0.18:5000'

ID = random.randint(100000, 1000000)

PARAMS = {
        'id': ID,
        'name': 'TEST',
        'description': 'TESTING DESC'
    }


def test_register():
    data = {
        'username': 'username',
        'password': 'password',
        'public_id': '1'
    }
    response = requests.post(f'{ENDPOINT}/register', params=data)
    assert response.status_code == 201


def test_create_product():
    response = requests.post(f'{ENDPOINT}/products/create')
    assert response.status_code == 401

    headers = {
        'x-access-tokens': requests.get(f'{ENDPOINT}/login', auth=HTTPBasicAuth('username', 'password')).json()['token']
    }

    response = requests.post(f'{ENDPOINT}/products/create', headers=headers)
    expected_json = {'error': 'Please provide all arguments.', 'success': False}
    assert response.status_code == 400
    assert expected_json == response.json()

    response = requests.post(f'{ENDPOINT}/products/create', params=PARAMS, headers=headers)
    expected_json = {'message': 'TEST was added to Products.', 'product_id': ID, 'success': True}
    assert response.status_code == 201
    assert expected_json == response.json()


def test_get_all_products():
    response = requests.get(f'{ENDPOINT}/products/all')
    assert response.status_code == 401

    headers = {
        'x-access-tokens': requests.get(f'{ENDPOINT}/login', auth=HTTPBasicAuth('username', 'password')).json()['token']
    }

    response = requests.get(f'{ENDPOINT}/products/all', headers=headers)
    assert response.status_code == 200


def test_get_product():
    headers = {
        'x-access-tokens': requests.get(f'{ENDPOINT}/login', auth=HTTPBasicAuth('username', 'password')).json()['token']
    }

    response = requests.get(f'{ENDPOINT}/products/get', headers=headers)
    expected_json = {'error': 'Please provide a Product ID.', 'success': False}
    assert response.status_code == 400
    assert expected_json == response.json()

    response = requests.get(f'{ENDPOINT}/products/get?id=idecko', headers=headers)
    expected_json = {'error': 'Invalid product ID.', 'success': False}
    assert response.status_code == 400
    assert expected_json == response.json()

    response = requests.get(f'{ENDPOINT}/products/get?id={ID}')
    assert response.status_code == 401

    response = requests.get(f'{ENDPOINT}/products/get?id={ID}', headers=headers)
    expected_json = {
        "product": PARAMS,
        "success": True}
    assert response.status_code == 200
    assert expected_json == response.json()


def test_search_product():
    headers = {
        'x-access-tokens': requests.get(f'{ENDPOINT}/login', auth=HTTPBasicAuth('username', 'password')).json()['token']
    }

    response = requests.get(f'{ENDPOINT}/products/search', headers=headers)
    expected_json = {'error': 'Please provide a name to search.', 'success': False}
    assert response.status_code == 400
    assert expected_json == response.json()

    response = requests.get(f'{ENDPOINT}/products/search?name=jmenocotamneni', headers=headers)
    expected_json = {'error': 'No products match this name', 'success': False}
    assert response.status_code == 400
    assert expected_json == response.json()

    response = requests.get(f'{ENDPOINT}/products/search?name={PARAMS["name"]}')
    assert response.status_code == 401

    response = requests.get(f'{ENDPOINT}/products/search?name={PARAMS["name"]}', headers=headers)
    expected_json = {"found_products": [PARAMS], "success": True}
    assert response.status_code == 200
    assert expected_json == response.json()


def test_get_offers():
    headers = {
        'x-access-tokens': requests.get(f'{ENDPOINT}/login', auth=HTTPBasicAuth('username', 'password')).json()['token']
    }

    response = requests.get(f'{ENDPOINT}/products/offers', headers=headers)
    expected_json = {'error': 'Please provide a Product ID.', 'success': False}
    assert response.status_code == 400
    assert expected_json == response.json()

    response = requests.get(f'{ENDPOINT}/products/offers?id={ID}')
    assert response.status_code == 401

    response = requests.get(f'{ENDPOINT}/products/offers?id={ID}', headers=headers)
    assert response.status_code == 200


def test_update_product():
    headers = {
        'x-access-tokens': requests.get(f'{ENDPOINT}/login', auth=HTTPBasicAuth('username', 'password')).json()['token']
    }

    response = requests.put(f'{ENDPOINT}/products/update', headers=headers)
    expected_json = {'error': 'Please provide all arguments.', 'success': False}
    assert response.status_code == 400
    assert expected_json == response.json()

    params = {
        'id': ID,
        'name': 'NEW TEST',
        'description': 'NEW TESTING DESC'
    }
    response = requests.put(f'{ENDPOINT}/products/update', params=params)
    assert response.status_code == 401

    response = requests.put(f'{ENDPOINT}/products/update', params=params, headers=headers)
    expected_json = {'message': 'Product updated', 'success': True}
    assert response.status_code == 200
    assert expected_json == response.json()


def test_delete_product():
    headers = {
        'x-access-tokens': requests.get(f'{ENDPOINT}/login', auth=HTTPBasicAuth('username', 'password')).json()['token']
    }

    response = requests.delete(f'{ENDPOINT}/products/delete', headers=headers)
    expected_json = {'error': 'Please provide a Product ID.', 'success': False}
    assert response.status_code == 400
    assert expected_json == response.json()

    response = requests.delete(f'{ENDPOINT}/products/delete?id={ID}')
    assert response.status_code == 401

    response = requests.delete(f'{ENDPOINT}/products/delete?id={ID}', headers=headers)
    expected_json = {'message': 'NEW TEST was deleted.', 'success': True}
    assert response.status_code == 200
    assert expected_json == response.json()


def test_delete_user():
    headers = {
        'x-access-tokens': requests.get(f'{ENDPOINT}/login', auth=HTTPBasicAuth('username', 'password')).json()['token']
    }

    response = requests.delete(f'{ENDPOINT}/users/delete')
    assert response.status_code == 401

    response = requests.delete(f'{ENDPOINT}/users/delete?id=1', headers=headers)
    assert response.status_code == 200
