from flask import render_template
from flask_praetorian import auth_required

from app.main import bp
from app.models import Item, User


@bp.route('/')
@bp.route('/index')
def index():
	return render_template('index.html')  # возвращаю страницу, рендерю хтмл


@bp.route('/entry')
@auth_required
def entry():
	return render_template('entry.html')


@bp.route('/user/<user_login>')  # только для админ ролей, кладовщик и т д
@auth_required
def user(user_login):
	user = User.query.filter_by(user_login=user_login).first_or_404()
	return render_template('user.html', user=user)  # item_user


@bp.route('/item/<item_id>')
@auth_required
def item(item_id):
	item = Item.query.filter_by(item_id=item_id).first_or_404()
	return render_template('item.html', item=item)

# edit_profile
