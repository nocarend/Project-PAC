from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app.models import User, UserSignup


class LoginForm(FlaskForm):
	login = StringField('Login', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')


class SignUpForm(FlaskForm):
	login = StringField('Login', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	name = StringField('ФИО', validators=[DataRequired()])
	phone = StringField('Номер телефона', validators=[DataRequired()])  # Regexp later
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	description = StringField("Описание заявки")
	submit = SubmitField('Send a request')

	def validate_login(self, user_login):
		sign = UserSignup.query.filter_by(user_login=user_login.data).first()
		user = User.query.filter_by(user_login=user_login.data).first()
		if user is not None or sign is not None:
			raise ValidationError('Please use a different username.')

	def validate_email(self, email):
		sign = UserSignup.query.filter_by(user_email=email.data).first()
		user = User.query.filter_by(user_email=email.data).first()
		if user is not None or sign is not None:
			raise ValidationError('Please use a different email address.')

	def validate_phone(self, phone):
		sign = UserSignup.query.filter_by(user_phone=phone.data).first()
		user = User.query.filter_by(user_phone=phone.data).first()
		if user is not None or sign is not None:
			raise ValidationError('Please use a different phone number.')


class ResetPasswordRequestForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Request Password Reset')
