FROM python:3.12.4-bookworm

LABEL org.opencontainers.image.source https://github.com/flemk/homelab-operator

ARG HOMELAB_OPERATOR_VERSION

EXPOSE 80 443

WORKDIR /app
ADD . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN python ./homelab_operator/manage.py collectstatic --noinput

RUN sed -i 's/%HOMELAB_OPERATOR_VERSION%/'"$HOMELAB_OPERATOR_VERSION"'/g' ./homelab_operator/templates/html/base.html

RUN openssl req -x509 -newkey rsa:4096 -keyout ./crt/key.pem -out ./crt/cert.pem -days 365 -nodes -subj '/CN=localhost'
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*
COPY nginx.conf /etc/nginx/sites-available/default

CMD python ./homelab_operator/manage.py migrate && nginx -c /app/nginx.conf && cd ./homelab_operator && waitress-serve --listen=*:8000 homelab_operator.wsgi:application
