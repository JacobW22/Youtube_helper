#!/bin/sh

# Run Gunicorn
echo "Running command: 'gunicorn --workers=5 --threads=2 youtube_helper.wsgi:application -b 0.0.0.0:8000'"

python manage.py makemigrations && python manage.py migrate && gunicorn --workers=4 --threads=2 youtube_helper.wsgi:application -b 0.0.0.0:8000