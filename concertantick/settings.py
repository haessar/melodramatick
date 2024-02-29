from melodramatick.settings import *  # noqa: F401, F403
from melodramatick.settings import INSTALLED_APPS as IMPORTED_APPS
from melodramatick.settings import BASE_DIR, ALLOWED_HOSTS, TEMPLATES, STATICFILES_DIRS


ALLOWED_HOSTS.extend(["vm", "127.0.0.1", "concertantick"])


#  Application definition

INSTALLED_APPS = ['concertantick'] + IMPORTED_APPS

TEMPLATES[0]['DIRS'].extend([BASE_DIR / "concertantick" / "templates"])

STATICFILES_DIRS = [BASE_DIR / "concertantick" / "static"] + STATICFILES_DIRS


# Site-specific settings

WORK_MODEL = 'concertantick.Concerto'
WORK_PLURAL_LABEL = 'concertos'

SITE = 'Concertantick'
BACKGROUND_COLOUR = '#eee80e'

SITE_ID = 3

INSTRUMENT_CHOICES = [
    ("piano", "Piano"),
]
