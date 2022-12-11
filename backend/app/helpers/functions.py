def none_check(n: int, array):
	return n * [None] == array


def get_user_data(req):
	user_login = req.get('login', None)
	user_password = req.get('password', None)
	user_name = req.get('name', None)
	user_email = req.get('email', None)
	user_phone = req.get('phone', None)
	return user_login, user_password, user_name, user_email, user_phone


def get_item_data(req):
	item_name = req.get('item', None)
	category_name = req.get('category_name', None)
	item_weight = req.get('weight', None)
	item_quantity_current = req.get('current', None)
	item_quantity_max = req.get('max', None)
	item_cost = req.get('cost', None)
	item_description = req.get('description', None)
	return item_name, category_name, item_weight, item_quantity_current, item_quantity_max,\
	       item_cost, item_description
