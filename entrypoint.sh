#!/bin/bash
set -e

# Run Django setup tasks
python ./homelab_operator/manage.py makemigrations
python ./homelab_operator/manage.py migrate
python ./homelab_operator/manage.py create_default_superuser

# Write environment variables to /etc/environment
printenv | grep API_KEY > /etc/environment

# Replace placeholders in nginx configuration files
if [ -z "${HOST}" ]; then
  echo "[ERROR] HOST environment variable is not set."
  exit 1
fi
sed -i "s/%HOMELAB_OPERATOR_HOST%/${HOST}/g" /app/nginx/homelab-operator.conf
sed -i "s/%HOMELAB_OPERATOR_HOST%/${HOST}/g" /app/nginx/ingress-forward.conf

# Start cron
service cron start

# Start nginx
nginx -c /app/nginx.conf

# Start nginx for ingress handling
nginx -t -c /app/nginx/ingress-handler.conf
if [ $? -ne 0 ]; then
  echo "[WARNING] Nginx configuration test failed. Please check your configurations. Resuming without ingress handler."
else
  nginx -c /app/nginx/ingress-handler.conf
fi

# Start gunicorn (in foreground)
cd ./homelab_operator
exec gunicorn homelab_operator.wsgi:application --bind 127.0.0.1:8000 --worker-class=gevent
