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
- source venv/bin/activate
- pip install -r requirements.txt
- python manage.py migrate
- python manage.py collectstatic
- sudo systemctl restart gunicorn.target
- sudo systemctl restart celery.target
