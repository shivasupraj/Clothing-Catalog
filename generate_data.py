from models import Base, User, Category, Product
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy import create_engine

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
session = scoped_session(sessionmaker(bind=engine))

# Create dummy user
user = User(
    name='Rob king',
    email='robking@email.com',
    picture=(
        "https://encrypted-tbn0.gstatic.com/"
        "images?q=tbn:ANd9GcTfobIEm2kfH0xPgbhF6j4MWtQGMOFbpprh3cxulpxknBJ-x2TV"
    ))
session.add(user)
session.commit()

# Create Categories
rec = Category(name='Recent', user_id=user.id)
session.add(rec)
session.commit()

shirts = Category(name='Shirts', user_id=user.id)
session.add(shirts)
session.commit()

jeans = Category(name='Jeans', user_id=user.id)
session.add(jeans)
session.commit()

shoes = Category(name='Shoes', user_id=user.id)
session.add(shoes)
session.commit()

bags = Category(name='Bags', user_id=user.id)
session.add(bags)
session.commit()

accessories = Category(name='Accessories', user_id=user.id)
session.add(accessories)
session.commit()

hoodies = Category(name='Hoodies', user_id=user.id)
session.add(hoodies)
session.commit()

sweatshirts = Category(name='Sweatshirts', user_id=user.id)
session.add(sweatshirts)
session.commit()

# Add products
product1 = Product(
    name='cherokee shirt',
    description='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet.
    Praesent eleifend laoreet pulvinar.''',
    price=12,
    picture=(
        "https://s7d5.scene7.com/is/image/ColumbiaSportswear2/"
        "1617431_073_f?$MHW_grid$&align=0,1"
    ),
    category=jeans,
    user=user)
session.add(product1)
session.commit()

product1 = Product(
    name='cherokee shirt',
    description='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet.
    Praesent eleifend laoreet pulvinar.''',
    price=12,
    picture=(
        "https://s7d5.scene7.com/is/image/ColumbiaSportswear2/"
        "1617431_073_f?$MHW_grid$&align=0,1"
    ),
    category=jeans,
    user=user)
session.add(product1)
session.commit()

product1 = Product(
    name='cherokee shirt',
    description='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet.
    Praesent eleifend laoreet pulvinar.''',
    price=12,
    picture=(
        "https://s7d5.scene7.com/is/image/ColumbiaSportswear2/"
        "1617431_073_f?$MHW_grid$&align=0,1"
    ),
    category=jeans,
    user=user)
session.add(product1)
session.commit()

product1 = Product(
    name='cherokee shirt',
    description='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet.
    Praesent eleifend laoreet pulvinar.''',
    price=12,
    picture=(
        "https://s7d5.scene7.com/is/image/ColumbiaSportswear2/"
        "1617431_073_f?$MHW_grid$&align=0,1"
    ),
    category=jeans,
    user=user)
session.add(product1)
session.commit()

product1 = Product(
    name='cherokee shirt',
    description='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet.
    Praesent eleifend laoreet pulvinar.''',
    price=12,
    picture=(
        "https://s7d5.scene7.com/is/image/ColumbiaSportswear2/"
        "1617431_073_f?$MHW_grid$&align=0,1"
    ),
    category=jeans,
    user=user)
session.add(product1)
session.commit()

product1 = Product(
    name='cherokee shirt',
    description='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet.
    Praesent eleifend laoreet pulvinar.''',
    price=12,
    picture=(
        "https://s7d5.scene7.com/is/image/ColumbiaSportswear2/"
        "1617431_073_f?$MHW_grid$&align=0,1"
    ),
    category=shoes,
    user=user)
session.add(product1)
session.commit()

product1 = Product(
    name='cherokee shirt',
    description='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Aenean dapibus dui sapien, vitae tempus felis aliquet sit amet.
    Praesent eleifend laoreet pulvinar.', price=12''',
    picture=(
        "https://s7d5.scene7.com/is/image/ColumbiaSportswear2/"
        "1617431_073_f?$MHW_grid$&align=0,1"
    ),
    category=shirts,
    user=user)
session.add(product1)
session.commit()

print('Added data to database')
