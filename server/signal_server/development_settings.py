"""
Django settings for signal_server project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

from .settings import *

DEBUG = True

ALLOWED_HOSTS =  "*"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'