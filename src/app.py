"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planets, Favorites
import requests
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

#traer todos los characters
@app.route('/character', methods=["GET"])
def get_all_character():

    character = Character()
    character= character.query.all()
    character = list(map(lambda item: item.serialize(), character))

    return jsonify(character), 200

# traer los characer por id
@app.route('/character/<int:character_id>', methods=["GET"])
def get_one_character(character_id):
    character = Character()
    character = character.query.get(character_id)

    if character is None:
        raise APIException("User not found", status_code=404)
    else:
        return jsonify(character.serialize())
    
#traer todos los planetas
@app.route('/planets', methods=["GET"])
def get_all_planets():

    planets = Planets()
    planets = planets.query.all()
    planets = list(map(lambda item: item.serialize(), planets))

    print(planets)
    return jsonify(planets), 200

#traer los planetas por id
@app.route('/planets/<int:planet_id>', methods=["GET"])
def get_one_planet(planet_id):

    planet = Planets()
    planet = planet.query.get(planet_id)

    if planet is None:
        raise APIException("Planet not found", status_code=404)
    else:
        return jsonify(planet.serialize())

# traer todos los usuarios
@app.route('/users', methods=["GET"])
def get_all_users():
    users = User()
    users = users.query.all()

    users = list(map(lambda item: item.serialize(), users ))
    return jsonify(users), 200

# traer todos los favoritos de un usuario
@app.route('/users/favorites/<int:theid>', methods=["GET"])
def get_all_favorites_user(theid=None):
    user = User()
    user = user.query.filter_by(id=theid).first()

    return jsonify(user.serialize()), 200

# agregamos un character a favoritos
@app.route("/favorite/character/<int:character_id>", methods=["POST"])
def add_character_fav(character_id):
    user_id = 3

    fav = Favorites()
    fav.user_id = user_id
    fav.character_id = character_id

    db.session.add(fav)

    try:
        db.session.commit()
        return jsonify("se guardo exitosamente"), 200
    except Exception as error:
        db.session.rollback
        return jsonify("error debes revisar"),401

# agregamos un planeta a favoritos
@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_planet_fav(planet_id):
    user_id = 3
    fav = Favorites()
    fav.user_id = user_id
    fav.planets_id = planet_id

    db.session.add(fav)

    try:
        db.session.commit()
        return jsonify("Se guardo exitosamente"), 200
    except Exception as erro:
        db.session.rollback
        return jsonify("Error deves revisar"),201
        
@app.route("/favorite/character/<int:character_id>", methods=["DELETE"])
def delete_characte_fav(character_id):
    user_id = 3  # Assume we are dealing with user ID 3
    fav = Favorites.query.filter_by(user_id=user_id, character_id=character_id).first()

    if not fav:
        return jsonify("Favorite planet not found"), 404

    try:
        db.session.delete(fav)
        db.session.commit()
        return jsonify("Favorite planet deleted successfully"), 200
    except Exception as error:
        db.session.rollback()
        return jsonify("Error occurred, could not delete"), 500

@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_planet_fav(planet_id):
    user_id = 3  # Assume we are dealing with user ID 3
    fav = Favorites.query.filter_by(user_id=user_id, planets_id=planet_id).first()

    if not fav:
        return jsonify("Favorite planet not found"), 404

    try:
        db.session.delete(fav)
        db.session.commit()
        return jsonify("Favorite planet deleted successfully"), 200
    except Exception as error:
        db.session.rollback()
        return jsonify("Error occurred, could not delete"), 500
  
    
# traer todos los planets
#@app.route('/planets/')

@app.route('/character/population', methods=['GET'])
def get_character_population():
    response = requests.get("https://www.swapi.tech/api/people?page=1&1limit=2")
    response = response.json()
    response = response.get("results")

    for item in response:
        result = requests.get(item.get("url"))
        result = result.json()
        result = result.get("result")
        character =Character()
        character.name = result.get("properties").get("name")
        character.gender = result.get("properties").get("gender")
        character.height = result.get("properties").get("height")
        character.hair_color = result.get("properties").get("hair_color")
        character.birth_year = result.get("properties").get("birth_year")

        try:
            db.session.add(character)
            db.session.commit()
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify("error"), 500

    return jsonify("populando listo"), 200

@app.route('/planet/population', methods=['GET'])
def get_planet_population():
    response = requests.get("https://www.swapi.tech/api/planets?page=1&1limit=2")
    response = response.json()
    response = response.get("results")

    for item in response:
        result = requests.get(item.get("url"))
        result = result.json()
        result = result.get("result")
        planets =Planets()
        planets.name = result.get("properties").get("name")
        planets.diameter = result.get("properties").get("diameter")
        planets.rotation_period = result.get("properties").get("rotatio period")
        planets.gravity = result.get("properties").get("gravity")
        planets.population = result.get("properties").get("population")
        planets.terrain = result.get("properties").get("terrain")

        try:
            db.session.add(planets)
            db.session.commit()
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify("error"), 500

    return jsonify("populando listo"), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
