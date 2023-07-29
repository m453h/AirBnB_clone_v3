#!/usr/bin/python3
"""
users.py
This module creates a new view for User objects that
handles all default RESTFul API actions
"""

from flask import jsonify, abort, request
from api.v1.views import app_views
from models import storage
from models.user import User


@app_views.route("/users/", methods=["GET"])
def list_users():
    """Retrieves the list of all User objects"""
    user_objs = storage.all(User)
    users_list = []
    for user in user_objs.values():
        users_list.append(user.to_dict())
    return jsonify(users_list)


@app_views.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    """Retrieves a User object by id"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)

    return jsonify(user.to_dict())


@app_views.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Deletes a User object by id"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    user.delete()
    storage.save()
    return jsonify({})


@app_views.route("/users/", methods=["POST"])
def create_user():
    """Creates a new User and stores it"""
    user_data = request.get_json()
    if not user_data:
        abort(400, "Not a JSON")
    if 'email' not in user_data:
        abort(400, "Missing email")
    if 'password' not in user_data:
        abort(400, "Missing password")
    user = User(**user_data)
    user.save()
    return jsonify(user.to_dict()), 201


@app_views.route("/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    """Updates a User given by user_id and stores it"""
    user = storage.get(User, user_id)

    if user is None:
        abort(404)
    if len(request.data) == 0:
        abort(400, "Not a JSON")
    user_data = request.get_json()
    if not user_data:
        abort(400, "Not a JSON")
    for key, value in user_data.items():
        keys_to_ignore = ["id", "created_at", "updated_at", "email"]
        if key not in keys_to_ignore:
            setattr(user, key, value)
    user.save()
    user = user.to_dict()
    return jsonify(user), 200
