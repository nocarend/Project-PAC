import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY')

	# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
	# SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL')
	# os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	MAIL_USE_TLS = 1
	MAIL_MAX_EMAILS = 1000
	MAIL_SERVER = os.environ.get('MAIL_SERVER')
	MAIL_PORT = os.environ.get('MAIL_PORT')
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	ADMINS = os.environ.get('ADMINS')

	JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
	JWT_ACCESS_LIFESPAN = {"hours": 24}
	JWT_REFRESH_LIFESPAN = {"days": 30}

	LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')  # for heroku
