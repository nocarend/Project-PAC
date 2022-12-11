from flask import Response
from flask_praetorian import roles_accepted

from app.api.auth import bp
from app.models import UserSignup


@bp.route('/approve_user/<username>', methods=['POST'])
@roles_accepted('warehouseman', 'admin')
def approve_user(username):
	"""
	Approves user registration request.
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
		    example: pepe
		  required: true
	responses:
	  200:
		description: Request approved. User is created.
	  404:
	    description: User with this username didn't send a request.
	"""
	user = UserSignup.query.filter_by(user_login=username).first()
	if user:
		user.add_user()
	return Response(status=200 if user else 404)


@bp.route('/reject_user/<username>', methods=['POST'])
@roles_accepted('warehouseman', 'admin')
def reject_user(username):
	"""
	Rejects user registration request.
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
		    example: pepe
		  required: true
	responses:
	  200:
		description: Request rejected.
	  404:
	    description: User with this username didn't send a request.
	"""
	user = UserSignup.query.filter_by(user_login=username).one_or_none()
	if user:
		user.delete()
	return Response(status=200 if user else 404)
