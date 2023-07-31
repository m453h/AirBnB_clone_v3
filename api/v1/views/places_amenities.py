#!/usr/bin/python3
"""
place_amenities.py
This module creates a new view for Amenity objects that
handles all default RESTFul API actions
"""

from flask import jsonify, request, abort
from api.v1.views import app_views
from models import storage
from models.amenity import Amenity
from models.place import Place
from os import getenv, environ


@app_views.route("/places/<place_id>/amenities", methods=["GET"],
                 strict_slashes=False)
def get_place_amenities(place_id):
    """ Retrieves the list of all Amenity objects of a Place """
    output = []

    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    if "HBNB_TYPE_STORAGE" in environ and getenv("HBNB_TYPE_STORAGE") == "db":
        amenities = place.amenities
        for amenity in amenities:
            output.append(amenity.to_dict())
    else:
        amenity_ids = place.amenity_ids
        for amenity_id in amenity_ids:
            amenity = storage.get(Amenity, amenity_id)
            output.append(amenity.to_dict())

    return jsonify(output), 200


@app_views.route("/places/<place_id>/amenities/<amenity_id>",
                 methods=["DELETE"], strict_slashes=False)
def delete_amenity(place_id, amenity_id):
    """ Deletes a Amenity object """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)

    if "HBNB_TYPE_STORAGE" in environ and getenv("HBNB_TYPE_STORAGE") == "db":
        amenities = place.amenities
        if amenity not in amenities:
            abort(404)
        amenities.remove(amenity)
    else:
        amenity_ids = place.amenity_ids
        if amenity_id not in amenity_ids:
            abort(404)
        amenity_ids.remove(amenity_id)

    place.save()
    return jsonify({}), 200


@app_views.route("/places/<place_id>/amenities/<amenity_id>", methods=["POST"],
                 strict_slashes=False)
def create_amenity(place_id, amenity_id):
    """ Creates a Amenity """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)

    if "HBNB_TYPE_STORAGE" in environ and getenv("HBNB_TYPE_STORAGE") == "db":
        amenities = place.amenities
        if amenity in amenities:
            return jsonify(amenity.to_dict()), 200
        amenities.append(amenity)
    else:
        amenity_ids = place.amenity_ids
        if amenity_id in amenity_ids:
            return jsonify(amenity.to_dict()), 200
        amenity_ids.append(amenity_id)

    place.save()
    return jsonify(amenity.to_dict()), 201
