# Melodramatick

Melodramatick is a Django template repository for building "tick" sites: catalogue and audience-engagement apps centred on a particular kind of work, such as operas, ballets, concertos, or other collections in the performing arts.

The shared core provides reusable apps for composers, works, performances, listening, top lists, accounts, admin tooling, and common UI. Each generated tick app supplies its own concrete work model, as well as settings, templates, and site identity.

## Installation

Start by creating your own repository from the Melodramatick template on
GitHub. Click **Use this template** > **Create a new repository**. Leave
**Include all branches** unchecked.

Set up environment

    git clone <your-new-template-repo-url>
    cd <your-new-template-repo>
    virtualenv --python=python3.10 venv
    source venv/bin/activate
    python -m pip install --upgrade pip

Create your local environment file

    cp .env-sample .env

You can edit `.env` to configure local or deployment-specific settings. The
sample file includes the available settings and their default local values.

Install Melodramatick and dependencies

    python -m pip install -e .

By default, Melodramatick uses a local SQLite database at `db.sqlite3`.
To use MySQL instead, install the MySQL extra and set `DATABASE_URL` in `.env`:

    python -m pip install -e ".[mysql]"

## Create a new Melodramatick app (`balletick` example)
You should now have your instance of Melodramatick installed and may want to create a bespoke site to track audience engagement in some performing arts context. Let's take "Balletick" as an example - a site for tracking engagement with ballet works across the ages.

Let's initialise the app

    python manage.py startapptick balletick --work ballet --colour-hex=#addde7
    export DJANGO_SETTINGS_MODULE=balletick.settings

*Note: Remember to re-run this `export` command whenever you have a fresh terminal session to ensure DJANGO_SETTINGS_MODULE is set correctly.*

This will have created a custom `Ballet` model. You might want to add some bespoke fields to allow recording of, for example, a work's choreographer. You can do this by editing the `class Ballet` definition in `balletick/models.py`.

When you are happy with the custom model code, migrate the models to your configured database

    python manage.py makemigrations
    python manage.py migrate

To begin populating your site, you will need to create a "superuser" to access the admin interface:

    python manage.py createsuperuser

When you are ready, launch the site locally

    python manage.py runserver

and visit http://127.0.0.1:8000/ in your browser, where you can sign in with your superuser account and click "Admin".

### Optional data imports
Rather than manually entering all your data via the admin interface to populate your site, you might want to use some provided automations. Both the `Composers` and `Works` (or in this case `Ballets`) admin pages have an `Import CSV` button to allow instant population of these objects from prepared CSV files (see `guides/csv_imports.md` for formatting advice).

Composer quotes are optional; when populated they will appear on the home page of your site. After populating composers, if you want to populate quotes from RapidAPI, add `RAPID_API_KEY` to `.env` before opening a Django shell

    python manage.py shell

and running the quote import helper:

    exec(open("./melodramatick/utils/quotel_api.py").read())

## Example deployments
The live example ecosystem is maintained on https://github.com/haessar/melodramatick/tree/production, where currently Operatick, Balletick and Concertantick are linked as submodules. These live sites can each be accessed via https://melodramatick.com/.

## Contributing

If you want to build your own tick site, use the template flow above. If you want to contribute to changing the Melodramatick core itself, fork the Melodramatick repository, clone your fork, make changes on a branch, and open a pull request.

    git clone git@github.com:<your-github-username>/melodramatick.git
    cd melodramatick

### testtick dummy app for testing

Due to the [polymorphic](https://django-polymorphic.readthedocs.io/en/stable/quickstart.html#making-your-models-polymorphic) nature of core Melodramatick models, we have provided a dummy "testtick" validation app to provide class instantiations for unit testing of core functionality, rather than relying on submodules. It is not intended as a real engagement site for deployment.

Run the test suite before opening a pull request:

    DJANGO_SETTINGS_MODULE=testtick.settings DATABASE_URL=sqlite:////tmp/melodramatick-test.sqlite3 python manage.py test
