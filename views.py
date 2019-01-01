from models import Base, User, Category, Product
from flask import Flask, jsonify, request, url_for, abort, g, render_template, redirect, flash
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

from helpers import check_url, check_price
import random, string

auth = HTTPBasicAuth()


engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
session = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

#Fake data
# categories = [{ 'id' : 1, 'name' : 'shirts', 'user_id' : '1' }, { 'id' : 2, 'name' : 'jeans', 'user_id' : '1' } , { 'id' : 3, 'name' : 'bags', 'user_id' : '1' }]
# category = { 'id' : 1, 'name' : 'shirts', 'user_id' : '1' }

# items = [ { 'id' : 1, 'name' : 'cherokee shirt', 'description' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet. Praesent eleifend laoreet pulvinar.', 'price' : 12, 'picture' : 'https://s7d5.scene7.com/is/image/ColumbiaSportswear2/1617431_073_f?$MHW_grid$&align=0,1', 'category_id' : 1, 'user_id' : 1 }, 
#           { 'id' : 1, 'name' : 'cherokee shirt', 'description' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet. Praesent eleifend laoreet pulvinar.', 'price' : 12, 'picture' : 'https://s7d5.scene7.com/is/image/ColumbiaSportswear2/1617431_073_f?$MHW_grid$&align=0,1', 'category_id' : 1, 'user_id' : 1 },
#           { 'id' : 1, 'name' : 'cherokee shirt', 'description' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet. Praesent eleifend laoreet pulvinar.', 'price' : 12, 'picture' : 'https://s7d5.scene7.com/is/image/ColumbiaSportswear2/1617431_073_f?$MHW_grid$&align=0,1', 'category_id' : 2, 'user_id' : 1 },
#           { 'id' : 1, 'name' : 'cherokee shirt', 'description' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet. Praesent eleifend laoreet pulvinar.', 'price' : 12, 'picture' : 'https://s7d5.scene7.com/is/image/ColumbiaSportswear2/1617431_073_f?$MHW_grid$&align=0,1', 'category_id' : 1, 'user_id' : 1 }, 
#           { 'id' : 1, 'name' : 'cherokee shirt', 'description' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet. Praesent eleifend laoreet pulvinar.', 'price' : 12, 'picture' : 'https://s7d5.scene7.com/is/image/ColumbiaSportswear2/1617431_073_f?$MHW_grid$&align=0,1', 'category_id' : 1, 'user_id' : 1 },
#           { 'id' : 1, 'name' : 'cherokee shirt', 'description' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet. Praesent eleifend laoreet pulvinar.', 'price' : 12, 'picture' : 'https://s7d5.scene7.com/is/image/ColumbiaSportswear2/1617431_073_f?$MHW_grid$&align=0,1', 'category_id' : 2, 'user_id' : 1 },
#           { 'id' : 1, 'name' : 'cherokee shirt', 'description' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet. Praesent eleifend laoreet pulvinar.', 'price' : 12, 'picture' : 'https://s7d5.scene7.com/is/image/ColumbiaSportswear2/1617431_073_f?$MHW_grid$&align=0,1', 'category_id' : 3, 'user_id' : 1 }
# ]
# item = { 'id' : 1, 'name' : 'cherokee shirt', 'description' : 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet. Praesent eleifend laoreet pulvinar.', 'price' : 12, 'picture' : 'https://s7d5.scene7.com/is/image/ColumbiaSportswear2/1617431_073_f?$MHW_grid$&align=0,1', 'category_id' : 3, 'user_id' : 1 }

categories = session.query(Category).all()
@app.route('/')
@app.route('/catalog')
def index():
    """
    Displays the home page of the app sorted by the latest added elements.
    """
    items = session.query(Product).all()
    return render_template('index.html', categories = categories, items = items)

@app.route('/catalog/<string:category>/items')
def showItemsOfCategory(category):
    category_obj = session.query(Category).filter_by(name = category).first()
    items = session.query(Product).filter_by(category_id = category_obj.id)
    return render_template('displayItems.html', category = category, categories = categories, items = items)

@app.route('/catalog/<string:category>/items/<int:item_id>')
def displayItemOfCategory(category, item_id):
    item = session.query(Product).filter_by(id = item_id).first()
    return render_template('displayItemDetails.html', category = category, categories = categories, item = item)

@app.route('/catalog/<string:category>/items/add', methods = ['GET', 'POST'])
def addItemToCategory(category):
    if request.method == 'GET':
        return render_template('addItemToCategory.html', category = category, categories = categories)
    else:
        user = session.query(User).all()[0]
        category_obj = session.query(Category).filter_by(name = category).first()

        # Checks if an user exists or not
        if category_obj is None:
            flash('No category available for the provided value')
            return redirect(url_for('showItemsOfCategory', category = category))
        
        # Checks if the given url is an active url or not
        if not check_url(request.form['image_url']):
            flash('Invalid url given as an input')
            return redirect(url_for('showItemsOfCategory', category = category))
        
        #Checks if the user entered right floating point value
        if not check_price(request.form['price']):
            flash('Enter a valid price value with decimal values')
            return redirect(url_for('showItemsOfCategory', category = category))

        item = Product(
            name = request.form['name'],
            description = request.form['description'],
            picture = request.form['image_url'],
            price = request.form['price'],
            category = category_obj,
            user = user
        )

        session.add(item)
        session.commit()
        flash('Successfully added the product to catalog - %s' % category)
        return redirect(url_for('showItemsOfCategory', category = category))

@app.route('/catalog/<string:category>/items/<int:item_id>/edit', methods = ['GET', 'POST'])
def editItemOfCategory(category, item_id):
    if request.method == 'GET':
        item = session.query(Product).filter_by(id = item_id).first()
        if item is None:
            flash('Cannot find the product entered')
            return redirect(url_for('displayItemOfCategory', category = category))
        return render_template('editItemDisplay.html', category = category, categories = categories, item = item)
    else:
        user = session.query(User).all()[0]
        category_obj = session.query(Category).filter_by(name = category).first()

        # Checks if an user exists or not
        if category_obj is None:
            flash('No category available for the provided value')
            return redirect(url_for('showItemsOfCategory', category = category))
        
        # Checks if the given url is an active url or not
        if not check_url(request.form['image_url']):
            flash('Invalid url given as an input')
            return redirect(url_for('showItemsOfCategory', category = category))
        
        #Checks if the user entered right floating point value
        if not check_price(request.form['price']):
            flash('Enter a valid price value with decimal values')
            return redirect(url_for('showItemsOfCategory', category = category))
        
        item = session.query(Product).filter_by(id = item_id).first()

        #Checks if the product/item is available
        if item is None:
            flash('Cannot find the product')
            return redirect(url_for('showItemsOfCategory', category = category))

        item.name = request.form['name']
        item.description = request.form['description']
        item.picture = request.form['image_url']
        item.price = request.form['price']
        item.category = category_obj
        item.user = user
        

        session.add(item)
        session.commit()

        flash('Successfully updated the product to catalog - %s' % category)
        return redirect(url_for('showItemsOfCategory', category = category))
        

@app.route('/catalog/<string:category>/items/<int:item_id>/delete')
def deleteItemOfCategory(category, item_id):
    return render_template('deleteItemOfCategory.html', category = category, categories = categories, item = item)





if __name__ == '__main__':
    app.debug = True
    app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(host='0.0.0.0', port=5000)