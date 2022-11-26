from flask import jsonify, request
from flask_praetorian import auth_required

from app import db
from app.api.adding import bp
from app.models import Category, Item, User


@bp.route('/add_item', methods=['POST'])
@auth_required
# @roles_required
def add_item():
	req = request.get_json(force=True)
	item = req.get('item', None)
	category_id = req.get('category_id', None)
	weight = req.get('weight', None)
	quantity = req.get('quantity', None)
	cost = req.get('cost', None)
	description = req.get('description', None)
	req['is_added'] = True
	if None in [item, category_id, weight, quantity, cost]:
		req['is_added'] = False
		return jsonify(req), 404
	newItem = Item(item_name=item, category_id=category_id,
	               item_weight=weight,
	               item_quantity_max=quantity, item_cost=cost,
	               item_description="" if description is None else description)
	db.session.add(newItem)
	db.session.commit()
	return jsonify(req), 200


@bp.route('/add_category', methods=['POST'])
@auth_required
# @roles_required
def add_category():
	req = request.get_json(force=True)
	category = req.get('category', None)
	weight = req.get('weight', None)
	req['is_added'] = True
	if None in [category, weight]:
		req['is_added'] = False
		return jsonify(req), 404
	newCategory = Category(category_name=category, category_weight=weight)
	db.session.add(newCategory)
	db.session.commit()
	return jsonify(req), 200


# мне кажется, что валидация полей совсем не нужна в апи
@bp.route('/add_user', methods=['POST'])
@auth_required
# @roles_required
def add_user():
	req = request.get_json(force=True)
	login = req.get('login', None)
	password = req.get('password', None)
	full_name = req.get('user_name', None)
	email = req.get('user_email', None)
	phone = req.get('phone', None)
	req['is_added'] = True
	if None in [login, password, full_name, email, phone]:
		req['is_added'] = False
		return jsonify(req), 404
	newUser = User(user_login=login, user_password=password, user_name=full_name, user_email=email,
	               user_phone=phone)
	newUser.add_user()
	return jsonify(req), 200
