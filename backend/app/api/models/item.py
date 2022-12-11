from flask import jsonify, request, Response
from flask_praetorian import auth_required, current_rolenames, current_user, current_user_id,\
	roles_accepted

from app import db
from app.api.models import bp
from app.errors.handlers import ElementNotFoundError, JSONNotEnoughError, MoneyError,\
	ValidationError
from app.helpers.functions import get_item_data, none_check
from app.models import Category, Item, ItemInUse


@bp.route('/items', methods=['GET'])
@auth_required
def items_get():
	"""
	Return all items in stock.
	---
	parameters:
		- in: header
		  name: Authorization
		  schema:
			type: string
			example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
		  required: true
	responses:
	  200:
		description: JSON array with all items.
		schema:
		  type: array
		  items:
		    type: object
		    properties:
		      avatar:
		        type: string
		      item_id:
		        type: integer
		      item_name:
		        type: string
		      category:
		        type: object
		        properties:
		          category_id:
		            type: integer
		          category_name:
		            type: string
		          category_weight:
		            type: integer
		      item_weight:
		        type: integer
		      item_quantity_current:
		        type: integer
		      item_quantity_max:
		        type: integer
		      item_cost:
		        type: integer
		      item_description:
		        type: string
		      item_datetime:
		        type: string
	"""
	items = Item.query.all()
	return jsonify(items=items), 200


@bp.route('/items', methods=['POST'])
@roles_accepted('warehouseman', 'admin')
def items_post():
	"""
	Creates a new item. Allowed only for warehouseman and admin roles.
	---
	parameters:
		- in: header
		  name: Authorization
		  schema:
			type: string
			example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
		  required: true
		- in: body
		  name: Data
		  schema:
		    type: object
		    properties:
		      name:
		        type: string
		      category_name:
		        type: string
		      weight:
		        type: integer
		      current:
		        type: integer
		        description: current quantity
		      max:
		        type: integer
		        description: max quantity
		      cost:
		        type: integer
		      description:
		        type: string
	responses:
	  200:
		description: Item is created.
	  403:
	    description: Not enough arguments or Some unique data already exists in database.
	"""
	req = request.get_json(force=True)
	name, category_name, weight, current, maxx, cost, description = get_item_data(req)
	if None in [name, category_name]:
		raise JSONNotEnoughError()
	newItem = Item(item_name=name, category_id=Category.search_by_name(category_name).category_id)
	if weight:
		newItem.item_weight = weight
	if current:
		newItem.item_quantity_current = current
	if maxx:
		newItem.item_quantity_max = maxx
	if cost:
		newItem.item_cost = cost
	if description:
		newItem.item_description = description
	newItem.add()
	return Response(status=201)


@bp.route('/items/<item_id>', methods=['GET'])
@auth_required
def items_item_id_get(item_id):
	"""
	Get element by its id. If you are warehouseman you can see some additional data.
	---
	parameters:
		- in: header
		  name: item_id
		  schema:
			type: integer
			example: 13
		  required: true
	responses:
	  200:
	    description: Info about item.
	    schema:
	      type: object
	      properties:
	        avatar:
	          type: string
	        category:
	          type: object
	          properties:
	            category_id:
	              type: integer
	            category_name:
	              type: string
	            category_weight:
	              type: integer
	        item_cost:
	          type: integer
	        item_description:
	          type: string
	        item_id:
	          type: integer
	        item_name:
	          type: string
	        item_quantity_current:
	          type: integer
	        item_quantity_max:
	          type: integer
	        item_weight:
	          type: integer
	  403:
	    description: There are no item with given id.
	"""
	item = Item.search_by_id(item_id)
	if item is None:
		raise ElementNotFoundError()
	return (jsonify(item=item) if 'warehouseman' not in current_rolenames() and 'admin' not in\
	                              current_rolenames() else jsonify(item=item,
	                                                               usersRecords=item.users())), 200


@bp.route('/items/<item_id>', methods=['DELETE'])
@roles_accepted('warehouseman', 'admin')
def items_item_id_delete(item_id):
	"""
	Delete given item.
	---
	parameters:
		- in: path
		  name: item_id
		  schema:
		    type: integer
	responses:
		204:
		  description: Deletion is successful.
		403:
		  description:
		    Item is not found.
	"""
	item = Item.search_by_id(item_id)
	if item is None:
		raise ElementNotFoundError()
	item.delete()
	return Response(status=204)


@bp.route('/items/<item_id>', methods=['PATCH'])
@roles_accepted('warehouseman', 'admin')
def items_item_id_patch(item_id):
	"""
	Update item's info.
	---
	parameters:
		- in: path
		  name: item_id
		  schema:
		    type: integer
		- in: body
		  name: data
		  schema:
		    type: object
		    properties:
		      name:
		        type: string
		      category_name:
		        type: string
		      weight:
		        type: integer
		      current:
		        type: integer
		      max:
		        type: integer
		      cost:
		        type: integer
		      description:
		        type: string
	responses:
	  200:
	    description: Update is successful.
	  403:
	    description: Item is not found.
	"""
	item = Item.search_by_id(item_id)
	if item is None:
		raise ElementNotFoundError()
	req = request.get_json(force=True)
	name, category_name, weight, current, maxx, cost, description = get_item_data(req)
	category_id = None
	if category_name:
		category_id = Category.search_by_name(category_name)
	if name and category_name is None:
		category_id = item.category_id
	elif category_name and name is None:
		name = item.item_name
	if not none_check(1, [Item.search_by_name_and_category(name, category_id)]):
		raise ValidationError()
	if name:
		item.item_name = name
	if category_id:
		item.category_id = category_id
	if weight:
		item.item_weight = weight
	if current:
		item.item_quantity_current = current
	if maxx:
		item.item_quantity_max = maxx
	if cost:
		item.item_cost = cost
	if description:
		item.item_description = description
	db.session.commit()
	return Response(status=200)


@bp.route('/items/use/book', methods=['POST'])
@auth_required
def item_book():
	"""
	Book a list of items.
	---
	parameters:
		- in: body
		  name: items
		  schema:
		    type: object
		    properties:
		      items:
		        type: array
		        items:
		          type: object
		          properties:
		            item_id:
		              type: integer
		            quantity:
		              type: integer
	responses:
	  200:
	    description: All items was booked.
	  403:
	    description: "User don't have enough money or Is given wrong item_id or Not enough
	    arguments in JSON body."
	"""
	req = request.get_json(force=True)
	items = req.get('items', None)
	if items is None:
		raise JSONNotEnoughError()
	for i in items:
		item = Item.search_by_id(i['item_id'])
		count = i['quantity']
		if item is None:
			raise ElementNotFoundError()
		if count is None:
			raise JSONNotEnoughError()
		if 'warehouseman' in current_rolenames() or 'admin' in current_rolenames():
			item.book(current_user_id(), count, True)
			continue
		if current_user().user_money <= 0:
			raise MoneyError()
		item.book(current_user_id(), count, False)
	return Response(status=200)


# work
@bp.route('/items/use/unbook', methods=['POST'])
@auth_required
def item_unbook():
	"""
	Unbook a list of items.
	---
	parameters:
		- in: body
		  name: useIds
		  schema:
			type: object
			properties:
			  useIds:
			    type: array
			    items:
			      type: object
			      properties:
			        use_id:
			          type: integer
			        quantity:
			          type: integer
	responses:
	  200:
	    description: Unbooking is successful.
	  403:
	    description: "Given wrong use_id or wrong quantity, or You are trying to access item that
	    doesn't belong to you."
	"""
	req = request.get_json(force=True)
	useIds = req.get('useIds', None)
	if useIds is None:
		raise JSONNotEnoughError()
	for i in useIds:
		itemRecord = ItemInUse.search_by_use_id(i['use_id'])
		count = i['quantity']
		if itemRecord is None:
			raise ElementNotFoundError()
		if count is None:
			raise JSONNotEnoughError()
		itemRecord.unbook(count)
	return Response(status=200)


# work
@bp.route('/items/use/return', methods=['POST'])
@roles_accepted('warehouseman', 'admin')
def item_return():
	"""
	Return an item.
	---
	parameters:
		- in: body
		  name: useIds
		  schema:
			type: object
			properties:
			  useIds:
			    type: array
			    items:
			      type: object
			      properties:
			        use_id:
			          type: integer
			        quantity:
			          type: integer
	responses:
	  200:
	    description: Return is successful.
	  403:
	    description: "Given wrong use_id or wrong quantity."
	"""
	req = request.get_json(force=True)
	useIds = req.get('useIds', None)
	if useIds is None:
		raise JSONNotEnoughError()
	for i in useIds:
		itemRecord = ItemInUse.search_by_use_id(i['use_id'])
		count = i['quantity']
		if itemRecord is None:
			raise ElementNotFoundError()
		if count is None:
			raise JSONNotEnoughError()
		itemRecord.return_(count)
	return Response(status=200)


# work
@bp.route('/items/use/approve', methods=['POST'])
@roles_accepted('warehouseman', 'admin')
def approve_item():
	"""
	Admins feature to approve booking request.
	---
	parameters:
		- in: body
		  name: itemIds
		  schema:
		    type: object
		    properties:
		      useIds:
		        type: array
		        items:
		          type: object
		          properties:
		            use_id:
		              type: integer
		            description:
		              type: string
	responses:
	  200:
	    description: Request is approved.
	  403:
	    description: Wrong use_id.
	"""
	req = request.get_json(force=True)
	useIds = req.get('useIds', None)
	if useIds is None:
		raise JSONNotEnoughError()
	for i in useIds:
		description = i['description']
		itemRecord = ItemInUse.search_by_use_id(i['use_id'])
		if itemRecord is None:
			raise ElementNotFoundError()
		itemRecord.is_confirm = True
		itemRecord.use_description = description
	db.session.commit()
	return Response(status=200)


@bp.route('/items/use/reject', methods=['POST'])
@roles_accepted('warehouseman', 'admin')
def reject_item():
	"""
	Admins feature to reject booking request.
	---
	parameters:
		- in: body
		  name: itemIds
		  schema:
		    type: object
		    properties:
		      useIds:
		        type: array
		        items:
		          type: object
		          properties:
		            use_id:
		              type: integer
	responses:
	  200:
	    description: Request is rejected.
	  403:
	    description: Wrong use_id.
	"""
	req = request.get_json()
	useIds = req.get('useIds', None)
	if useIds is None:
		raise JSONNotEnoughError()
	for i in useIds:
		itemRecord = ItemInUse.search_by_use_id(i['use_id'])
		if itemRecord is None:
			raise ElementNotFoundError()
		itemRecord.return_(itemRecord.item_quantity)
	return Response(status=200)
