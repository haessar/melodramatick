# Melodramatick
mkdir balletick
cd balletick
virtualenv --python=python3.10 venv
source venv/bin/activate
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10  # update pip
pip install ../melodramatick/dist/melodramatick-0.1.tar.gz
django-admin startproject balletick .    ## /home/haessar/personal_projects/balletick
python manage.py startapp ballet
**FILL IN APP**
**FILL IN .env WITH ENV VARIABLES**
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
