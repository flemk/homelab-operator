FROM python:3.12.4-bookworm

LABEL org.opencontainers.image.source https://github.com/flemk/homelab-operator

ARG HOMELAB_OPERATOR_VERSION

EXPOSE 80 443

WORKDIR /app
ADD . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN python ./homelab_operator/manage.py collectstatic --noinput

RUN sed -i 's/%HOMELAB_OPERATOR_VERSION%/'"$HOMELAB_OPERATOR_VERSION"'/g' ./homelab_operator/templates/html/base.html

RUN openssl req -x509 -newkey rsa:4096 -keyout ./crt/key.key -out ./crt/cert.crt -days 365 -nodes -subj '/CN=localhost'
RUN apt-get update && apt-get install -y nginx cron curl && rm -rf /var/lib/apt/lists/*
COPY nginx.conf /etc/nginx/sites-available/default

# Create internal cron script
RUN mkdir -p /app/scripts
RUN echo '#!/bin/bash\n\
# Internal cron script to call the homelab-operator cron endpoint\n\
API_KEY=${API_KEY:-DEFAULT_API_KEY}\n\
curl -s http://localhost:8000/cron/${API_KEY}/ || echo "Cron call failed at $(date)"' > /app/scripts/internal_cron.sh
RUN chmod +x /app/scripts/internal_cron.sh
RUN echo "*/10 * * * * root /app/scripts/internal_cron.sh" >> /etc/crontab

CMD service cron start && python ./homelab_operator/manage.py makemigrations && python ./homelab_operator/manage.py migrate && nginx -c /app/nginx.conf && cd ./homelab_operator && waitress-serve --listen=*:8000 homelab_operator.wsgi:application
