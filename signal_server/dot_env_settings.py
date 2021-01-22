import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
print(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, ".environment"))

from .settings import *

DEBUG = True

ALLOWED_HOSTS = "*"

SECURE_SSL_REDIRECT = False

# To use: python manage.py runserver --settings=signal_server.dot_env_settings
