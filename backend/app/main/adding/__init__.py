from flask import Blueprint

bp = Blueprint('adding', __name__)

from app.main.adding import routes
