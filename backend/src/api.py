import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ----------------------------------
# ROUTES
# ----------------------------------
'''
GET Route handler for getting list of drinks
'''
@app.route('/drinks')
def get_drinks():
    # get all drinks
    drinks =  Drink.query.all()

    # 404 if no drinks found
    if len(drinks) == 0:
        abort(404)

    # format using .short()
    drinks_short = [drink.short() for drink in drinks]

    # return drinks
    return jsonify({
        # 'status_code': 200 TODO: CHECK
        'success': True,
        'drinks': drinks_short
    })

'''
GET Route handler for getting drink details
Requires the 'get:drinks-detail' permission
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    # get all drinks 
    drinks = Drink.query.all().long()
    
    # 404 if no drinks
    if len(drinks) == 0:
        abort(404)

    # format using .long()
    drinks_long = [drink.long() for drink in drinks]

    # return drinks
    return jsonify({
        'success': True,
        'drinks': drinks_long
    })

'''
POST Route handler for adding new drink
Requires the 'post:drinks' permission
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    # get drink info form request
    body = request.get_json()
    title = body['title']
    recipe = body['recipe']

    # create new drink
    drink = Drink(title=title, recipe=json.dumps(recipe)) #TODO: what is going on?? 

    try:
        # add drink to database
        drink.insert()
    except Exception as e:
        print('ERROR: ', str(e) )
        abort(422)

    return jsonify({
        'success': True,
        'drinks': drink.long()
    })

'''
PATCH Route handler for editing drink
Requires the 'patch:drinks' permission

'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(*args, **kwargs):
    # get ID from kwargs
    id = kwargs['id']

    # get drink by id
    drink = Drink.query.filter_by(id=id).one_or_none()

    # 404 if drink not found
    if drink is None:
        abort(404)

    # get request body and update title/recipe
    body = request.get_json()

    if 'title' in body:
        drink.title = body['title']
    
    if 'recipe' in body:
        drink.recipe = body['recipe']

    # update drink in db
    try:
        drink.insert()
    except Exception as e:
        print('EXCEPTION: ', str(e))
        abort(400)

    # array and return
    drink = [drink.long()]

    return jsonify({
        'success': True,
        'drinks': drink
    })

'''
DELETE Route handler for deleting drink
Requires the 'delete:drinks' permission
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(*args, **kwargs):
    # get id from kwargs
    id = kwargs['id']

    # get drink by id 
    drink = Drink.query.filter_by(id=id).one_or_none()

    # 404 if drink not found
    if drink is None:
        abort(404)
    
    # delete
    try: 
        drink.delete()
    except Exception as e:
        print('EXCEPTION: ', str(e))
        abort(500)

    return jsonify({
        'success': True,
        'delete': id
    })

# ----------------------------------
# Error Handling
# ----------------------------------
# Error handling for unprocessable entity

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

# Error handling for resource not found

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

# Error handling for bad request

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "bad request"
                    }), 400

# Error handling  for AuthError

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response 
