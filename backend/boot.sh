#!/bin/sh
# shellcheck disable=SC2039
source venv/bin/activate
flask db init
flask db migrate
flask db stamp head
flask db upgrade
exec gunicorn -b :5000 --access-logfile - --error-logfile - nsu:app