from dataclasses import dataclass
from datetime import datetime
from hashlib import md5
from secrets import token_hex
from time import time

import flask
import jwt
from flask import current_app

from app import db, guard


# userHike = db.Table('hikes',
#                     db.Column('user_id', db.Integer, db.ForeignKey('user.user_id')),
#                     db.Column('hike_id', db.Integer, db.ForeignKey('hike.hike_id')),
#                     db.Column('role', db.Integer)  # роль, пока что только завснар
#                     )


# @login.user_loader
# def load_user(id):
#     return User.query.get(int(id))


# class Hike(db.Model):
#     hike_id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
#     hike_category = db.Column(db.Integer, index=True)
#     hike_leader_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), index=True)
#     hike_description = db.Column(db.String, index=True)
#     hike_status = db.Column(db.Integer, index=True)  # 0 - уже прошёл, 1 еще не закончились сроки
# (надо ли хранить?)
# users = db.relationship(
#     'Hike', secondary=userHike,
#     primaryjoin=(userHike.c.hike_id == hike_id),
#     backref=db.backref('userHike', lazy='dynamic'), lazy='dynamic')


class Category(db.Model):
	category_id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
	category_name = db.Column(db.String, index=True)
	category_weight = db.Column(db.Integer, index=True)
	category_datetime = db.Column(db.DateTime, default=datetime.utcnow, index=True)

	def set_name(self, name):
		self.category_name = name

	def set_weight(self, weight):
		self.category_weight = weight


@dataclass
class Item(db.Model):
	item_id: int
	item_name: str
	category_id: int
	item_weight: int
	item_quantity_current: int
	item_quantity_max: int
	item_cost: int
	item_description: str
	item_datetime: datetime

	item_id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
	item_name = db.Column(db.String(128), index=True)
	category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), index=True)
	item_weight = db.Column(db.Integer, index=True)
	item_quantity_current = db.Column(db.Integer, default=0, index=True)
	item_quantity_max = db.Column(db.Integer, index=True)
	item_cost = db.Column(db.Integer, index=True)
	item_description = db.Column(db.String(200))
	item_datetime = db.Column(db.DateTime, default=datetime.utcnow, index=True)

	def get_avatar(self, size):
		digest = md5(str(self.item_id).upper().encode('utf-16')).hexdigest()
		return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

	def show_users(self):
		return flask.jsonify(ItemInUse.query.join(
			User, ItemInUse.item_id == self.item_id).filter(
			ItemInUse.user_id == User.user_id).order_by(
			ItemInUse.use_datetime.desc()).all()).get_json()


@dataclass
class ItemInUse(db.Model):
	use_id: int
	user_id: int
	item_id: int
	item_quantity: int
	use_description: str
	use_datetime: datetime

	use_id = db.Column(db.Integer, primary_key=True, index=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), index=True)
	item_id = db.Column(db.Integer, db.ForeignKey('item.item_id'), index=True)
	item_quantity = db.Column(db.Integer, index=True)
	use_description = db.Column(db.String(150))
	use_datetime = db.Column(db.DateTime, index=True)

	def get_item(self):
		return Item.query.filter_by(item_id=self.item_id).first()

	def get_user(self):
		return User.query.filter_by(user_id=self.user_id).first()


#
# def __repr__(self):
#     return '<ItemsUse {}>'.format(self.item_id)


# Class for User table
@dataclass
class User(db.Model):
	user_id: int
	user_login: str
	user_password: str
	user_name: str
	user_email: str
	user_phone: str
	user_money: int
	user_roles: str
	user_status: int
	user_isactive: bool
	user_datetime: datetime

	user_id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
	user_login = db.Column(db.String(150), unique=True, index=True)
	user_password = db.Column(db.String(128))
	user_name = db.Column(db.String(120), index=True)
	user_email = db.Column(db.String(120), unique=True, index=True)
	user_phone = db.Column(db.String(9), index=True)
	user_money = db.Column(db.Integer, default=0)
	user_roles = db.Column(db.Text, default="")
	user_status = db.Column(db.Integer, default=0)  # user, elder or nothing
	user_isactive = db.Column(db.Boolean, default=True, server_default='true', index=True)
	user_datetime = db.Column(db.DateTime, default=datetime.utcnow, index=True)

	@property
	def identity(self):
		return self.user_id

	@property
	def rolenames(self):
		"""
		*Required Attribute or Property*

		flask-praetorian requires that the user class has a ``rolenames`` instance
		attribute or property that provides a list of strings that describe the roles
		attached to the user instance
		"""
		try:
			return self.user_roles.split(",")
		except Exception:
			return []

	@property
	def password(self):
		"""
		*Required Attribute or Property*

		flask-praetorian requires that the user class has a ``password`` instance
		attribute or property that provides the hashed password assigned to the user
		instance
		"""
		return self.user_password

	@classmethod
	def lookup(cls, username):
		"""
		*Required Method*

		flask-praetorian requires that the user class implements a ``lookup()``
		class method that takes a single ``username`` argument and returns a user
		instance if there is one that matches or ``None`` if there is not.
		"""
		return cls.query.filter_by(user_login=username).one_or_none()

	@classmethod
	def identify(cls, id):
		"""
		*Required Method*

		flask-praetorian requires that the user class implements an ``identify()``
		class method that takes a single ``id`` argument and returns user instance if
		there is one that matches or ``None`` if there is not.
		"""
		return cls.query.get(id)

	def is_valid(self):
		return self.user_isactive

	# hikes = db.relationship(
	#     'User', secondary=userHike,
	#     primaryjoin=(userHike.c.user_id == user_id),
	#     backref=db.backref('userHike', lazy='dynamic'), lazy='dynamic')

	def add_user(self):
		db.session.add(self)
		a_user = User.query.filter_by(user_login=self.user_login).first()
		salt = UserSalt(user_id=a_user.user_id, salt=token_hex(64))
		db.session.add(salt)
		self.set_password(a_user.user_password)
		db.session.commit()

	def get_reset_password_token(self, expires_in=600):
		return jwt.encode({'reset_password': self.user_id, 'exp': time() + expires_in},
		                  current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])[
				'reset_password']
		except:
			return
		return User.query.get(id)

	def set_password(self, password):
		self.user_password = guard.hash_password(self.hashed_password(password))

	# db.commit()

	def hashed_password(self, password):
		salt = UserSalt.query.filter_by(user_id=self.user_id).first().salt
		return md5(password.encode()).hexdigest() + salt

	# def check_password(self, password):
	#     return check_password_hash(self.user_password,
	#                                guard.hash_password(self.hashed_password(password)))

	def get_id(self):
		return self.user_id

	def get_isactive(self):
		return self.user_isactive

	def show_items(self):
		return flask.jsonify(ItemInUse.query.join(
			Item, ItemInUse.item_id == Item.item_id).filter(
			ItemInUse.user_id == self.user_id).order_by(
			ItemInUse.use_datetime.desc()).all()).get_json()


# def item_take:

# def item_return:


class UserSignup(db.Model):
	signup_id = db.Column(db.Integer, primary_key=True, index=True)
	user_login = db.Column(db.String(150), unique=True, index=True)
	user_password = db.Column(db.String(128))
	user_name = db.Column(db.String(120), index=True)
	user_email = db.Column(db.String(120), unique=True, index=True)
	user_phone = db.Column(db.String(9), index=True)
	signup_datetime = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # удалить

	def set_password(self, password):
		self.user_password = password  # не будем хранить соль, если кто-то будет аппрувить

	# заявку тогда только соль создастся

	def add_user(self):
		user = User(user_login=self.user_login, user_password=self.user_password,
		            user_name=self.user_name, user_email=self.user_email,
		            user_phone=self.user_phone)
		user.add_user()
		db.session.delete(self)
		db.session.commit()

	def delete_user(self):
		db.session.delete(self)
		db.session.commit()


class UserSalt(db.Model):
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True, index=True)
	salt = db.Column(db.Text(150))
