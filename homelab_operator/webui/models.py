from django.db import models
import socket
import paramiko

class Server(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17)
    note = models.TextField(null=True, blank=True)
    ssh_username = models.CharField(max_length=100, null=True, blank=True)
    ssh_password = models.CharField(max_length=100, null=True, blank=True)
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
        
    def shutdown(self):
        try:
            if self.ssh_username and self.ssh_password:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(self.ip_address, username=self.ssh_username, password=self.ssh_password)
                stdin, stdout, stderr = client.exec_command('sudo shutdown now')
                client.close()
                return True
            else:
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
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='services')
    port = models.IntegerField()
    icon_url = models.URLField(null=True, blank=True)
    note = models.TextField(null=True, blank=True) 

    def __str__(self):
        return f"{self.name} on {self.server.name}"
