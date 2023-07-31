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
    city = storage.get("City", city_id)
    if city is None:
        abort(404)
    places_list = []
    places = city.places
    for place in places:
        places_list.append(place.to_dict())
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
    place = place.to_dict()
    return jsonify(place), 200


@app_views.route("/places_search", methods=["POST"], strict_slashes=False)
def places_search():
    """ Retrieves all Place objects depending of the JSON
    in the body of the request.
    """
    try:
        json_data = request.get_json()
    except Exception:
        abort(400, "Not a JSON")

    if json_data:
        states = json_data.get('states', None)
        cities = json_data.get('cities', None)
        amenities = json_data.get('amenities', None)

    if not json_data or (not states and not cities and
                         not amenities):
        places = storage.all(Place).values()
        places_list = []
        for place in places:
            places_list.append(place.to_dict())
        return jsonify(places_list)

    places_list = []
    if states:
        for state_id in states:
            state = storage.get(State, state_id)
            if state:
                for city in state.cities:
                    if city:
                        places_list.extend(city.places)
    if cities:
        city_objs = []
        for city_id in cities:
            city = storage.get(City, city_id)
            if city:
                city_objs.append(city)
        for city in city_objs:
            if city:
                for place in city.places:
                    if place not in places_list:
                        places_list.append(place)
    if amenities:
        if not places_list:
            places_list = storage.all(Place).values()
        amenity_objs = []
        for amenity_id in amenities:
            amenity = storage.get(Amenity, amenity_id)
            if amenity:
                amenity_objs.append(amenity)

        new_places_list = []
        for place in places_list:
            all_amenities_present = True
            for amenity in amenities_obj:
                if amenity not in place.amenities:
                    all_amenities_present = False
                    break
            if all_amenities_present:
                new_places_list.append(place)

        places_list = new_places_list

    results = []
    for place in places_list:
        place_dict = place.to_dict()
        place_dict.pop('amenities', None)
        results.append(place_dict)

    return jsonify(results)
