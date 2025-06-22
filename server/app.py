#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# GET RESTAURANTS
class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return make_response(jsonify(
            [r.to_dict(rules=("-restaurant_pizzas",)) for r in restaurants]
        ), 200)

api.add_resource(Restaurants, "/restaurants")



# GET restaurant by id and DELETE restaurant by id
class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return make_response(jsonify(
                restaurant.to_dict(rules=("restaurant_pizzas.pizza",))
            ), 200)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

api.add_resource(RestaurantByID, "/restaurants/<int:id>")



# GET PIZZAS
class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return make_response(jsonify(
            [p.to_dict(rules=("-restaurant_pizzas",)) for p in pizzas]
        ), 200)

api.add_resource(Pizzas, "/pizzas")



# POST RESTAURANTPIZZAS
class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        if not (1 <= data.get("price", 0) <= 30):
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        try:
            rp = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"],
            )
            db.session.add(rp)
            db.session.commit()

            return make_response(jsonify(
                rp.to_dict(rules=(
                    "-restaurant.restaurant_pizzas",
                    "-pizza.restaurant_pizzas",
                ))
            ), 201)

        except Exception:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
