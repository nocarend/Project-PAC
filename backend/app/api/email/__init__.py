from flask import Blueprint

bp = Blueprint('email', __name__)

from app.api.email import routes
