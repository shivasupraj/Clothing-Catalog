from models import Base, User
from flask import Flask, jsonify, request, url_for, abort, g, render_template
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

auth = HTTPBasicAuth()


engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
session = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

#Fake data
categories = [{ 'id' : 1, 'name' : 'shirts', 'user_id' : '1' }, { 'id' : 2, 'name' : 'jeans', 'user_id' : '1' } , { 'id' : 3, 'name' : 'bags', 'user_id' : '1' }]
category = { 'id' : 1, 'name' : 'shirts', 'user_id' : '1' }

items = [ { 'id' : 1, 'name' : 'cherokee shirt', 'description' : 'A very good shirt', 'picture' : 'link to shirt', 'category_id' : 1, 'user_id' : 1 }, 
          { 'id' : 1, 'name' : 'cherokee shirt', 'description' : 'A very good shirt', 'picture' : 'link to shirt', 'category_id' : 1, 'user_id' : 1 },
          { 'id' : 1, 'name' : 'cherokee shirt', 'description' : 'A very good shirt', 'picture' : 'link to shirt', 'category_id' : 2, 'user_id' : 1 },
          { 'id' : 1, 'name' : 'cherokee shirt', 'description' : 'A very good shirt', 'picture' : 'link to shirt', 'category_id' : 3, 'user_id' : 1 }
]
item = { 'id' : 1, 'name' : 'cherokee shirt', 'description' : 'A very good shirt', 'picture' : 'link to shirt', 'category_id' : 1, 'user_id' : 1 }


@app.route('/')
@app.route('/catalog')
def index():
    """
    Displays the home page of the app sorted by the latest added elements.
    """
    return render_template('index.html', categories = categories, items = items)

@app.route('/catalog/<string:category>/items')
def showItemsOfCategory(category):
    return render_template('displayItems.html', category = category, categories = categories, items = items)

@app.route('/catalog/<string:category>/items/<int:item_id>')
def displayItemOfCategory(category, item_id):
    return render_template('displayItemDetails.html', category = category, categories = categories, item = item)

@app.route('/catalog/<string:category>/items/add')
def addItemToCategory(category):
    return render_template('addItemToCategory.html', categories = categories)

@app.route('/catalog/<string:category>/items/<int:item_id>/edit')
def editItemOfCategory(category, item_id):
    return render_template('editItemDisplay.html', category = category, categories = categories, item = item)

@app.route('/catalog/<string:category>/items/<int:item_id>/delete')
def deleteItemOfCategory(category, item_id):
    return render_template('deleteItemOfCategory.html', category = category, categories = categories, item = item)





if __name__ == '__main__':
    app.debug = True
    #app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(host='0.0.0.0', port=5000)