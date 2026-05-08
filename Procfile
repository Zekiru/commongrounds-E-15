release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn commongrounds.wsgi --log-file -
