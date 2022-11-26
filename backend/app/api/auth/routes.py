from flask import jsonify, request

from app import guard
from app.api.auth import bp
from app.models import User


@bp.route('/login', methods=['POST'])
def login():
    req = request.get_json(force=True)
    username = req.get('username', None)
    password = req.get('password', None)
    us = User.lookup(username)
    if us:
        password = us.hashed_password(password)
    user = guard.authenticate(username, password)
    ret = {"access_token": guard.encode_jwt_token(user)}
    return jsonify(ret), 200 if user else 404


@bp.route('/refresh', methods=['POST'])
def refresh():
    """
    Refreshes an existing JWT by creating a new one that is a copy of the old
    except that it has a refreshed access expiration.
    .. example::
       $ curl http://localhost:5000/api/refresh -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    old_token = guard.read_token_from_header()
    new_token = guard.refresh_jwt_token(old_token)
    ret = {'access_token': new_token}
    return jsonify(ret), 200


@bp.route('/verify_password_token', methods=['POST'])
def verify_password_token():
    req = request.get_json(force=True)
    token = req.get('token', None)
    req['is_success'] = False
    user = User.verify_reset_password_token(token)
    if user:
        req['is_success'] = True
    return jsonify(req), 200 if user else 404


@bp.route('/set_new_password', methods=['POST'])  # хм два одинаковых запроса
def set_new_password():
    req = request.get_json(force=True)
    token = req.get('token', None)
    password = req.get('password', None)
    req['is_success'] = True
    user = User.verify_reset_password_token(token)
    user.set_password(password)
    return jsonify(req), 200 if user else 404
