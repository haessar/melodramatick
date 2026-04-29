Enabled systemd services:
- gunicorn@operatick.service
- gunicorn@concertantick.service
- gunicorn@balletick.service
- celery@operatick.service
- celery@concertantick.service
- celery@balletick.service

Nginx configs:
- /etc/nginx/sites-available/operatick
- /etc/nginx/sites-available/concertantick
- /etc/nginx/sites-available/balletick

Static locations:
- /var/www/operatick/static/
- /var/www/concertantick/static/
- /var/www/balletick/static/

Database:
- MySQL local
- DB name: melodramatick
- User: haessar
- Connection via DATABASE_URL in .env

Deploy commands:
- git pull
- git submodule update --recursive --remote
- source venv/bin/activate
- pip install .
- SETTINGS_MODULES="operatick.settings balletick.settings concertantick.settings"
- for settings in $SETTINGS_MODULES; do
    DJANGO_SETTINGS_MODULE=$settings python manage.py migrate
    DJANGO_SETTINGS_MODULE=$settings python manage.py collectstatic --noinput
  done
- sudo systemctl restart celery.target gunicorn.target
- sudo systemctl restart nginx
