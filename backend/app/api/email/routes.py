from flask import jsonify, request

from app.api.email import bp
from app.auth.email import send_password_reset_email
from app.models import User


@bp.route('/reset_password', methods=['POST'])
def reset_password():
    req = request.get_json(force=True)
    email = req.get('email', None)
    req['is_success'] = False
    user = User.query.filter_by(user_email=email).one_or_none()
    if user:
        send_password_reset_email(user)
        req['is_success'] = True
    return jsonify(req), 200 if user else 404
