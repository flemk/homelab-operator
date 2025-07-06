from functools import wraps
from django.utils import timezone
from django.core.cache import cache
from django.http import HttpResponse
from .models import Server, WOLSchedule

def rate_limit(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        ip = request.META.get('REMOTE_ADDR')
        key = f"rate_limit_is_online_{ip}"
        count = cache.get(key, 0)
        if count >= 120:
            return HttpResponse("Too Many Requests", status=429)
        cache.set(key, count + 1, timeout=60)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def update_uptime_statistics():
    now = timezone.now()
    hour = now.hour
    day = now.weekday()

    for server in Server.objects.all():
        if server.uptime_statistic.first():
            uptime_statistic = server.uptime_statistic.first()
            if not uptime_statistic.initialized:
                uptime_statistic.initialize_matrix()

            is_online = server.is_online()
            uptime_statistic.update_uptime(day, hour, is_online)

def process_schedules():
    now = timezone.now()
    minute_window = [(now.minute + offset) % 60 for offset in range(-5, 6)]
    schedules = WOLSchedule.objects.filter(
        enabled=True,
        schedule_time__hour=now.hour,
        schedule_time__minute__in=minute_window
    )

    for schedule in schedules.all():
        if schedule.server.auto_wake is False:
            schedules = schedules.exclude(id=schedule.id)
            continue
        if schedule.repeat:
            if schedule.repeat_type == 'daily':
                # schedule should be executed every day, no action needed
                continue
            if schedule.repeat_type == 'weekly':
                if schedule.schedule_time.weekday() != now.weekday():
                    schedules = schedules.exclude(id=schedule.id)
            elif schedule.repeat_type == 'monthly':
                if schedule.schedule_time.day != now.day:
                    schedules = schedules.exclude(id=schedule.id)
            else:
                schedules = schedules.exclude(id=schedule.id)
                continue
        else:
            if schedule.schedule_time.date() != now.date():
                schedules = schedules.exclude(id=schedule.id)

    for schedule in schedules:
        log_entry = f'[{now}] - SCHEDULE: No action performed for schedule {schedule.id}'
        server = schedule.server
        if server:
            if schedule.type == 'WAKE':
                response = server.wake()
                if response is False:
                    log_entry = f'[{now}] - WAKE: Magic packet sent to {server.name} ' + \
                                f'(Scheduled by {schedule.user.username})'
                else:
                    log_entry = f'[{now}] - WAKE: Failed to send magic packet to ' + \
                                f'{server.name}: {response}'
            elif schedule.type == 'SHUTDOWN':
                response = server.shutdown()
                if response is False:
                    log_entry = f'[{now}] - SHUTDOWN: Shutdown command sent to {server.name} ' + \
                                f'(Scheduled by {schedule.user.username})'
                else:
                    log_entry = f'[{now}] - SHUTDOWN: Failed to send shutdown command to ' + \
                                f'{server.name}: {response}'
        else:
            log_entry = f'[{now}] - SCHEDULE: No server found for schedule {schedule.id}'

        if schedule.enable_log:
            schedule.logs = (schedule.logs or '') + log_entry + '\n'
            schedule.save()

    return HttpResponse("OK", status=200)

import subprocess
import socket
import requests
import ipaddress
from bs4 import BeautifulSoup

def ping_host(ip):
    # Use system ping for simplicity (Linux)
    # TODO implement fallback or a pure Python ping
    try:
        output = subprocess.check_output(['ping', '-c', '1', '-W', '1', ip])
        return True
    except subprocess.CalledProcessError:
        return False

def evaluate_service_name(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    title_tag = soup.title
    name = title_tag.string if title_tag and title_tag.string else 'Unknown'

    lowered = name.lower()
    if 'homelab operator' in lowered:
        name = 'Homelab Operator'
    elif 'opnsense' in lowered:
        name = 'OPNsense Firewall'
    elif 'nginx' in lowered:
        name = 'Generic Nginx Web Server'
    elif 'nextcloud' in lowered:
        name = 'Nextcloud'
    elif 'paperless' in lowered:
        name = 'Paperless-ngx Document Management'
    elif 'jellyfin' in lowered:
        name = 'Jellyfin Media Server'
    elif 'home assistant' in lowered:
        name = 'Home Assistant'
    elif 'portainer' in lowered:
        name = 'Portainer'
    elif 'traefik' in lowered:
        name = 'Traefik Reverse Proxy'
    elif 'unraid' in lowered:
        name = 'Unraid Server'
    elif 'proxmox' in lowered:
        name = 'Proxmox Virtual Environment'
    elif 'pi-hole' in lowered:
        name = 'Pi-hole DNS Ad Blocker'
    elif 'grafana' in lowered:
        name = 'Grafana Dashboard'
    elif 'mysql' in lowered or 'mariadb' in lowered:
        name = 'MySQL/MariaDB Database Server'
    else:
        name = name.strip() or 'Unknown'

    return name

def check_http(ip):
    services = []
    for port, scheme in [(443, 'https'), (80, 'http')]:
        try:
            url = f'{scheme}://{ip}'
            response = requests.get(url, timeout=2, verify=False)  # TODO Insecure HTTPS request?
            server = response.headers.get('Server', 'Unknown')
            if response.ok and response.text:
                name = evaluate_service_name(response.text)
            else:
                name = 'Unknown'
            services.append({
                    'name': name,
                    'endpoint': ip,
                    'port': port,
                    'url': url,
                })
            break
        except Exception:
            continue
    return services

def discover_network(subnet='192.168.178.0/24'):
    servers = []
    net = ipaddress.ip_network(subnet)
    for ip in net.hosts():
        ip_str = str(ip)
        if ping_host(ip_str):
            services = check_http(ip_str)
            if services:
                servers.append({
                    'ip_address': ip_str,
                    'services': services
                })
    return servers
