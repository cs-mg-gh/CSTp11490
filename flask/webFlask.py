from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap5 import Bootstrap
from tcgdexsdk import TCGdex
import requests

tcgdex = TCGdex("en")

# create an instance of Flask
app = Flask(__name__)

bootstrap = Bootstrap(app)

# Data storage for favorites
checkedOutN = []
checkedOut = []

@app.route('/')
def home():
    return render_template('index.html')

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

@app.route('/cart', methods=['POST'])
def cart():
    card_id = request.form.get('card_id')

    # Check if the card is already in the favorites list
    if card_id and card_id not in [card['id'] for card in checkedOut]:
        try:
            # Fetch card details from the API
            response = requests.get(f'https://api.tcgdex.net/v2/en/cards/{card_id}')
            response.raise_for_status()
            card = response.json()

            # Add card to the favorites list
            checkedOut.append(card)
            checkedOutN.append(card['name'])


        except requests.exceptions.RequestException:
            return redirect(url_for('pokedex', error="Could not add card to favorites."))

    return redirect(url_for('pokedex'))

@app.route('/cart', methods=['GET'])
def favorite_pokemon():
    return render_template('cart.html', checkedOut=checkedOut)

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
