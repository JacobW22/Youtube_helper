#!/bin/sh

# Run Gunicorn
echo "Running command: 'gunicorn --workers=5 --threads=2 youtube_helper.wsgi:application -b 0.0.0.0:8000'"
exec gunicorn --workers=5 --threads=2 youtube_helper.wsgi:application -b 0.0.0.0:8000