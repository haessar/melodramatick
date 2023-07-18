# Melodramatick
## Create a new Melodramatick project (balletick example)
Set up environment

    mkdir balletick
    cd balletick
    virtualenv --python=python3.10 venv
    source venv/bin/activate
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10  # update pip; specific to my own dev env
Install Melodramatick and dependencies

    pip install ../melodramatick/dist/melodramatick-X.X.X.tar.gz
Start new django project in same dir

    django-admin startproject balletick .

Create "work" app

    python manage.py startapp ballet
    <fill in app models, settings, etc, inheriting from melodramatick.work>
**FILL IN .env WITH ENV VARIABLES**

Prepare database

    python manage.py makemigrations  # This will also create migrations for melodramatick models defined in your virtualenv
    python manage.py migrate
    python manage.py createsuperuser

Launch site

    python manage.py runserver
