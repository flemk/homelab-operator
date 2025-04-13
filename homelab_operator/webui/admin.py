from django.contrib import admin
from .models import Server, Service

class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'mac_address')
admin.site.register(Server, ServerAdmin)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'server', 'port', 'protocol', 'status')
admin.site.register(Service, ServiceAdmin)
