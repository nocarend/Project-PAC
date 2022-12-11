from flask import jsonify, request
from flask_praetorian import auth_required, current_user

from app.api import bp
from app.models import UserSignup


@bp.route('/')
def home():
    return {"Hello": "World"}, 200


@bp.route('/approve_user', methods=['POST'])
@auth_required
# @roles_required
def approve_user():
    req = request.get_json(force=True)
    username = req.get('username', None)
    req['is_approved'] = False
    user = UserSignup.query.filter_by(user_login=username).one_or_none()
    if user:
        user.add_user()
        req['is_approved'] = True
    return jsonify(req), 200 if user else 404


@bp.route('/reject_user', methods=['POST'])
@auth_required
# @roles_required
def reject_user():
    req = request.get_json(force=True)
    username = req.get('username', None)
    req['is_rejected'] = False
    user = UserSignup.query.filter_by(user_login=username).one_or_none()
    if user:
        user.delete_user()
        req['is_rejected'] = True
    return jsonify(req), 200 if user else 404


"""
Пока не уверен, что этот апи необходим. Так как в браузере нет проблем с простой генерацией 
странички по ссылке. Джсоны для этого вроде не нужны. Обговорить с Васей.
"""

# @bp.route('/user', methods=['POST'])  # только для админ ролей, кладовщик и т д
# @auth_required
# # @roles_required
# def user():
#     req = request.get_json(force=True)
#     username = req.get('username')
#     req['is_success'] = True
#     user = User.query.filter_by(user_login=username).one_or_none()
#     user_json = {}
#     if user:
#         req['is_success'] = True
#         user_json = {
#             "username": user.user_login,
#             "user_roles": user.user_roles,
#             "user_money": user.user_money,
#             "user_items": user.show_items()
#         }
#     print(user_json)
#     # print(jsonify(user.show_items()).get_json())
#     # print(jsonify(user_json))
#     return jsonify(user_json), 200 if user else 404

# @bp.route('/item')
# @auth_required
#
# def item(item_id):
#     item = Item.query.filter_by(item_id=item_id).first_or_404()
#     return render_template('item.html', item=item)
