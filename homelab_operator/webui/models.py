'''Models for the web UI of the homelab operator.'''
import os
import requests
import socket
from django.db import models
from django.utils.html import format_html

class UserProfile(models.Model):
    '''Model representing a user profile.'''
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile',
                                help_text='The user this profile belongs to')
    last_selected_homelab = models.ForeignKey('Homelab', on_delete=models.SET_NULL,
                                              null=True, blank=True,
                                              help_text='The last selected homelab for this user')
    show_wiki = models.BooleanField(default=True, help_text='Show or hide the wiki in the UI')
    show_networks = models.BooleanField(default=True, help_text='Show or hide networks in the UI')
    dark_mode = models.BooleanField(default=False,
                                    help_text='Enable Dark Mode (experimental)')

    def __str__(self):
        return f"Profile of {self.user.username}"

class Server(models.Model):
    '''Model representing a server.'''
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True,
                                              help_text='IP address of the server')
    port = models.IntegerField(default=80, null=True, blank=True,
                               help_text='Will be used to check if the server is online')
    mac_address = models.CharField(max_length=17, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    network = models.ForeignKey('Network', on_delete=models.CASCADE, null=True,
                                blank=True, related_name='servers')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    homelab = models.ForeignKey('Homelab', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='servers')
    auto_wake = models.BooleanField(default=False, help_text='Automatically wake the server on access')
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
        # TODO move this implementation to ShutdownURLConfiguration model
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
        except requests.exceptions.ConnectTimeout:
            return "Connection timed out."
        except requests.RequestException as e:
            return f"Shutdown failed with status code: {response.status_code}"

    def is_online(self):
        '''Checks if the server is online by attempting to connect to SSH.'''
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
    endpoint = models.CharField(max_length=100, null=True, blank=True,
                                help_text='Domain or IP address of the service. Used for online checking.')
    port = models.IntegerField(default=80)
    url = models.URLField(null=True, blank=True,
                          help_text='URL to access the service, if applicable. Used to redirect to the service.')
    icon_url = models.URLField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} on {self.server.name}"

    def is_online(self):
        '''Checks if the service is online by attempting to connect to the endpoint (domain or IP) and port.'''
        if not self.endpoint:
            return 'No endpoint provided.'

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                sock.connect((self.endpoint, self.port))
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
    repeat_type = models.CharField(max_length=10,
                                   choices=[
                                       ('daily', 'Daily'),
                                       ('weekly', 'Weekly'),
                                       ('monthly', 'Monthly'),
                                       ], null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    enabled = models.BooleanField(default=True, help_text='Enable or disable the WOL schedule')
    repeat = models.BooleanField(default=False, help_text='Repeat the WOL schedule')
    logs = models.JSONField(null=True, blank=True, default='',
                            help_text='Logs of the WOL schedule execution')
    enable_log = models.TextField(default='',
                                  help_text='Enable or disable logging for the WOL schedule')

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
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    public = models.BooleanField(default=False, help_text='Make the wiki accessible public')
    show_network_graph = models.BooleanField(default=True,
                                             help_text='Show a network graph in the wiki')
    show_servers = models.BooleanField(default=True, help_text='Show servers in the wiki')
    show_services = models.BooleanField(default=True, help_text='Show services in the wiki')
    homelab = models.ForeignKey('Homelab', on_delete=models.CASCADE,
                                related_name='wiki')  # Homelab expected to only have one wiki
    pinned_services = models.ManyToManyField(Service, blank=True,
                                             related_name='pinned_wikis',
                                             help_text='Services pinned to the wiki for quick access')

    def __str__(self):
        return f"Wiki for {self.homelab.name}" if self.homelab else "Dangling Wiki"

class ServerUptimeStatistic(models.Model):
    '''Model representing server uptime statistics.
    matrix is a 7x24 matrix storing uptime statistics for each hour of the week:
        {
            "0": { # Day 0 (Monday)
                "0": [0.0, 1], # Hour 0 (00:00) - 0.0% uptime, 1 data point
                "1": [0.0, 1], # Hour 1 (01:00) - 0.0% uptime, 1 data point
                ...,
                "23": [0.0, 1] # Hour 23 (23:00) - 0.0% uptime, 1 data point
                },
            "1": { # Day 1 (Tuesday)
                ...
                },
            ...
        }
    '''
    server = models.ForeignKey('Server', on_delete=models.CASCADE, unique=True,
                               related_name='uptime_statistic')
    matrix = models.JSONField(default={"not":"initialized"})  # stores 7×24 matrix as nested lists/dict
    initialized = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Uptime statistics for {self.server.name}"

    def initialize_matrix(self):
        '''Initializes the uptime matrix with zeros.'''
        self.matrix = {str(day): {str(hour): [0.0, 0] for hour in range(24)} for day in range(7)}
        self.initialized = True
        self.save()

    def update_uptime(self, day: int, hour: int, is_online: bool):
        '''Increments the uptime for a specific day and hour.'''
        if not self.initialized:
            self.initialize_matrix()

        if str(day) in self.matrix and 0 <= hour < 24:
            p_old, n = self.matrix[str(day)][str(hour)]
            p_new = (p_old * n + int(is_online)) / (n + 1)
            self.matrix[str(day)][str(hour)][0] = p_new
            self.matrix[str(day)][str(hour)][1] += 1
            self.save()
        else:
            raise ValueError("Invalid day or hour for uptime matrix.")

    def get_probability_matrix(self):
        '''Returns the probability matrix as a 7x24 list.'''
        DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return [(DAY_NAMES[day], [(hour, self.matrix[str(day)][str(hour)][0]) for hour in range(24)]) for day in range(7)]
    