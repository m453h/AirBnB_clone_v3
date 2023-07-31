#!/usr/bin/python3
"""
cities.py
This module creates a new view for City objects that
handles all default RESTFul API actions
"""

from flask import jsonify, request, abort
from api.v1.views import app_views
from markupsafe import escape
from models import storage
from models.city import City
from models.state import State
from os import environ, getenv


@app_views.route("/states/<state_id>/cities", methods=["GET"],
                 strict_slashes=False)
def get_state_cities(state_id):
    """ Retrieves the list of all City objects of a State """
    state_id_cln = escape(state_id)
    key = "State." + state_id_cln
    output = []

    objs = storage.all(State)
    if key in objs:
        state = objs[key]
        retrieved = state.cities

        if retrieved:
            for city in retrieved:
                output.append(city.to_dict())

        return jsonify(output)
    else:
        abort(404)


@app_views.route("/cities/<city_id>", methods=["GET"], strict_slashes=False)
def get_city(city_id):
    """ Retrieves a City object """
    city_id_cln = escape(city_id)
    key = "City." + city_id_cln

    objs = storage.all(City)

    if key in objs:
        return jsonify(objs[key].to_dict())
    else:
        abort(404)


@app_views.route("/cities/<city_id>", methods=["DELETE"], strict_slashes=False)
def delete_city(city_id):
    """ Deletes a City object """
    city_id_cln = escape(city_id)
    key = "City." + city_id_cln

    objs = storage.all(City)
    obj_keys = objs.keys()

    if key in obj_keys:
        objs[key].delete()
        storage.save()
        return jsonify({})
    else:
        abort(404)


@app_views.route("/states/<state_id>/cities", methods=["POST"],
                 strict_slashes=False)
def create_city(state_id):
    """ Creates a City """
    try:
        json_data = request.get_json()
    except Exception:
        abort(400, description="Not a JSON")

    if not json_data:
        abort(400, description="Not a JSON")

    if "name" not in json_data.keys():
        abort(400, description="Missing name")

    if json_data["name"] == "":
        abort(400, description="Missing name")

    state_id_cln = escape(state_id)
    key = "State." + state_id_cln

    objs = storage.all(State)
    obj_keys = objs.keys()
    if key in obj_keys:
        new_city = City(**json_data)
        setattr(new_city, "state_id", state_id_cln)
        new_city.save()
        return jsonify(new_city.to_dict()), 201
    else:
        abort(404)


@app_views.route("/cities/<city_id>", methods=["PUT"], strict_slashes=False)
def update_city(city_id):
    """ Updates a City object """
    if len(request.data) == 0:
        abort(400, "Not a JSON")

    try:
        json_data = request.get_json()
    except Exception:
        abort(400, description="Not a JSON")

    if not json_data:
        abort(400, description="Not a JSON")

    city_id_cln = escape(city_id)
    key = "City." + city_id_cln

    objs = storage.all(City)
    obj_keys = objs.keys()

    if key in obj_keys:
        skip = ["id", "state_id", "created_at", "updated_at"]
        for data in json_data.keys():
            if data in skip:
                continue
            else:
                setattr(objs[key], data, json_data[data])
        objs[key].save()
        return jsonify(objs[key].to_dict())
    else:
        abort(404)
