from flask import current_app, render_template

from app.helpers.email_default import send_email


def send_password_reset_email(user):
	token = user.get_reset_password_token()
	send_email('[NSU] Reset Your Password',
	           sender=current_app.config['ADMINS'][0],
	           recipients=[user.user_email],
	           text_body=render_template('email/reset_password.txt',
	                                     user=user, token=token),
	           html_body=render_template('email/reset_password.html',
	                                     user=user, token=token))


def send_signup_confirm_email(user):
	token = user.get_confirmation_token()
	send_email('[NSU] Confirm Your Email', sender=current_app.config['ADMINS'][0],
	           recipients=[user.user_email],
	           text_body=render_template('email/confirm_email.txt', user=user, token=token),
	           html_body=render_template('email/confirm_email.html', user=user, token=token))
