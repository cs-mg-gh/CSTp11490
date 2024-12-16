# using sqlite through sqlalchemy to hold user data
# using bcrypt to hash passwords for security reasons
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

database = SQLAlchemy()
bcrypt = Bcrypt()

class User(database.databaseModel):
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