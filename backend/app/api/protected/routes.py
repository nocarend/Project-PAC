from flask import jsonify
from flask_praetorian import auth_required, current_user

from app.api.protected import bp


@bp.route("/fromAny")
@auth_required
def protected():
	"""
	A protected endpoint. The auth_required decorator will require a header
	containing a valid JWT
	.. example::
	   $ curl http://localhost:5000/protected -X GET \
		 -H "Authorization: Bearer <your_token>"
	"""
	return jsonify(user=current_user().user_name, is_allowed=True)
