from urllib import response
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap5 import Bootstrap
from tcgdexsdk import TCGdex
from databaseModel import database, User, bcrypt, ShoppingCart, Card
import requests
from functools import wraps


# user verfication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# tcgdex = TCGdex("en")
#
# # create an instance of Flask
app = Flask(__name__)

bootstrap = Bootstrap(app)

# Data storage for favorites
checkedOutN = []
checkedOut = []

# Flask Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "supersecretkey"  # Add a secret key for sessions and flash messages

# Initialize database and bcrypt with the app
database.init_app(app)
bcrypt.init_app(app)

# set up database
with app.app_context():
    database.create_all()

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if user exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists', 'error')
            return redirect(url_for('signup'))

        # Add new user
        new_user = User(username=username, email=email, password=password)
        database.session.add(new_user)
        database.session.commit()
        flash('Account created successfully.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check user credentials
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Home route
@app.route('/')
@login_required
def home():
    return render_template('index.html')


# Search route
@app.route('/search', methods=['GET'])
def search():
    # search for either set or name
    searh_term = request.args.get('search_term', '')
    search_type = request.args.get('search_type', 'name')
    cards = []

    # try to find specfic search query
    try:
        if search_type == 'name':
            response = requests.get(f'https://api.tcgdex.net/v2/en/cards?name={search_term}')
        elif search_type == 'set':
            response = requests.get(f'https://api.tcgdex.net/v2/en/sets/{search_term}')

        response.raise_for_status()
        cards = response.json()
        return render_template('search.html', cards = cards, searh_term = searh_term)
    except requests.exceptions.RequestException:
        return render_template('search.html', cards = None, error = "No results found")

# addind to cart route
@app.route('/add_to_cart', methods = ['POST'])
def add_to_cart():
    # login check
    if 'user_id' not in session:
        flash('You mush be logged in')
        return redirect(url_for('login'))

    card_id = request.form.get('card_id')
    if not card_id:
        flash('No card selscted')
        return redirect(url_for('search'))

    existing_item = ShoppingCart.query.filter_by(user_id = session.get('user_id'), card_id = card_id).first()
    if existing_item:
        flash('Card already added to cart')
        return redirect(url_for('search'))
    
    # add new card
    new_item = ShoppingCart(user_id = session.get('user_id'), card_id = card_id)
    database.session.add(new_item)
    database.session.commit()
    flash('Card added to your cart')
    return(redirect(url_for('search')))


@app.route('/pokedex', methods=['GET'])
def pokedex():
    pokemon_name = request.args.get('name', 'pikachu').lower()

    try:
        # Fetch Pokémon data
        response = requests.get(f'https://api.tcgdex.net/v2/en/cards?name={pokemon_name}')

        response.raise_for_status()
        pokemon = response.json()

        return render_template('pokedex.html', pokemon=pokemon, checkedOut=checkedOut, error=None)

    except requests.exceptions.RequestException:
        return render_template('pokedex.html', pokemon=None, checkedOut=checkedOut, error="Pokémon not found. Try another name!")

@app.route('/cart', methods=['POST', 'GET'])
def cart():
    if 'user_id' not in session:
        flash('You must be logged in to access the cart.', 'error')
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    if request.method == 'POST':
        card_id = request.form.get('card_id')
        if not card_id:
            flash('No card selected.', 'error')
            return redirect(url_for('search'))

        # Check if the card is already in the cart
        existing_item = ShoppingCart.query.filter_by(user_id=user_id, card_id=card_id).first()
        if existing_item:
            flash('Card already in your cart.', 'info')
        else:
            # Add the card to the shopping cart
            new_item = ShoppingCart(user_id=user_id, card_id=card_id)
            database.session.add(new_item)
            database.session.commit()
            flash('Card added to your cart.', 'success')

    # Fetch all cards in the user's cart
    cart_items = ShoppingCart.query.filter_by(user_id=user_id).all()
    cards = []

    # Fetch card details for each card in the cart
    for item in cart_items:
        try:
            response = requests.get(f'https://api.tcgdex.net/v2/en/cards/{item.card_id}')
            response.raise_for_status()
            card = response.json()
            cards.append(card)
        except requests.exceptions.RequestException:
            flash(f"Could not retrieve details for card ID {item.card_id}.", 'error')

    return render_template('cart.html', cards=cards)


@app.route('/tierlist', methods=['GET'])
def tier_list():
    pokemon_tl = {
        "S": [],
        "A": [],
        "B": [],
        "C": [],
        "F": []
    }

    tiered_pokemon = [
        {"name": "nidoking", "tier": "S"},
        {"name": "victini", "tier": "S"},
        {"name": "charizard", "tier": "A"},
        {"name": "slowpoke", "tier": "A"},
        {"name": "gengar", "tier": "A"},
        {"name": "hitmonchan", "tier": "B"},
        {"name": "mawile", "tier": "B"},
        {"name": "blaziken", "tier": "B"},
        {"name": "geodude", "tier": "C"},
        {"name": "loudred", "tier": "C"},
        {"name": "bunnelby", "tier": "C"},
        {"name": "zubat", "tier": "F"},
        {"name": "diglett", "tier": "F"},
        {"name": "gumshoos", "tier": "F"}
    ]

    try:
        for entry in tiered_pokemon:
            response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{entry["name"]}')
            response.raise_for_status()
            pokemon = response.json()
            pokemon_tl[entry["tier"]].append(pokemon)

        return render_template('tierlist.html', pokemonTL=pokemon_tl)

    except requests.exceptions.RequestException:
        return "Error fetching Pokémon data.", 500
    
@app.route('/browseBySet', methods=['GET'])
def browse():
    set_name = request.args.get('set', 'Darkness Ablaze').lower()

    try:
        # Fetch Pokémon set data
        response = requests.get(f'https://api.tcgdex.net/v2/en/sets/{set_name}')
        response.raise_for_status()
        pokemon_set = response.json()

        return render_template('browseBySet.html', pokemon_set=pokemon_set, checkedOut=checkedOut, error=None)

    except requests.exceptions.RequestException:
        return render_template('browseBySet.html', pokemon_set=None, checkedOut=checkedOut, error="Set not found. Try another name!")


if __name__ == '__main__':
    app.run(debug=True)
