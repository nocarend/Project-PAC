from flask import Blueprint

bp = Blueprint('adding', __name__)

from app.api.adding import routes
