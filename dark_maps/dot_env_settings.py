import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
print(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, ".environment"))

from .settings import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase',
    }
}

ALLOWED_HOSTS = "*"

SECURE_SSL_REDIRECT = False

# To use: python manage.py runserver --settings=dark_maps.dot_env_settings
