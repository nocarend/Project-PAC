from flask import jsonify, request, Response
from flask_praetorian import current_rolenames, roles_accepted

from app import db
from app.api.auth.validators import email_validate, password_validate, phone_validate
from app.api.models import bp
from app.errors.handlers import ElementNotFoundError, JSONNotEnoughError, MethodNotAllowedError,\
	ValidationError
from app.helpers.functions import get_user_data, none_check
from app.models import User, UserSignup


@bp.route('/users', methods=['GET'])
@roles_accepted('treasurer', 'warehouseman', 'admin')
def users_get():
	"""
	Return all users data.
	---
	parameters:
		- in: header
		  name: Authorization
		  schema:
			type: string
			example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
		  required: true
	responses:
	  200:
	    description: All users data.
	    schema:
		  type: array
		  items:
		    type: object
		    properties:
		      user_id:
		        type: integer
		      user_login:
		        type: string
		      user_password:
		        type: string
		      user_name:
		        type: string
		      user_email:
		        type: string
		      user_money:
		        type: integer
		      user_isactive:
		        type: integer
		      user_datetime:
		        type: string
		      user_roles:
		        type: string
		      items:
		        type: array
		        items:
		          type: Item
	"""
	return jsonify(users=User.query.all()), 200


@bp.route('/users', methods=['POST'])
@roles_accepted('warehouseman', 'admin')
def users_post():
	"""
	Create a new user, admin feature.
	---
	parameters:
		- in: header
		  name: Authorization
		  schema:
			type: string
			example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
		  required: true
		- in: body
		  name: Data
		  schema:
		    type: object
		    properties:
		      login:
		        type: string
		      password:
		        type: string
		      name:
		        type: string
		      email:
		        type: string
		      phone:
		        type: string
	responses:
	  201:
	    description: User has created.
	  403:
	    description: Some unique data already exists in database or Some data doesn't match format.
	"""
	req = request.get_json(force=True)
	# protected_from_treasurer()
	login, password, name, email, phone = get_user_data(req)
	if None in [login, password, name, email, phone]:
		raise JSONNotEnoughError()
	if not email_validate(email) or not phone_validate(phone) or not password_validate(
			password):
		raise ValidationError()
	newUser = User(user_login=login, user_password=password, user_name=name,
	               user_email=email,
	               user_phone=phone)
	newUser.add()
	return Response(status=201)


@bp.route('/users/<username>', methods=['GET'])
@roles_accepted('treasurer', 'warehouseman', 'admin')
def users_username_get(username):
	"""
	Get user info and items by given username. Allowed only for warehouseman and admin roles.
	---
	parameters:
		- in: header
		  name: Authorization
		  schema:
			type: string
			example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
		  required: true
		- in: path
		  name: username
		  schema:
			type: string
			example: pepka
			required: true
	responses:
	  200:
		description: Return user info and items.
		schema:
		  type: object
		  properties:
		    items:
		      type: array
		      items:
		        type: object
		        properties:
		          is_confirm:
		            type: boolean
		          item:
		            type: object
		            properties:
		              avatar:
		                type: string
		              category:
		                type: object
		                properties:
		                  category_id:
		                    type: string
		                  category_name:
		                    type: string
		                  category_weight:
		                    type: integer
		              item_cost:
		                type: integer
		              item_description:
		                type: string
		              item_id:
		                type: integer
		              item_name:
		                type: string
		              item_quantity_current:
		                type: integer
		              item_quantity_max:
		                type: integer
		              item_weight:
		                type: integer
		          item_quantity:
		            type: integer
		          use_datetime:
		            type: string
		          use_description:
		            type: string
		    user_email:
		      type: string
		    user_id:
		      type: integer
		    user_isactive:
		      type: boolean
		    user_login:
		      type: string
		    user_money:
		      type: integer
		    user_name:
		      type: string
		    user_phone:
		      type: string
		    user_roles:
		      type: string
	  403:
		description: Element not found.
	"""
	user = User.search_by_login(username)
	if user is None:
		raise ElementNotFoundError()
	return jsonify(user), 200


@bp.route('/users/<username>', methods=['DELETE'])
@roles_accepted('warehouseman', 'admin')
def users_username_delete(username):
	"""
	Delete user.
	---
	parameters:
		- in: path
		  name: username
		  schema:
		    type: string
		    example: pepka
	responses:
	  204:
	    description: Delete is successful.
	"""
	user = User.search_by_login(username)
	if user is None:
		raise ElementNotFoundError()
	# protected_from_treasurer()
	user.delete()
	return Response(status=204)


@bp.route('/users/<username>', methods=['PATCH'])
@roles_accepted('treasurer', 'warehouseman', 'admin')
def users_username_patch(username):
	"""
	Change user data.
	---
	parameters:
		- in: path
		  name: username
		  schema:
		    type: string
		    example: pepka
		- in: body
		  name: Data
		  schema:
		    type: object
		    properties:
		      login:
		        type: string
		      password:
		        type: string
		      phone:
		        type: string
		      name:
		        type: string
		      email:
		        type: string
		      money:
		        type: integer
		      roles:
		        type: string
		      is_active:
		        type: boolean
	responses:
	  200:
	    description: Update is successful.
	"""
	user = User.search_by_login(username)
	req = request.get_json(force=True)
	if user is None:
		raise ElementNotFoundError()
	if request.method == 'PATCH' and 'admin' not in current_rolenames() and 'warehouseman' not\
			in current_rolenames():
		money = req.get('money', user.user_money)
		user.user_money = money
		db.session.commit()
	elif request.method == 'PATCH':
		login, password, name, email, phone = get_user_data(req)
		money = req.get('money', user.user_money)
		roles = req.get('roles', user.user_roles)
		is_active = req.get('is_active', user.user_isactive)
		if not none_check(6, [User.search_by_phone(phone) if phone else
		                      None,
		                      User.search_by_email(email) if email else
		                      None,
		                      User.search_by_login(
			                      login) if login else None,
		                      UserSignup.search_by_login(login) if login
		                      else None,
		                      UserSignup.search_by_email(email) if email
		                      else None,
		                      UserSignup.search_by_phone(phone) if phone
		                      else None]):
			raise ValidationError()
		if 'admin' not in current_rolenames() and 'admin' in User.search_by_login(\
				login).rolenames():  # запрет кладовщику менять админа
			raise MethodNotAllowedError()
		if login:
			user.user_login = login
		if name:
			user.user_name = name
		if password:
			user.set_password(password)
		if email:
			user.user_email = email
		if phone:
			user.user_phone = phone
		user.user_money = money
		user.user_roles = roles
		user.user_isactive = is_active
		db.session.commit()
	return Response(status=200)
