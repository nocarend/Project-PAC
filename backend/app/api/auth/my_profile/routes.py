from flask import jsonify
from flask_praetorian import auth_required, current_user

from app.api.auth.my_profile import bp


# потом пост нужен будет и т д, использовать как настройки
@bp.route('/', methods=['GET'])
@auth_required
def my_data():
	"""
	Get all current user data and his items.
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
		description: Data is given. Format ....
        # value: prediction details
        # schema:
        #   $ref: '#/definitions/value'
        # examples:
        #   rgb: ['red', 'green', 'blue']
    # definitions:
    #   data:
    #     type: array
    #     items:
    #       type: object
    #         items:
    #           $ref: '#/definitions/Color'
    #       itemsInUse:
    #         type: array
    #         properties
	#
    #   Color:
    #     type: string
	"""
	itemsRecords = current_user()
	return jsonify(user=itemsRecords)
