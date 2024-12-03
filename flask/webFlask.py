from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
import requests


# create an instance of Flask
app = Flask(__name__)
bootstrap = Bootstrap5(app)

# Data storage for favorites
favoritesN = []
favorites = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pokedex', methods=['GET'])
def pokedex():
    pokemon_name = request.args.get('name', 'pikachu').lower()
    add_to_favorites = request.args.get('favorite') == 'on'

    try:
        # Fetch Pokémon data
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}')
        response.raise_for_status()
        pokemon = response.json()

        # Add to favorites if applicable
        if add_to_favorites and pokemon_name not in favoritesN:
            favoritesN.append(pokemon_name)
            favorites.append(pokemon)

        return render_template('pokedex.html', pokemon=pokemon, favorites=favorites, error=None)

    except requests.exceptions.RequestException:
        return render_template('pokedex.html', pokemon=None, favorites=favorites, error="Pokémon not found. Try another name!")

@app.route('/favorites', methods=['GET'])
def favorite_pokemon():
    return render_template('favorites.html', favorites=favorites)

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

if __name__ == '__main__':
    app.run(debug=True)
