## Getting Started

### Dependencies

* all dependencies listed in requirements.txt

### To start the api either:

* visit https://appliftingflask.herokuapp.com/register and register, then visit /login to get your JWT token
* build image from Dockerfile and run locally
* install all dependencies and run from terminal or IDE

### Environment variables

For running locally you need to specify 2 environment variables:
* OFFERS_URL - Endpoint of the Offers MS.
* ACCESS_TOKEN - Access token for the Offers MS.

There is also a PORT environment variable, which is used by Heroku and defaults to 5000.

# Routes

Here is a list of all the routes with their functions and methods.

### /register - POST

You need to register on this route to be able to login later.

Arguments:
* username (REQUIRED) - Your username.
* password (REQUIRED) - Your password.

### /login - GET

If you succesfully login with HTTP Authenticate, it returns a token you need to INCLUDE IN HEADERS (x-access-tokens) WITH ALL OTHER API CALLS.

### /users/all - GET

Retuns all registered users.

### /users/delete - DELETE

Deletes a user by his public id.

Arguments:
* id (REQUIRED) - Your user public id.

### /products/create - POST

Creates a new product with specified arguments, adds in into database and registers it in Offers MS.

Arguments:
* name (REQUIRED) - Product name of your choice.
* description (REQUIRED) - Short description of your product.
* id (OPTIONAL) - Here you can specify an id for your product, if left empty, it will be generated for you.

### /products/all - GET

Returns all the products from the database.

### /products/get - GET

Returns 1 specific product by its id.

Arguments:
* id (REQUIRED) - The id of the product you want to get.

### /products/search - GET

Returns product if its name matches your search. If multiple products match the name, returns them all.

Arguments:
* name (REQUIRED) - The name of the product you want to search for.

### /products/update - PUT

Updates existing product with a new name and description.

Arguments:
* id (REQUIRED) - Id of the product you want to update.
* name (REQUIRED) - New product name of your choice.
* description (REQUIRED) - New description of your product.


### /products/offers - GET

Shows all available offers from Offers MS for specified product. Refreshes every 60s.

Arguments:
* id (REQUIRED) - Id of the product you want to see offers for.

### /products/delete - DELETE

Deletes specified product and its offers from the database.

Arguments:
* id (REQUIRED) - Id of the product you want to delete.

### /delete_key - DELETE

Deletes api_key you provide with your headers.

## Testing

You can use the provided tests and run them with:
```
pytest tests.py
```

Feel free to change the tests file.

## Author

Milan Černý
