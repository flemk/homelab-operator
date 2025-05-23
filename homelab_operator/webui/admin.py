from django.contrib import admin
from .models import Server, Service, Network, WOLSchedule, ShutdownURLConfiguration

class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'mac_address')
admin.site.register(Server, ServerAdmin)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'server', 'port')
admin.site.register(Service, ServiceAdmin)

class NetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
admin.site.register(Network, NetworkAdmin)

class WOLScheduleAdmin(admin.ModelAdmin):
    list_display = ('server', 'schedule_time', 'repeat', 'repeat_type')
admin.site.register(WOLSchedule, WOLScheduleAdmin)

class ShutdownURLConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'server')
admin.site.register(ShutdownURLConfiguration, ShutdownURLConfigurationAdmin)
