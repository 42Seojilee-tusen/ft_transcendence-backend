#!/bin/bash

cd ./mysite

sleep 3

python manage.py makemigrations
python manage.py migrate

test -f manage.py || django-admin startproject mysite .
mkdir -p images/profiles
mkdir -p images/two_factor_qr_code

# python3 manage.py runserver 0.0.0.0:8000
# gunicorn config.wsgi --bind 0.0.0.0:8000
daphne -b 0.0.0.0 -p 8000 config.asgi:application
