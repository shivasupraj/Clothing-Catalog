from models import Base, User, Category, Product
from flask import Flask, jsonify, request
from flask import url_for, abort, g
from flask import render_template, redirect, flash
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy import create_engine

from flask_httpauth import HTTPBasicAuth
import json

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

from flask import session as login_session
import random
import string

# import redis for caching and rate limiting
import redis

# import the helper functions
from helpers import checkUrl, checkPrice

auth = HTTPBasicAuth()

CLIENT_ID = json.loads(
    open(
        'client_secrets.json', 'r'
    ).read())['web']['client_id']

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
session = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

r = redis.StrictRedis(host='localhost', port=6379, db=0)
categories = session.query(Category).all()

# login routes


@app.route('/login')
def login():
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits
        ) for x in xrange(32))
    login_session['state'] = state
    return render_template(
        'login.html',
        STATE=state,
        login_session=login_session
    )


# connecting to the google server
@app.route('/gconnect', methods=['POST'])
def gconnect():
    print('gconnect')
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    print(code)
    try:
        # Exchange the one-time-access code for the credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'),
            401
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is a valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    print(result)

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the access token is for the intented user
    google_id = credentials.id_token['sub']
    if result['user_id'] != google_id:
        response = make_response(
                json.dumps('Token\'s userid does not match given user id'),
                401
            )
        response.headers['Content-Type'] = 'application/json'
        return response

    # check if the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
                json.dumps('Token\'s CLIENTID does not match '),
                401
            )
        response.headers['Content-Type'] = 'application/json'
        return response

    # check if the user is already logged in
    stored_credentials = login_session.get('access_token')
    stored_google_id = login_session.get('google_id')

    print(login_session.get('access_token'), login_session.get('google_id'))
    if stored_credentials is not None and google_id == stored_google_id:
        response = make_response(json.dumps('User is already logged In'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # store access token in the session for the later use
    login_session['access_token'] = credentials.access_token
    login_session['google_id'] = google_id

    # get user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    print(data)
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    items = session.query(Product).all()
    flash("you are now logged in as %s" % login_session['username'])
    return render_template(
        'index.html',
        categories=categories,
        items=items,
        login_session=login_session
    )


@app.route('/gdisconnect')
def gdisconnect():
    print('gdisconnect')
    print(login_session)
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = """https://accounts.google.com/o/oauth2/revoke?token=%s""" % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset user's session
        del login_session['access_token']
        del login_session['google_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        flash('succefully disconnected')
        return redirect(url_for('index'))
    else:
        # if the token in invalid
        respose = make_response(
                json.dumps(
                    'Failed to revoke token for the given user'
                    ), 400)
        respose.headers['Content-Type'] = 'application/json'
        return respose


@app.route('/')
@app.route('/catalog')
def index():
    """
    Displays the home page of the app sorted by the latest added elements.
    """
    r.ltrim('newlyAddedProductsToCatalog', 0, 5)
    items_str = r.lrange('newlyAddedProductsToCatalog', 0, -1)
    items = []
    for item_str in items_str:
        items.append(json.loads(item_str))

    # items = session.query(Product).all()
    flash('Newly added items to the catalog')
    return render_template(
        'index.html',
        categories=categories,
        items=items,
        login_session=login_session
    )


@app.route('/catalog/<string:category>/items')
def showItemsOfCategory(category):
    if category.lower() == 'recent':
        return redirect(url_for('index'))
    category_obj = session.query(Category).filter_by(name=category).first()
    items = session.query(Product).filter_by(category_id=category_obj.id)
    return render_template(
        'displayItems.html',
        category=category,
        categories=categories,
        items=items,
        login_session=login_session
    )


@app.route('/catalog/<string:category>/items/<int:item_id>')
def displayItemOfCategory(category, item_id):
    item = session.query(Product).filter_by(id=item_id).first()
    print(login_session['user_id'], item.user_id)
    return render_template(
            'displayItemDetails.html',
            category=category,
            categories=categories,
            item=item,
            login_session=login_session
        )


@app.route('/catalog/items/add', methods=['GET', 'POST'])
def addItemToCategory():
    if 'username' not in login_session:
        flash('Please login to add a product to the catalog')
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template(
                    'addItemToCategory.html',
                    categories=categories,
                    login_session=login_session
                )
    else:
        user = getUserInfo(login_session['user_id'])
        category = request.form['category']
        category_obj = session.query(
                    Category
                ).filter_by(name=category).first()

        # Checks if an user exists or not
        if category_obj is None:
            flash('No category available for the provided value')
            return redirect(
                        url_for('showItemsOfCategory', category=category)
                    )

        # Checks if the given url is an active url or not
        if not checkUrl(request.form['image_url']):
            flash('Invalid url given as an input')
            return redirect(
                        url_for('showItemsOfCategory', category=category)
                    )

        # Checks if the user entered right floating point value
        if not checkPrice(request.form['price']):
            flash('Enter a valid price value with decimal values')
            return redirect(
                        url_for('showItemsOfCategory', category=category)
                    )

        item = Product(
            name=request.form['name'],
            description=request.form['description'],
            picture=request.form['image_url'],
            price=request.form['price'],
            category=category_obj,
            user=user
        )
        session.add(item)
        session.flush()
        session.refresh(item)

        # adds new element to the redis cache
        item_dict = item.serialize
        item_dict['category'] = category
        item_json = json.dumps(item_dict)
        r.lpush('newlyAddedProductsToCatalog', item_json)

        session.commit()

        flash('Successfully added the product to catalog - %s' % category)
        return redirect(url_for('showItemsOfCategory', category=category))


@app.route(
            '/catalog/<string:category>/items/<int:item_id>/edit',
            methods=['GET', 'POST']
        )
def editItemOfCategory(category, item_id):
    if 'username' not in login_session:
        flash('Please login to continue to edit the product')
        return redirect(url_for('index'))
    if request.method == 'GET':
        item = session.query(Product).filter_by(id=item_id).first()
        if item is None:
            flash('Cannot find the product entered')
            return redirect(
                        url_for('displayItemOfCategory', category=category)
                    )
        if item.user_id != login_session['user_id']:
            flash('you don\'t have the permission to edit the product')
        return render_template(
                    'editItemDisplay.html',
                    category=category,
                    categories=categories,
                    item=item,
                    login_session=login_session
                )
    else:
        user = getUserInfo(login_session['user_id'])
        category_obj = session.query(
                Category
            ).filter_by(name=category).first()

        # Checks if an user exists or not
        if category_obj is None:
            flash('No category available for the provided value')
            return redirect(url_for('showItemsOfCategory', category=category))

        # Checks if the given url is an active url or not
        if not checkUrl(request.form['image_url']):
            flash('Invalid url given as an input')
            return redirect(
                    url_for('showItemsOfCategory', category=category)
                )

        # Checks if the user entered right floating point value
        if not checkPrice(request.form['price']):
            flash('Enter a valid price value with decimal values')
            return redirect(
                        url_for('showItemsOfCategory', category=category)
                    )

        item = session.query(Product).filter_by(id=item_id).first()

        # Checks if the product/item is available
        if item is None:
            flash('Cannot find the product')
            return redirect(
                    url_for('showItemsOfCategory', category=category)
                )

        item.name = request.form['name']
        item.description = request.form['description']
        item.picture = request.form['image_url']
        item.price = request.form['price']
        item.category = category_obj
        item.user = user

        session.add(item)
        session.commit()

        flash('Successfully updated the product to catalog - %s' % category)
        return redirect(url_for('showItemsOfCategory', category=category))


@app.route(
        '/catalog/<string:category>/items/<int:item_id>/delete',
        methods=['GET', 'POST']
    )
def deleteItemOfCategory(category, item_id):
    if 'username' not in login_session:
        flash('Please login to continue to delete the product')
        return redirect(url_for('index'))
    if request.method == 'GET':
        item = session.query(Product).filter_by(id=item_id).first()

        if item is None:
            flash('Cannot find the product entered')
            return redirect(
                    url_for('displayItemOfCategory', category=category)
                )
        return render_template(
                    'deleteItemOfCategory.html',
                    category=category,
                    categories=categories,
                    item=item,
                    login_session=login_session
                )
    else:
        user = getUserInfo(login_session['user_id'])
        category_obj = session.query(Category).filter_by(name=category).first()

        # Checks if an user exists or not
        if category_obj is None:
            flash('No category available for the provided value')
            return redirect(url_for('showItemsOfCategory', category=category))

        item = session.query(Product).filter_by(id=item_id).first()

        if item is None:
            flash('Cannot find the product entered')
            return redirect(
                url_for(
                    'displayItemOfCategory',
                    category=category
                    )
                )

        # Check if the user is authorized to delete the product
        if user.id != item.user_id:
            flash('Cannot perform the operation - delete')
            return redirect(
                url_for(
                    'displayItemOfCategory',
                    category=category
                    )
                )
        session.delete(item)
        session.commit()
        flash('Succesfully deleted the product')
        return redirect(url_for('showItemsOfCategory', category=category))


# Return a collection of items in a category
# in JSON format.
@app.route('/json/catalog/<string:category>')
def showProdcutsOfCatalogInJSON(category):
    category_obj = session.query(Category).filter_by(name=category).first()
    if category_obj:
        category_id = category_obj.id
        items = session.query(Product).filter_by(category_id=category_id)
        return jsonify(catalog=[i.serialize for i in items])
    else:
        return jsonify(error='No data found')

# Returns information about a specific item in an category
# in JSON format


@app.route('/json/catalog/<string:category>/items/<int:item_id>')
def showItemDetailsJSON(category, item_id):
    item = session.query(Product).filter_by(id=item_id).first()
    if item:
        return jsonify(prodcut=item.serialize)
    else:
        return jsonify(error='No data found')

# Helper functions to create and mange users


def createUser(login_session):
    new_user = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
    )
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


if __name__ == '__main__':
    app.debug = True
    app.config['SECRET_KEY'] = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits
            ) for x in xrange(32)
        )
    app.run(host='0.0.0.0', port=5000)
