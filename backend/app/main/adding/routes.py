# from hashlib import md5
#
# from flask import redirect, render_template, url_for
# from flask_praetorian import auth_required
#
# from app import db
# from app.main.adding import bp
# from app.main.adding.forms import newCategoryForm, newItemForm, newUserForm
# from app.models import Category, Item, User
#
#
# @bp.route('/add_item', methods=['GET', 'POST'])
# @auth_required
# def add_item():
# 	categories = [i[0] for i in Category.query.with_entities(Category.category_name).all()]
# 	form = newItemForm()
# 	form.category.choices = categories
# 	if form.validate_on_submit():
# 		category_id = Category.query.filter_by(category_name=form.category.data).first().category_id
# 		newItem = Item(item_name=form.name.data, category_id=category_id,
# 		               item_weight=form.weight.data,
# 		               item_quantity_max=form.quantity.data, item_cost=form.cost.data,
# 		               item_description=form.description.data)
# 		db.session.add(newItem)
# 		db.session.commit()
# 		return redirect(url_for('main.entry'))
# 	return render_template('main/adding/new-item-page.html', form=form)
#
#
# @bp.route('/add_category', methods=['GET', 'POST'])
# @auth_required
# def add_category():
# 	form = newCategoryForm()
# 	if form.validate_on_submit():
# 		newCategory = Category(category_name=form.name.data, category_weight=form.weight.data)
# 		db.session.add(newCategory)
# 		db.session.commit()
# 		return redirect(url_for('main.entry'))
# 	return render_template('main/adding/new-category-page.html', form=form)
#
#
# @bp.route('/add_user', methods=['GET', 'POST'])
# @auth_required
# def add_user():
# 	form = newUserForm()
# 	if form.validate_on_submit():
# 		newUser = User(user_login=form.login.data,
# 		               user_password=md5(form.password.data.encode()).hexdigest(),
# 		               user_name=form.name.data, user_email=form.email.data,
# 		               user_phone=form.phone.data)
# 		newUser.add_user()
# 		return redirect(url_for('main.entry'))
# 	return render_template('main/adding/new-user-page.html', form=form)
