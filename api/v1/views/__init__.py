#!/usr/bin/python3
"""
__init__.py
This module creates a variable app_views which is an instance of Blueprint
"""

from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix='/api/v1')
state_views = Blueprint('state_views', __name__, url_prefix='/api/v1/states')
amenity_views = Blueprint('amenity_views', __name__, url_prefix='/api/v1/amenities')
place_views = Blueprint('place_views', __name__, url_prefix='/api/v1/places')
city_views = Blueprint('city_views', __name__, url_prefix='/api/v1/cities')
user_views = Blueprint('user_views', __name__, url_prefix='/api/v1/users')


from api.v1.views.index import *
from api.v1.views.cities import *
from api.v1.views.states import *
from api.v1.views.amenities import *
from api.v1.views.places import *
from api.v1.views.users import *
from api.v1.views.places_reviews import *
