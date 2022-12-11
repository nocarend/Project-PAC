from flask import jsonify, request, Response
from flask_praetorian.exceptions import ExpiredAccessError, InvalidTokenHeader, InvalidUserError,\
	MissingToken

from app import guard
from app.api.auth import bp
from app.api.auth.email import send_password_reset_email, send_signup_confirm_email
from app.api.auth.validators import email_validate, password_validate, phone_validate
from app.api.protected.routes import protected_from_any
from app.errors.handlers import AlreadyAuthError, ElementNotFoundError, JSONNotEnoughError,\
	ValidationError,\
	WrongTokenError
from app.helpers.functions import none_check
from app.models import User, UserSignup


@bp.route('/signup', methods=['POST'])
def signup():
	"""
	Registration with given data.
	---
	parameters:
		- in: body
		  name: Registration
		  schema:
			type: object
			required:
			  - login
			  - email
			  - name
			  - phone
			  - password
			properties:
			  login:
				type: string
			  email:
			    type: string
			  name:
			    type: string
			  phone:
			    type: string
			  password:
				type: string
	components:
	responses:
	  200:
		description: User should check email to confirm registration.
	  403:
		description: Some of unique data (username, email or phone) is already taken.
	"""
	try:
		protected_from_any()
		raise AlreadyAuthError()
	except MissingToken:
		pass
	except InvalidTokenHeader:
		pass
	except ExpiredAccessError:
		pass
	except InvalidUserError:
		pass
	req = request.get_json(force=True)
	login = req.get('login', None)
	email = req.get('email', None)
	name = req.get('name', None)
	phone = req.get('phone', None)
	password = req.get('password', None)
	if None in [login, email, name, phone, password]:
		raise JSONNotEnoughError()
	if not email_validate(email) or not phone_validate(phone) or not password_validate(password):
		raise ValidationError()
	if not none_check(6, [UserSignup.search_by_login(login), UserSignup.search_by_email(
			email), UserSignup.search_by_phone(phone),
	                      User.search_by_email(email), User.search_by_login(
			login), User.search_by_phone(phone)]):
		raise ValidationError()
	user = UserSignup(user_login=login, user_name=name,
	                  user_email=email, user_phone=phone, user_password=password)
	send_signup_confirm_email(user)
	return Response(status=200)


@bp.route('/signup/confirm/<token>', methods=['POST'])
def signup_confirm(token):
	"""
	Confirm email for registration.
	---
	parameters:
		- in: path
		  name: Token
		  description: Confirmation token.
	definitions:
	  token:
		type: string
	responses:
	  200:
		description: Confirmation successfully.
	  403:
		description: Token doesn't exist or User has already confirmed email.
	"""
	try:
		protected_from_any()
		raise AlreadyAuthError()
	except MissingToken:
		pass
	except InvalidTokenHeader:
		pass
	except ExpiredAccessError:
		pass
	except InvalidUserError:
		pass
	if UserSignup.verify_confirm_email_token(token) is None:
		raise WrongTokenError()
	return Response(status=200)


@bp.route('/login', methods=['POST'])
def login():
	"""
	Authentication via login and password.
	---
	parameters:
        - in: body
          name: Authentication
          description: Login.
          schema:
            type: object
            required:
              - login
              - password
            properties:
              login:
                type: string
              password:
                type: string
	definitions:
	  access_token:
	    type: object
	    properties:
	      access_token:
	        type: string
	  login:
	    type: string
	  password:
	    type: string
	responses:
	  200:
	    description: Token to access private pages.
	    schema:
	      $ref: '#/definitions/access_token'
	  401:
	    description: Wrong login or password.
	  403:
	    description: User is already authenticated or username | password is missing.
	"""
	try:
		protected_from_any()
		raise AlreadyAuthError()
	except MissingToken:
		pass
	except InvalidTokenHeader:
		pass
	except ExpiredAccessError:
		pass
	except InvalidUserError:
		pass
	req = request.get_json(force=True)
	login = req.get('login', None)
	password = req.get('password', None)
	if None in [login, password]:
		raise JSONNotEnoughError()
	us = User.lookup(login)
	if us:
		password = us.hashed_password(password)
	user = guard.authenticate(login, password)
	return jsonify(access_token=guard.encode_jwt_token(user)), 200


@bp.route('/refresh', methods=['GET'])
def refresh():
	"""
	Refresh access token expiration by creating a new one.
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
		description: 'New token to access private pages.
		Response example:
			{
				"access_token": "eyJhbGciOiJIUzI1NiI..."
			}'
	  401:
		description: JWT token not found in headers under 'Authorization' or Invalid token.
	  425:
		description: Access permission for token has not expired. may not refresh.
	"""
	old_token = guard.read_token_from_header()
	new_token = guard.refresh_jwt_token(old_token)
	return jsonify(access_token=new_token), 200


@bp.route('/reset_password_request', methods=['POST'])
def reset_password_request():
	"""
	Send link to user's email to reset password.
	---
	parameters:
		- in: body
		  name: Sending mail
		  schema:
			type: object
			required:
			  - email
			properties:
			  email:
				type: string
	definitions:
	  email:
		type: string
	responses:
	  200:
		description: Mail is send.
	  403:
		description: User is already authenticated or Email doesn't exist.
	"""
	try:
		protected_from_any()
		raise AlreadyAuthError()
	except MissingToken:
		pass
	except InvalidTokenHeader:
		pass
	except ExpiredAccessError:
		pass
	except InvalidUserError:
		pass
	req = request.get_json(force=True)
	email = req.get('email', None)
	if email is None:
		raise JSONNotEnoughError()
	user = User.search_by_email(email)
	if user is None:
		raise ElementNotFoundError()
	send_password_reset_email(user)
	return Response(status=200)


@bp.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
	"""
	Set new password by given link with valid token.
	---
	parameters:
		- in: path
		  name: Token
		  description: Generated token for password resetting.
		- in: body
		  name: Password
		  schema:
			type: object
			required:
			  - password
			properties:
			  password:
				type: string
	definitions:
	  token:
		type: string
	  password:
	    type: string
	responses:
	  200:
		description: Confirmation successfully.
	  403:
		description: Token doesn't exist.
	"""
	try:
		protected_from_any()
		raise AlreadyAuthError()
	except MissingToken:
		pass
	except InvalidTokenHeader:
		pass
	except ExpiredAccessError:
		pass
	except InvalidUserError:
		pass
	user = User.verify_reset_password_token(token)
	if user is None:
		raise WrongTokenError()
	req = request.get_json(force=True)
	password = req.get('password', None)
	if password is None:
		raise JSONNotEnoughError()
	if not password_validate(password):
		raise ValidationError()
	if password:
		user.set_password(password)
	return Response(status=200 if password else 404)
