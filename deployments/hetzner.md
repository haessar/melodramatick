# Hetzner Deployment

This file documents the current Hetzner production host. It complements
`deployments/promote-release.md`, which covers the release promotion workflow.

Pushing to the `production` branch triggers `.github/workflows/deploy.yml`.
That workflow connects to the Hetzner host over SSH and runs the deployment
commands listed below.

## GitHub Actions secrets

The deployment workflow requires these repository secrets:

- `HOST`: Hetzner host address.
- `USERNAME`: SSH username.
- `KEY`: SSH private key.

## Host inventory

Enabled systemd services:

- `gunicorn@operatick.service`
- `gunicorn@concertantick.service`
- `gunicorn@balletick.service`
- `celery@operatick.service`
- `celery@concertantick.service`
- `celery@balletick.service`

Nginx configs:

- `/etc/nginx/sites-available/operatick`
- `/etc/nginx/sites-available/concertantick`
- `/etc/nginx/sites-available/balletick`

Static locations:

- `/var/www/operatick/static/`
- `/var/www/concertantick/static/`
- `/var/www/balletick/static/`

Database:

- MySQL runs locally on the Hetzner host.
- Database name: `melodramatick`
- Database user: `haessar`
- Django connection is configured via `DATABASE_URL` in `.env`.

## Deployment workflow commands

The deployment workflow runs these commands on the Hetzner host:

```bash
cd melodramatick/
source venv/bin/activate
git stash
git fetch origin
git checkout production
git pull origin production
git submodule update --init --recursive
git stash pop
pip install -e .
SETTINGS_MODULES="operatick.settings balletick.settings concertantick.settings"
for settings in $SETTINGS_MODULES; do
  DJANGO_SETTINGS_MODULE=$settings python manage.py migrate
  DJANGO_SETTINGS_MODULE=$settings python manage.py collectstatic --noinput
done
sudo systemctl restart celery.target gunicorn.target
sudo systemctl restart nginx
```

## Manual checks

Check service status:

```bash
sudo systemctl status celery.target gunicorn.target nginx
```

Check recent Gunicorn logs:

```bash
sudo journalctl -u gunicorn@operatick.service -n 100 --no-pager
sudo journalctl -u gunicorn@balletick.service -n 100 --no-pager
sudo journalctl -u gunicorn@concertantick.service -n 100 --no-pager
```

Check recent Celery logs:

```bash
sudo journalctl -u celery@operatick.service -n 100 --no-pager
sudo journalctl -u celery@balletick.service -n 100 --no-pager
sudo journalctl -u celery@concertantick.service -n 100 --no-pager
```

Check Nginx status and configuration:

```bash
sudo nginx -t
sudo systemctl status nginx
```
