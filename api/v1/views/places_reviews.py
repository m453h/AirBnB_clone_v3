#!/usr/bin/python3
"""
place_reviews.py
This module creates a new view for Review objects that
handles all default RESTFul API actions
"""

from flask import jsonify, request, abort
from api.v1.views import app_views
from markupsafe import escape
from models import storage
from models.review import Review
from models.place import Place
from models.user import User


@app_views.route("/places/<string:place_id>/reviews", methods=["GET"],
                 strict_slashes=False)
def get_place_reviews(place_id):
    """ Retrieves the list of all Review objects of a Place """
    output = []

    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    reviews = place.reviews

    for review in reviews:
        output.append(review.to_dict())

    return jsonify(output)


@app_views.route("/reviews/<string:review_id>", methods=["GET"],
                 strict_slashes=False)
def get_review(review_id):
    """ Retrieves a Review object """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)

    return jsonify(review.to_dict())


@app_views.route("/reviews/<string:review_id>", methods=["DELETE"],
                 strict_slashes=False)
def delete_review(review_id):
    """ Deletes a Review object """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)

    review.delete()
    storage.save()
    return jsonify({})


@app_views.route("/places/<string:place_id>/reviews", methods=["POST"],
                 strict_slashes=False)
def create_review(place_id):
    """ Creates a Review """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    try:
        json_data = request.get_json()
    except Exception:
        abort(400, description="Not a JSON")

    if not json_data:
        abort(400, description="Not a JSON")

    if "user_id" not in json_data.keys():
        abort(400, description="Missing user_id")

    if json_data["user_id"] == "":
        abort(400, description="Missing user_id")

    if "text" not in json_data.keys():
        abort(400, description="Missing text")

    user_id = json_data["user_id"]
    user = storage.get(User, user_id)
    if user is None:
        abort(404)

    new_review = Review(**json_data)
    setattr(new_review, "place_id", place_id)
    storage.new(new_review)
    storage.save()
    return jsonify(new_review.to_dict()), 201


@app_views.route("/reviews/<review_id>", methods=["PUT"],
                 strict_slashes=False)
def update_review(review_id):
    """ Updates a Review object """
    if len(request.data) == 0:
        abort(400, "Not a JSON")

    try:
        json_data = request.get_json()
    except Exception:
        abort(400, description="Not a JSON")

    if not json_data:
        abort(400, description="Not a JSON")

    review = storage.get(Review, review_id)
    if review is None:
        abort(404)

    skip = ["id", "user_id", "created_at", "updated_at", "place_id"]

    for data in json_data.keys():
        if data in skip:
            continue
        else:
            setattr(review, data, json_data[data])

    review.save()
    return jsonify(review.to_dict())
