from dataclasses import dataclass
from datetime import datetime
from hashlib import md5
from secrets import token_hex
from time import time

import jwt
from flask import current_app
from flask_praetorian import current_user_id
# from sqlalchemy_serializer import SerializerMixin

from app import db, guard
from app.errors.handlers import ElementNotFoundError, StockError, ValidationError
from app.helpers.functions import none_check


# userHike = db.Table('hikes',
#                     db.Column('user_id', db.Integer, db.ForeignKey('user.user_id')),
#                     db.Column('hike_id', db.Integer, db.ForeignKey('hike.hike_id')),
#                     db.Column('role', db.Integer)  # роль, пока что только завснар
#                     )
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

@dataclass
class Category(db.Model):
	category_id: int
	category_name: str
	category_weight: int
	# category_datetime: datetime
	# items: list
	category_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True,
	                        index=True)
	category_name = db.Column(db.String, index=True)
	category_weight = db.Column(db.Integer, default=None, index=True)
	category_datetime = db.Column(db.DateTime, default=datetime.utcnow, index=True)

	@staticmethod
	def search_by_name(name):
		return Category.query.filter_by(category_name=name).first()

	@staticmethod
	def search_by_id(id):
		return Category.query.filter_by(category_id=id).first()

	# @property
	def items(self):
		return Item.search_by_category(self.category_id).all()


@dataclass
class Item(db.Model):
	item_id: int
	item_name: str
	# category_id: int
	category: Category
	item_weight: int
	item_quantity_current: int
	item_quantity_max: int
	item_cost: int
	item_description: str
	# item_datetime: datetime
	# users:str
	avatar: str

	serialize_rules = ('-category.items', 'item_datetime', 'category_id')

	item_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True, index=True)
	item_name = db.Column(db.String(128), index=True)
	category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), index=True)
	item_weight = db.Column(db.Integer, default=None, index=True)
	item_quantity_current = db.Column(db.Integer, default=0, index=True)
	item_quantity_max = db.Column(db.Integer, default=0, index=True)
	item_cost = db.Column(db.Integer, default=None, index=True)
	item_description = db.Column(db.String(200), default=None)
	item_datetime = db.Column(db.DateTime, default=datetime.utcnow, index=True)
	category = db.relationship('Category', backref='category', lazy=True)

	@property
	def avatar(self, size=50):
		digest = md5(str(self.item_id).upper().encode('utf-16')).hexdigest()
		return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

	@property
	def category(self):
		return Category.search_by_id(self.category_id)

	@staticmethod
	def getAll():
		res = []
		for item in Item.query.all():
			res += item.to_dict()
		return res

	@staticmethod
	def search_by_id(item_id):
		return Item.query.filter_by(item_id=item_id).first()

	@staticmethod
	def search_by_name_and_category(item, category):
		return Item.query.filter_by(item_name=item, category_id=category)

	@staticmethod
	def search_by_category(category_id):
		return Item.query.filter(category_id=category_id)

	# @property
	def users(self):
		return ItemInUse.query.join(
			User, ItemInUse.item_id == self.item_id).filter(
			ItemInUse.user_id == User.user_id).order_by(
			ItemInUse.use_datetime.desc()).all()

	def add(self):
		if not none_check(1, [self.search_by_item_and_category(self.item_name, self.category_id)]):
			raise ValidationError()
		db.session.add(self)
		db.session.commit()

	def delete(self):
		users = ItemInUse.search_by_item(self.item_id)
		for x in users:
			x.delete()
		db.session.delete(self)
		db.session.commit()

	def book(self, user_id, count, confirm):
		if self.item_quantity_current - count < 0:
			raise StockError()
		self.item_quantity_current -= count
		db.session.commit()
		itemRecord = ItemInUse(user_id=user_id, item_id=self.item_id,
		                       item_quantity=count, is_confirm=confirm)
		itemRecord.add()


# Class for User table
@dataclass
class User(db.Model):
	user_id: int
	user_login: str
	# user_password: str
	user_name: str
	user_email: str
	user_phone: str
	user_money: int
	user_roles: str
	user_isactive: bool
	# user_datetime: datetime
	items: str

	serialize_rules = ('-items.user',)

	user_id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
	user_login = db.Column(db.String(150), unique=True, index=True)
	user_password = db.Column(db.String(128))
	user_name = db.Column(db.String(120), index=True)
	user_email = db.Column(db.String(120), unique=True, index=True)
	user_phone = db.Column(db.String(9), index=True)
	user_money = db.Column(db.Integer, default=0)
	user_roles = db.Column(db.Text, default="")
	user_isactive = db.Column(db.Boolean, default=True, server_default='true', index=True)
	user_datetime = db.Column(db.DateTime, default=datetime.utcnow, index=True)

	@property
	def items(self):
		return ItemInUse.query.join(
			Item, ItemInUse.item_id == Item.item_id).filter(
			ItemInUse.user_id == self.user_id).order_by(
			ItemInUse.use_datetime.desc()).all()

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

	@staticmethod
	def search_by_login(login):
		return User.query.filter_by(user_login=login).first()

	@staticmethod
	def search_by_phone(phone):
		return User.query.filter_by(user_phone=phone).first()

	@staticmethod
	def search_by_email(email):
		return User.query.filter_by(user_email=email).first()

	@staticmethod
	def search_by_id(id):
		return User.query.filter_by(user_id=id).first()

	def add_salt(self):
		salt = UserSalt(user_id=self.user_id, salt=token_hex(64))
		db.session.add(salt)
		db.session.commit()

	def add(self):
		if not none_check(6, [self.search_by_phone(
				self.user_phone),
			self.search_by_login(self.user_login),
			self.search_by_email(
				self.user_email), UserSignup.search_by_email(
				self.user_email), UserSignup.search_by_login(self.user_login),
			UserSignup.search_by_phone(self.user_phone)]):
			raise ValidationError()
		db.session.add(self)
		a_user = User.search_by_login(self.user_login)
		self.add_salt()
		self.set_password(a_user.user_password)
		db.session.commit()

	def delete(self):
		salt = UserSalt.search_by_id(self.user_id)
		items = ItemInUse.search_by_user(self.user_id)
		for x in items:
			x.delete()
		db.session.delete(self)
		db.session.delete(salt)
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
			return None
		return User.query.get(id)

	def set_password(self, password):
		self.user_password = guard.hash_password(self.hashed_password(password))
		db.session.commit()

	def hashed_password(self, password):
		salt = UserSalt.query.filter_by(user_id=self.user_id).first().salt
		return md5(password.encode()).hexdigest() + salt


# def item_take:

# def item_return:

@dataclass
class UserSignup(db.Model):
	signup_id: int
	user_login: str
	# user_password: str
	user_name: str
	user_email: str
	user_phone: str
	signup_datetime: datetime

	signup_id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
	user_login = db.Column(db.String(150), unique=True, index=True)
	user_password = db.Column(db.String(128))
	user_name = db.Column(db.String(120), index=True)
	user_email = db.Column(db.String(120), unique=True, index=True)
	user_phone = db.Column(db.String(9), unique=True, index=True)
	signup_datetime = db.Column(db.DateTime, default=datetime.utcnow, index=True)

	@staticmethod
	def search_by_id(id):
		return UserSignup.query.filter_by(signup_id=id).first()

	@staticmethod
	def search_by_login(login):
		return UserSignup.query.filter_by(user_login=login).first()

	@staticmethod
	def search_by_email(email):
		return UserSignup.query.filter_by(user_email=email).first()

	@staticmethod
	def search_by_phone(phone):
		return UserSignup.query.filter_by(user_phone=phone).first()

	def add(self):
		if not none_check(2, [User.search_by_email(self.user_email), self.search_by_email(
				self.user_email)]):
			raise ValidationError()
		db.session.add(self)
		db.session.commit()

	def add_user(self):
		user = User(user_login=self.user_login, user_password=self.user_password,
		            user_name=self.user_name, user_email=self.user_email,
		            user_phone=self.user_phone)
		db.session.add(user)
		db.session.commit()
		a_user = User.search_by_login(self.user_login)
		a_user.add_salt()
		a_user.set_password(self.user_password)
		self.delete()
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def get_confirmation_token(self, expires_in=60 * 60 * 24 * 7):
		return jwt.encode({
			'login': self.user_login, "password": self.user_password,
			"name":  self.user_name,
			"email": self.user_email, "phone": self.user_phone, 'exp': time() + expires_in
			},
			current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

	@staticmethod
	def verify_confirm_email_token(token):
		try:
			data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
			user = UserSignup(user_login=data["login"], user_password=data["password"],
			                  user_name=data["name"], user_email=data["email"], user_phone=data[
					"phone"])
			user.add()
			return True
		except:
			return None


@dataclass
class UserSalt(db.Model):
	user_id: int
	salt: str

	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True, index=True)
	salt = db.Column(db.Text(150))

	@staticmethod
	def search_by_id(id):
		return UserSalt.query.filter_by(user_id=id).first()


@dataclass
class ItemInUse(db.Model):
	# use_id: int
	user_id: int
	# item_id: int
	item: Item
	# user: User
	item_quantity: int
	is_confirm: bool
	use_description: str
	use_datetime: datetime

	use_id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), index=True)
	item_id = db.Column(db.Integer, db.ForeignKey('item.item_id'), index=True)
	item_quantity = db.Column(db.Integer, index=True, default=1)
	is_confirm = db.Column(db.Boolean, index=True, default=False)
	use_description = db.Column(db.String(150), default="")
	use_datetime = db.Column(db.DateTime, default=datetime.utcnow(), index=True)

	# searching item by id
	@property
	def item(self):
		return Item.query.filter_by(item_id=self.item_id).first()

	@property
	def user(self):
		return User.query.filter_by(user_id=self.user_id).first()

	@staticmethod
	def search_by_use_id(use_id):
		return ItemInUse.query.filter_by(use_id=use_id).first()

	@staticmethod
	def search_by_user(user_id, all=True):
		return ItemInUse.query.filter_by(user_id=user_id).all() if all else\
			ItemInUse.query.filter_by(user_id=user_id, is_confirm=True).all()

	@staticmethod
	def search_by_item(item_id, all=True):
		return ItemInUse.query.filter_by(item_id=item_id).all() if all else\
			ItemInUse.query.filter_by(item_id=item_id, is_confirm=True).all()

	def unbook(self, count):
		item = self.item()
		if count is None or count > self.item_quantity or count <= 0:
			raise StockError()
		if self.user_id != current_user_id() or self.is_confirm == True:
			raise ElementNotFoundError()
		item.item_quantity_current += count
		if count == self.item_quantity:
			self.delete()
		else:
			self.item_quantity -= count
		db.session.commit()

	def return_(self, quantity=1):
		if quantity > self.item_quantity or quantity <= 0:
			raise StockError()
		item = self.item()
		item.item_quantity_current += quantity
		if quantity == self.item_quantity:
			self.delete()
		else:
			self.item_quantity -= quantity
		db.session.commit()

	def add(self):
		db.session.add(self)
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()
