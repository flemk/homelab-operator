from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Server, Service, Network, WOLSchedule, ShutdownURLConfiguration, Homelab, \
    Wiki, UserProfile, ServerUptimeStatistic, AppState, Ingress, MaintenancePlan

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'mac_address')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'server', 'port')

@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')

@admin.register(WOLSchedule)
class WOLScheduleAdmin(admin.ModelAdmin):
    list_display = ('server', 'schedule_time', 'repeat', 'repeat_type')

@admin.register(ShutdownURLConfiguration)
class ShutdownURLConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'server')

@admin.register(Homelab)
class HomelabAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'user')

@admin.register(Wiki)
class WikiAdmin(admin.ModelAdmin):
    list_display = ('homelab',)

@admin.register(ServerUptimeStatistic)
class ServerUptimeStatisticAdmin(admin.ModelAdmin):
    list_display = ('server',)

@admin.register(AppState)
class AppStateAdmin(admin.ModelAdmin):
    list_display = ('last_cron',)

@admin.register(Ingress)
class IngressAdmin(admin.ModelAdmin):
    list_display = ('name', 'homelab', 'target_service', 'created_at')
    list_filter = ('homelab', 'target_service')
    search_fields = ('name', 'target_service__name')

@admin.register(MaintenancePlan)
class MaintenancePlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'assignee', 'priority', 'scheduled_date', 'repeat_interval')
