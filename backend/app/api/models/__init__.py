from flask import Blueprint

bp = Blueprint('models', __name__)

from app.api.models import user, item