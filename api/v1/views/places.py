#!/usr/bin/python3
"""
This module handles the view for Place objects that handles
all default RESTFul API actions
"""
from flask import jsonify, abort, request
from api.v1.views import place_views, city_views, app_views
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from models.state import State
from models.amenity import Amenity
from os import getenv


@city_views.route("/<string:city_id>/places", methods=["GET"],
                  strict_slashes=False)
def list_places(city_id):
    """Retrieves the list of all places objects in a city"""
    places_objs = storage.all(Place)
    places_list = []
    for place in places_objs.values():
        if place.city_id == city_id:
            places_list.append(place.to_dict())

    if not places_list:
        abort(404)
    return jsonify(places_list)


@place_views.route("/<string:place_id>", methods=["GET"], strict_slashes=False)
def get_place(place_id):
    """Retrieves an Place object by id"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    return jsonify(place.to_dict())


@place_views.route("/<string:place_id>", methods=["DELETE"],
                   strict_slashes=False)
def delete_place(place_id):
    """Deletes a Place object by id"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    place.delete()
    storage.save()
    return jsonify({})


@city_views.route("/<string:city_id>/places", methods=["POST"],
                  strict_slashes=False)
def create_place(city_id):
    """Creates a new Place and stores it"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    if len(request.data) == 0:
        abort(400, "Not a JSON")
    place_data = request.get_json()
    if not place_data:
        abort(400, "Not a JSON")
    if 'user_id' not in place_data:
        abort(400, "Missing user_id")
    user = storage.get(User, place_data['user_id'])
    if user is None:
        abort(404)
    if 'name' not in place_data:
        abort(400, "Missing name")

    setattr(place, "city_id", city_id)
    place = Place(**place_data)
    place.save()
    return jsonify(place.to_dict()), 201


@place_views.route("/<string:place_id>", methods=["PUT"], strict_slashes=False)
def update_place(place_id):
    """Updates a Place given by place_id and stores it"""
    place = storage.get(Place, place_id)

    if place is None:
        abort(404)
    if len(request.data) == 0:
        abort(400, "Not a JSON")
    place_data = request.get_json()
    if not place_data:
        abort(400, "Not a JSON")
    for key, value in place_data.items():
        keys_to_ignore = ["id", "user_id", "city_id",
                          "created_at", "updated_at"]
        if key not in keys_to_ignore:
            setattr(place, key, value)
    place.save()
    storage.save()
    place = place.to_dict()
    return jsonify(place), 200


@app_views.route("/places_search", methods=["POST"])
def places_search():
    """ Retrieves all Place objects depending of the JSON
    in the body of the request.
    """
    try:
        json_data = request.get_json()
    except Exception:
        abort(400, "Not a JSON")

    output = []
    pre_output = []

    if len(json_data) == 0:
        places = storage.all(Place)
        for place in places.values():
            output.append(place.to_dict())
        return output

    if "states" in json_data and len(json_data["states"]) != 0:
        for state_id in json_data["states"]:
            state = storage.get(State, state_id)
            state_cities = state.cities
            for city in state_cities:
                places = city.places
                for place in places:
                    pre_output.append(place)

    if "cities" in json_data and len(json_data["cities"]) != 0:
        for city_id in json_data["cities"]:
            city = storage.get(City, city_id)
            if "states" in json_data and len(json_data["states"]) != 0:
                if city.state_id in json_data["states"]:
                    continue
            places = city.places
            for place in places:
                pre_output.append(place)

    if len(pre_output) == 0:
        places = storage.all(Place)
        for place in places.values():
            pre_output.append(place)

    if "amenities" in json_data and len(json_data["amenities"]) != 0:
        for place in pre_output:
            not_present = 0
            amenity_ids = []
            if getenv("HBNB_TYPE_STORAGE") == "db":
                amenities = place.amenities
                for amenity in amenities:
                    amenity_ids.append(amenity.id)
            else:
                amenity_ids = place.amenity_ids

            if all(amen_id in amenity_ids for amen_id
                   in json_data["amenities"]):
                place_dict = place.to_dict()
                if getenv("HBNB_TYPE_STORAGE") == "db":
                    del place_dict["amenities"]
                else:
                    del place_dict["amenity_ids"]
                output.append(place_dict)
    else:
        for place in pre_output:
            output.append(place.to_dict())

    return jsonify(output), 200
