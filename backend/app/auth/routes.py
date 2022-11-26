import requests
from flask import flash, make_response, redirect, render_template, url_for
from flask_praetorian import auth_required

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, ResetPasswordForm, ResetPasswordRequestForm, SignUpForm
from app.models import UserSignup


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
	# if current_user.is_authenticated:
	#     return redirect(url_for('main.entry'))
	form = SignUpForm()
	if form.validate_on_submit():
		userSignup = UserSignup(user_login=form.login.data, user_name=form.name.data,
		                        user_email=form.email.data, user_phone=form.phone.data)
		userSignup.set_password(form.password.data)
		db.session.add(userSignup)
		db.session.commit()
		return render_template('auth/signup-result.html')
	return render_template('auth/signup.html', title='Register', form=form)


@bp.route('/login', methods=['GET', 'POST'])  # на реакт перенести
def login():
	# if current_user.is_authenticated:
	#     return redirect(url_for('main.entry'))
	form = LoginForm()
	if form.validate_on_submit():
		# user = User.query.filter_by(user_login=form.login.data).first()
		# if user is None or not user.check_password(
		#         form.password.data) or user.get_isactive() == False:  # user isactive
		#     flash('Invalid login or password')
		#     return redirect(url_for('auth.login'))
		# login_user(user, remember=form.remember_me.data)
		# next_page = request.args.get('next')
		# if not next_page or url_parse(next_page).netloc != '':
		#     next_page = url_for('main.entry')
		res = requests.post('http://127.0.0.1:5000' + url_for('api.auth.login'),
		                    json={
			                    "username": f"{form.login.data}",
			                    "password": f"{form.password.data}"
			                    })
		if res.status_code == 200:
			red = make_response(redirect(url_for('main.entry')))
			red.set_cookie("access_token", value=res.json()["access_token"], httponly=True)
			return red
		return redirect(url_for('auth.login'))
	return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
	# if current_user.is_authenticated:
	#     return redirect(url_for('main.entry'))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		requests.post('http://127.0.0.1:5000' + url_for('api.email.reset_password'),
		              json={"email": f"{form.email.data}"})
		flash('Check your email for the instructions to reset your password')
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password_request.html',
	                       title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	# if current_user.is_authenticated:
	# 	return redirect(url_for('main.entry'))
	req = requests.post('http://127.0.0.1:5000' + url_for('api.auth.verify_password_token'),
	                    json={"token": f"{token}"})
	if req.status_code == 404:
		return redirect(url_for('main.index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		requests.post('http://127.0.0.1:5000' + url_for('api.auth.set_new_password'),
		              json={"token": f"{token}", "password": form.password.data})
		flash('Your password has been reset.')
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html', form=form)


@bp.route('/logout')
@auth_required
def logout():
	# logout_user()
	return redirect(url_for('main.index'))
