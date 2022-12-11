from flask import jsonify

from app import db
from app.errors import bp


class MoneyError(Exception):
	description = "Money is not enough."
	status_code = 403


class StockError(Exception):
	description = "Some problem with stock."
	status_code = 403


class AlreadyAuthError(Exception):
	description = "Authenticated users cannot access this link."
	status_code = 403


class WrongTokenError(Exception):
	description = "Fail to identify token."
	status_code = 403


class ValidationError(Exception):
	description = "Some unique data already exists in database. Or missing data format."
	status_code = 403


class MethodNotAllowedError(Exception):
	description = "You don't have needed rights or method not implemented."
	status_code = 405


class JSONNotEnoughError(Exception):
	description = "Not enough arguments in request."
	status_code = 403


class ElementNotFoundError(Exception):
	description = "Cannot find element by given identificator."
	status_code = 403


@bp.app_errorhandler(MoneyError)
def not_enough_money(error):
	return jsonify(error=error.description), error.status_code


@bp.app_errorhandler(StockError)
def not_enough_items(error):
	return jsonify(error=error.description), error.status_code


@bp.app_errorhandler(AlreadyAuthError)
def alreadyAuthError(error):
	return jsonify(error=error.description), error.status_code


@bp.app_errorhandler(WrongTokenError)
def tokenError(error):
	return jsonify(error=error.description), error.status_code


@bp.app_errorhandler(ValidationError)
def validationError(error):
	return jsonify(error=error.description), error.status_code


@bp.app_errorhandler(MethodNotAllowedError)
def method_not_allowed(error):
	return jsonify(error=error.description), error.status_code


@bp.app_errorhandler(404)
def not_found_error(error):
	return jsonify(error="Path is not found."), 404


@bp.app_errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return jsonify(error="Unknown server error."), 500


@bp.app_errorhandler(JSONNotEnoughError)
def not_enough_error(error):
	return jsonify(error=error.description), error.status_code


@bp.app_errorhandler(ElementNotFoundError)
def element_not_found_error(error):
	return jsonify(error=error.description), error.status_code
