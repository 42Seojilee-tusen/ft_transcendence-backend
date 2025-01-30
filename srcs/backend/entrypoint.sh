#!/bin/bash

cd ./mysite

python manage.py makemigrations
python manage.py migrate

test -f manage.py || django-admin startproject mysite .
# mkdir -p /logs
# touch /logs/django.log
# chmod 755 /logs/django.log

#tail -f /logs/django.log

# python3 manage.py runserver 0.0.0.0:8000
gunicorn config.wsgi --bind 0.0.0.0:8000
