import re


def email_validate(email):
	regex = re.compile('([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
	return re.fullmatch(regex, email)


def phone_validate(phone):
	regex = re.compile('[\\+]7(\\d{10})')
	return re.fullmatch(regex, phone)


def password_validate(password: str):
	return len(password) > 5
