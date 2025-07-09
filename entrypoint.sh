#!/bin/bash
set -e

# Run Django setup tasks
python ./homelab_operator/manage.py makemigrations
python ./homelab_operator/manage.py migrate
python ./homelab_operator/manage.py create_default_superuser

# Write environment variables to /etc/environment
printenv | grep API_KEY > /etc/environment

# Start cron
service cron start

# Start nginx
nginx -c /app/nginx.conf

# Start gunicorn (in foreground)
cd ./homelab_operator
exec gunicorn homelab_operator.wsgi:application --bind 127.0.0.1:8000 --worker-class=gevent
