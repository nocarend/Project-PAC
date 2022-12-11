from flask import jsonify
from flask_praetorian import auth_required, current_user, roles_accepted

from app.api.protected import bp


@bp.route("/fromAny")
@auth_required
def protected_from_any():
	"""
	Check user is he authenticate or not.
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
		description: Return  user.
	  401:
		description: Token is missing or Invalid token.
	"""
	return jsonify(user=current_user().user_name), 200


@bp.route('/fromDefault', methods=['GET'])
@roles_accepted('treasurer', 'warehouseman', 'admin')
def protected_from_default():
	"""
	Protect from unprivileged users (default).
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
		description: Return  user.
	  401:
		description: Token is missing or Invalid token, or You are stupid moron.
	"""
	return jsonify(current_user().user_name), 200


@bp.route('/fromTreasurer', methods=['GET'])
@roles_accepted('leader', 'warehouseman', 'admin')
def protected_from_treasurer():
	"""
	Protect from treasurer..
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
		description: Return  user.
	  401:
		description: Token is spasite missing or Invalid token.
	"""
	return jsonify(user=current_user().user_name), 200

# auth user
