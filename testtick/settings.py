from melodramatick.settings import *  # noqa: F401, F403
from melodramatick.settings import INSTALLED_APPS as IMPORTED_APPS
from melodramatick.settings import BASE_DIR, ALLOWED_HOSTS, TEMPLATES, STATICFILES_DIRS


ALLOWED_HOSTS.extend(["127.0.0.1", "localhost", "testtick"])


#  Application definition

INSTALLED_APPS = ['testtick'] + IMPORTED_APPS

TEMPLATES[0]['DIRS'].extend([BASE_DIR / "testtick" / "templates"])

STATIC_ROOT = '/var/www/testtick/static'
STATICFILES_DIRS = [BASE_DIR / "testtick" / "static"] + STATICFILES_DIRS


# Test deployment settings

WORK_MODEL = 'testtick.Testitem'
WORK_PLURAL_LABEL = 'testitems'

SITE = 'Testtick'
BACKGROUND_COLOUR = '#d9edf7'

SITE_ID = 4

TEST_RUNNER = 'testtick.runner.TesttickDiscoverRunner'

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "testtick",
    }
}
