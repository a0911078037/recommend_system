from __future__ import absolute_import
from flask import Blueprint
import flask_restx as restful
from .router import router


bp = Blueprint('v1', __name__, static_folder='static')
api = restful.Api(bp, catch_all_404s=True)

for route in router:
    api.add_resource(route.pop('resource'), *route.pop('urls'), **route)
