'''Models for the web UI of the homelab operator.'''

import os
import requests
import socket
from django.db import models

class Server(models.Model):
    '''Model representing a server.'''
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    port = models.IntegerField(default=80, null=True, blank=True)
    mac_address = models.CharField(max_length=17, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    network = models.ForeignKey('Network', on_delete=models.CASCADE, null=True,
                                blank=True, related_name='servers')
    status_url = models.URLField(null=True, blank=True)  # TODO implement status URL check
    auto_wake = models.BooleanField(default=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    homelab = models.ForeignKey('Homelab', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='servers')
    # TODO Shutdown URL configuration (related_name): implement as shutdown_adapther, which can be
    # a ShutdownURLConfiguration, ShutdownSSLConfiguration, similar ...

    def __str__(self):
        return str(self.name)

    def wake(self):
        '''Sends a Wake-on-LAN magic packet to the server.'''
        if not self.mac_address:
            return 'No MAC address provided.'
        try:
            mac_bytes = bytes.fromhex(self.mac_address.replace(":", "").replace("-", ""))
            magic_packet = b'\xff' * 6 + mac_bytes * 16

            broadcast_address = os.getenv('BROADCAST_ADDRESS', '255.255.255.255')
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(magic_packet, (broadcast_address, 9))
            return False
        except Exception as e:
            return str(e)

    def shutdown(self):
        '''calls the shutdown URL of the server.'''
        if not self.shutdown_url:
            return 'No shutdown URL provided.'
        if self.shutdown_url.all().count() > 1:
            return 'Multiple shutdown URLs provided.'
        shutdown_url = self.shutdown_url.all().first()
        if shutdown_url is None:
            return 'No shutdown URL configuration found.'

        try:
            response = requests.post(
                shutdown_url.url,
                headers=shutdown_url.headers,
                data=shutdown_url.data,
                timeout=10,
                verify=False,  # Disable SSL verification for testing or self-signed certificates
                )
            if response.status_code == 200:
                return False
            return f"Shutdown failed with status code: {response.status_code}"
        except requests.RequestException as e:
            return str(e)

    def is_online(self):
        '''Checks if the server is online by attempting to connect to SSH.'''
        # TODO this could be as well implemented in the browser as JS/ping ... reduces loading time
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                sock.connect((self.ip_address, self.port))
            return True
        except (socket.timeout, socket.error):
            return False

class Service(models.Model):
    '''Model representing a service running on a server.'''
    name = models.CharField(max_length=100)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='services')
    port = models.IntegerField(default=80)
    icon_url = models.URLField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} on {self.server.name}"

    def is_online(self):
        '''Checks if the service is online by attempting to connect to the specified port.'''
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                sock.connect((self.server.ip_address, self.port))
            return True
        except (socket.timeout, socket.error):
            return False

class Network(models.Model):
    '''Model representing a network.'''
    name = models.CharField(max_length=20)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    homelab = models.ForeignKey('Homelab', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='networks')

    def __str__(self):
        return str(self.name)

class WOLSchedule(models.Model):
    '''Model representing a Wake-on-LAN schedule.'''
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='wol_schedules')
    schedule_time = models.DateTimeField()
    type = models.CharField(max_length=10,
                                   choices=[
                                       ('WAKE', 'WAKE'),
                                       ('SHUTDOWN', 'SHUTDOWN'),
                                       ])
    enabled = models.BooleanField(default=True)
    repeat = models.BooleanField(default=False)
    repeat_type = models.CharField(max_length=10,
                                   choices=[
                                       ('daily', 'Daily'),
                                       ('weekly', 'Weekly'),
                                       ('monthly', 'Monthly'),
                                       ], null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"WOL for {self.server.name} at {self.schedule_time}"

class ShutdownURLConfiguration(models.Model):
    '''Model representing a shutdown URL configuration.'''
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=300)
    headers = models.JSONField(null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='shutdown_url')

    def __str__(self):
        return str(self.name)

    def is_valid(self):
        '''Checks if the shutdown URL is valid by sending a test request.'''
        pass

class Homelab(models.Model):
    '''Model representing a homelab.'''
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True,
                             related_name='homelabs')

    def __str__(self):
        return str(self.name)

class Wiki(models.Model):
    '''Model representing a wiki page for a homelab.'''
    public = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    show_networks = models.BooleanField(default=True)
    show_servers = models.BooleanField(default=True)
    show_services = models.BooleanField(default=True)
    homelab = models.ForeignKey('Homelab', on_delete=models.CASCADE, related_name='wiki')
