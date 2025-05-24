> This project superseeds [flemk/server-dashboard](https://github.com/flemk/server-dashboard)

# Homelab Operator
Homelab Operator displays your homelab infrastructure and provides actions such as wake-on-lan and ssh-shutdown. You can also create an overview of your services running on your machines. You can enable auto-wake where this tool wakes your servers based on usage heuristic (tbd) or create schedules to wake/shutdown your server (which are triggered by a cron job +/-5min).

This tool is still in development.

![Dashboard](./src/dashboard.png)

## Installation
### Docker Compose
See `docker-compose.yml` or `docker-compose-build-local.yml` and the `.env` file.

The easiest way to run this application is by using docker compose. A sample configuration coul look like:

```yaml
services:
  web:
    image: ghcr.io/flemk/homelab-operator:latest
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_HOST=${POSTGRES_HOST}
      - POSTGRES_PORT=${POSTGRES_PORT}
      - ALLOWED_HOST=${ALLOWED_HOST}
      - CSRF_TRUSTED_ORIGIN=${CSRF_TRUSTED_ORIGIN}
    ports:
      - "${WEB_PORT}:80"
      - "${WEB_SSL_PORT}:443"
    volumes:
      - ./web-crt:/app/crt  # Use your own certificates
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - ./db-data:/var/lib/postgresql/data
```

For WOL to work you need to have a route to the target machine(s). You may need to add the docker container to a macvlan network:
```bash
docker network create \
  -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=eth0 \
  macvlan_net
docker network connect macvlan_net <container>
```
You also may need to adjust the `BROADCAST_ADDRESS=255.255.255.255` environment variable.

To use the auto-wake functionality properly, you need to create a system level cron job in `crontab -e`:
```bash
# Call /cron inside the homelab-operator container
*/5 * * * * docker exec <container> php /var/www/html/cron.php
```
You need to call the cron endpoint every 10min for full coverage.