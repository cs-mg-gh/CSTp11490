# using sqlite through sqlalchemy to hold user data
# using bcrypt to hash passwords for security reasons
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

database = SQLAlchemy()
bcrypt = Bcrypt()

# user db 
class User(database.Model):
    # setting up basic rules
    # id, username, and email gave to be unique and not null
    # password doesnt have to be unique but cant be left blank

    id = database.Column(database.Integer, primary_key = True)
    username = database.Column(database.String(100), unique = True, nullable = False)
    email = database.Column(database.String(110), unique = True, nullable = False)
    password = database.Column(database.String(120), nullable = False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

# card db 
class Card(database.Model):
    # store card details and things of that nature 
    # id from tcgdex below
    id = database.Column(database.String(50), primary_key = True)
    name = database.Column(database.String(100), nullable = False)
    set = database.Column(database.String(100), nullable = False)
    image_url = database.Column(database.String(200), nullable = False)

    def __init__(self, card_id, name, set, image_url):
        self.id = card_id
        self.name = name
        self.set = set
        self.image_url = image_url

# shopping cart db
class ShoppingCart(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable = False)
    card_id = database.Column(database.String(50), database.ForeignKey('card.id'), nullable = False)

    card = database.relationship('Card', backref = 'cart_items', lazy = True)

    def __init(self, user_id, card_id):
        self.user_id = user_id
        self.card = card_id