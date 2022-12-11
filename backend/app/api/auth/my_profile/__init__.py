from flask import Blueprint

bp = Blueprint('my_profile', __name__)

from app.api.auth.my_profile import routes