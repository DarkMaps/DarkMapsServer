# # Start Gunicorn processes
# echo Starting Gunicorn.
# exec gunicorn signal_server.wsgi:application \
#     --bind 0.0.0.0:8000 \
#     --workers 3

python manage.py runserver --settings=signal_server.settings
