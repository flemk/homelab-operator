import subprocess
import requests
import ipaddress
import socket
from functools import wraps
from bs4 import BeautifulSoup

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

# Below functions are used for network discovery and service checks
# TODO refactor this into a separate module?

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
    port_schemes = [
        (443, 'https'),
        (80, 'http'),
        (8006, 'https'),  # Proxmox Web Interface
        ]
    for port, scheme in port_schemes:
        try:
            url = f'{scheme}://{ip}'
            response = requests.get(url, timeout=2, verify=False)  # TODO Insecure HTTPS request?
            if response.text:
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

def check_dns(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        # Standard DNS query for root (.)
        query = bytes([
            0xAA,  # Start byte or header
            0xBB,  # Second header byte
            0x01,  # Command or version
            0x00, 0x00,  # Reserved or flags
            0x01,  # Some flag or length
            0x00, 0x00,  # Reserved
            0x00, 0x00,  # Reserved
            0x00, 0x00,  # Reserved
            0x00, 0x00,  # Reserved
            0x00, 0x00,  # Reserved
            0x00, 0x00,  # Reserved
            0x00, 0x00,  # Reserved
            0x00, 0x00,  # Reserved
        ])
        sock.sendto(query, (ip, 53))
        data, _ = sock.recvfrom(512)
        if data:
            return [{
                'name': 'DNS Service',
                'endpoint': ip,
                'port': 53,
                'url': f'dns://{ip}'
            }]
    except Exception:
        pass
    finally:
        sock.close()

    return []

def discover_services(ip_str: str):
    services = []
    services.extend(check_http(ip_str))
    services.extend(check_dns(ip_str))
    # TODO Add more service checks (SSH, FTP, etc.)

    return services

def discover_network_stream(subnet, task_id=None):
    yield f'<!DOCTYPE html>\n'.encode()
    yield '<style>html {font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif; padding: 1rem;}</style>'.encode()

    yield f"Starting discovery on subnet {subnet}<br><br>".encode()

    servers = []
    servers_found = 0
    net = ipaddress.ip_network(subnet)

    for ip in net.hosts():
        ip_str = str(ip)
        yield f"Pinging {ip_str}... ".encode()

        if ping_host(ip_str):
            yield f"alive.<br>".encode()

            # Reverse DNS
            try:
                hostname = socket.gethostbyaddr(ip_str)[0]
            except Exception:
                hostname = None
            yield f"- Hostname: {hostname or 'N/A'}<br>".encode()

            # MAC address via ARP
            mac = None
            try:
                arp_output = subprocess.check_output(['arp', '-n', ip_str]).decode()
                for line in arp_output.splitlines():
                    if ip_str in line:
                        parts = line.split()
                        for part in parts:
                            if ':' in part and len(part) == 17:
                                mac = part
                                break
                        if mac:
                            break
            except Exception:
                pass
            yield f"- MAC: {mac or 'N/A'}<br>".encode()

            # Service discovery
            services = discover_services(ip_str)

            servers.append({
                'ip_address': ip_str,
                'hostname': hostname,
                'mac_address': mac,
                'services': services
            })

            if services:
                servers_found += 1
                yield f"- Services: {services}<br>".encode()
            else:
                yield f"- No services found.<br>".encode()
        else:
            yield f"unreachable.<br>".encode()
        yield f"\n".encode()

    cache.set(f"scan:{task_id}", servers, timeout=3600)

    yield f"<br>Discovery complete. {servers_found} servers found.\n".encode()
