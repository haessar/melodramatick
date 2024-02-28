# Melodramatick
## Installation
Set up environment

    git clone git@github.com:haessar/melodramatick.git
    cd melodramatick
    virtualenv --python=python3.10 venv
    source venv/bin/activate
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10  # update pip; specific to my own dev env
    python setup.py sdist
Install Melodramatick and dependencies

    pip install dist/melodramatick-X.X.X.tar.gz
    python manage.py migrate

Create super user

    python manage.py createsuperuser

Fill in .env with minimum expected environment variables

    SPOTIFY_CLIENT_ID=
    SPOTIFY_CLIENT_SECRET=
    RAPID_API_KEY=
    DATABASE_URL=mysql://<username>:<password>@<host>/melodramatick

## Create a new Melodramatick app (balletick example)
Initialise app

    python manage.py startapptick balletick --work ballet --colour-hex=#addde7
    export DJANGO_SETTINGS_MODULE=balletick.settings
    python manage.py makemigrations
    python manage migrate

When you are ready, launch site

    python manage.py runserver
