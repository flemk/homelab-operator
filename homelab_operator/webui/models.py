from django.db import models
import socket

class Server(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17)
    note = models.TextField(null=True, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def wake(self):
        try:
            mac_bytes = bytes.fromhex(self.mac_address.replace(":", "").replace("-", ""))
            magic_packet = b'\xff' * 6 + mac_bytes * 16
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(magic_packet, ("255.255.255.255", 9))
            return False
        except Exception as e:
            return str(e)

    def is_online(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                sock.connect((self.ip_address, 22))
            return True
        except (socket.timeout, socket.error):
            return False

class Service(models.Model):
    name = models.CharField(max_length=100)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    port = models.IntegerField()
    protocol = models.CharField(max_length=10, choices=[('TCP', 'TCP'), ('UDP', 'UDP')])
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} on {self.server.name}"
