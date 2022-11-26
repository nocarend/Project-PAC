from flask import Blueprint

bp = Blueprint('protected', __name__)

from app.api.protected import routes
