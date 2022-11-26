import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

import flask_cors
import flask_praetorian
from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db: SQLAlchemy = SQLAlchemy()
migrate = Migrate()
mail = Mail()
cors = flask_cors.CORS()
guard = flask_praetorian.Praetorian()


def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(config_class)
	db.init_app(app)
	migrate.init_app(app, db)
	mail.init_app(app)
	cors.init_app(app)
	from app.models import User
	guard.init_app(app, User)  # authentication

	from app.api import bp as api_bp

	from app.api.adding import bp as api_adding_bp
	api_bp.register_blueprint(api_adding_bp, url_prefix='/adding')
	from app.api.auth import bp as api_auth_bp
	api_bp.register_blueprint(api_auth_bp, url_prefix='/auth')
	from app.api.email import bp as api_email_bp
	api_bp.register_blueprint(api_email_bp, url_prefix='/email')
	from app.api.protected import bp as api_protected_bp
	api_bp.register_blueprint(api_protected_bp, url_prefix='/protected')

	app.register_blueprint(api_bp, url_prefix='/api')

	from app.errors import bp as errors_bp
	app.register_blueprint(errors_bp)

	from app.auth import bp as auth_bp
	app.register_blueprint(auth_bp, url_prefix='/auth')

	from app.main import bp as main_bp
	from app.main.adding import bp as main_adding_bp
	main_bp.register_blueprint(main_adding_bp)

	app.register_blueprint(main_bp)

	if not app.debug and not app.testing:
		if app.config['MAIL_SERVER']:
			auth = None
			if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
				auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
			secure = None
			if app.config['MAIL_USE_TLS']:
				secure = ()
			mail_handler = SMTPHandler(
				mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
				fromaddr='no-reply@' + app.config['MAIL_SERVER'],
				toaddrs=app.config['ADMINS'], subject='nsu Failure',
				credentials=auth, secure=secure)
			mail_handler.setLevel(logging.ERROR)
			app.logger.addHandler(mail_handler)
		if app.config['LOG_TO_STDOUT']:  # for heroku
			stream_handler = logging.StreamHandler()
			stream_handler.setLevel(logging.INFO)
			app.logger.addHandler(stream_handler)
		else:
			if not os.path.exists('logs'):
				os.mkdir('logs')
			file_handler = RotatingFileHandler('logs/nmm.log', maxBytes=10240, backupCount=10)
			file_handler.setFormatter(logging.Formatter(
				'%(asctime)s %(levelname)s: %(message)s '
				'[in %(pathname)s:%(lineno)d]'))
			file_handler.setLevel(logging.INFO)
			app.logger.addHandler(file_handler)

		app.logger.setLevel(logging.INFO)
		app.logger.info('nmm startup')
	return app


from app import models
