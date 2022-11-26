from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app.models import Category, Item, User, UserSignup


class newItemForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	category = SelectField('Category', validators=[DataRequired()])
	weight = IntegerField('Weight (grams)', validators=[DataRequired()])
	quantity = IntegerField("Item's quantity", validators=[DataRequired()])
	cost = IntegerField("Item's cost", validators=[DataRequired()])
	description = StringField('Description')
	submit = SubmitField('Confirm')

	def validate_name(self, name):
		item = Item.query.filter_by(item_name=name.data).first()
		if item is not None:
			raise ValidationError("Please use a different item's name")

	def validate_weight(self, weight):
		if weight.data < 0:
			raise ValidationError("Weight must be greater than 0")

	def validate_quantity(self, quantity):
		if quantity.data < 0:
			raise ValidationError("Quantity must be greater than 0")

	def validate_cost(self, cost):
		if cost.data < 0:
			raise ValidationError("Cost must be greater that 0")


class newUserForm(FlaskForm):
	login = StringField('Login', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	name = StringField('ФИО', validators=[DataRequired()])
	phone = StringField('Номер телефона', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	# status=SelectField('Role') # добавить юзера с указанной ролью
	submit = SubmitField('Confirm')

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


class newCategoryForm(FlaskForm):
	name = StringField("Category's name", validators=[DataRequired()])
	weight = IntegerField('Default weight in category', validators=[DataRequired()])
	submit = SubmitField('Confirm')

	def validate_name(self, name):
		category = Category.query.filter_by(category_name=name.data).first()
		if category is not None:
			raise ValidationError("Please use a different category's name")

	def validate_weight(self, weight):
		if weight.data < 0:
			raise ValidationError("Weight must be greater than 0")
