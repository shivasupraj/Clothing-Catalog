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
categories = [[1, 'shirts', '1'], [2, 'jeans', 1], [3, 'bags', 1]]
category = [1, 'shirts', 1]

items = [[1, 'cherokee shirt', 'A very good shirt', 'link to shirt', 1, 1], [1, 'cherokee shirt', 'A very good shirt', 'link to shirt', 1, 1], [1, 'cherokee shirt', 'A very good shirt', 'link to shirt', 1, 1]]
item = [1, 'cherokee shirt', 'A very good shirt', 'link to shirt', 1, 1]

@app.route('/')
@app.route('/catalog')
def index():
    return 'Welcome to main page'

@app.route('/catalog/<string:category>/items')
def showItemsOfCategory(category):
    return 'received showItemsOfCategory %s' % category

@app.route('/catalog/<string:category>/items/<int:item_id>')
def displayItemOfCategory(category, item_id):
    return 'displayItemOfCategory {} {}'.format(category, item_id)

@app.route('/catalog/<string:category>/items/add')
def addItemToCategory(category):
    return 'received addItemToCategory %s' % category

@app.route('/catalog/<string:category>/items/<int:item_id>/edit')
def editItemOfCategory(category, item_id):
    return 'received editItemOfCategory {} {}'.format(category, item_id) 

@app.route('/catalog/<string:category>/items/<int:item_id>/delete')
def deleteItemOfCategory(category, item_id):
    return 'deleteItemOfCategory {} {}'.format(category, item_id)

@app.route('/catalog/<string:category>/items/<int:item_id>/update')
def updateItemOfCategory(category, item_id):
    return 'updateItemOfCategory {} {}'.format(category, item_id)




if __name__ == '__main__':
    app.debug = True
    #app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(host='0.0.0.0', port=5000)