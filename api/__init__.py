from flask import Blueprint

from api.test_api import test_api

api_bp = Blueprint('api', __name__)

# Import API controllers

# url_prefix='/test' means the /test endpoint
api_bp.register_blueprint(test_api, url_prefix='/v1/test')