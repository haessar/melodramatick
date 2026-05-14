# Melodramatick
## Installation
Set up environment

    git clone <your-new-template-repo-url>
    cd <your-new-template-repo>
    virtualenv --python=python3.10 venv
    source venv/bin/activate
    python -m pip install --upgrade pip

Create your local environment file

    cp .env-sample .env

Install Melodramatick and dependencies

    python -m pip install -e .
    python manage.py migrate

By default, Melodramatick uses a local SQLite database at `db.sqlite3`.
To use MySQL instead, install the MySQL extra and set `DATABASE_URL` in `.env`:

    python -m pip install -e ".[mysql]"

Composer quotes are optional. If you want to populate quotes from RapidAPI,
add `RAPID_API_KEY` to `.env` before running the quote import helper.

Create super user

    python manage.py createsuperuser

## Create a new Melodramatick app (balletick example)
Initialise app

    python manage.py startapptick balletick --work ballet --colour-hex=#addde7
    export DJANGO_SETTINGS_MODULE=balletick.settings
    python manage.py makemigrations
    python manage migrate

When you are ready, launch site

    python manage.py runserver

## Example deployments
The live example ecosystem is maintained on the `production` branch, where currently Operatick, Balletick and Concertantick are linked as submodules.

## Contributing
### testtick dummy app for testing
Due to the polymorphic nature of core Melodramatick models, we have provided a dummy "testtick" validation app to provide class instantiations for unit testing of core functionality, rather than relying on submodules. It is not intended as a real engagement site for deployment.
