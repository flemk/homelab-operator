import os
from datetime import datetime
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from ..models import Server, Service, Network, ShutdownURLConfiguration, WOLSchedule, Homelab, \
    ServerUptimeStatistic
from ..forms import ServerForm, ServiceForm, NetworkForm, WOLScheduleForm, \
    ShutdownURLConfigurationForm, HomelabForm

@login_required
def create_uptime_statistic(request, server_id):
    '''View to create uptime statistics for a server.'''
    user = request.user
    server = Server.objects.get(id=server_id, user=user)

    if not server:
        messages.error(request, "Server not found")
        return redirect('dashboard_default')

    if server.uptime_statistic.exists():
        messages.error(request, "Uptime statistics already exist for this server")
        return redirect('dashboard_default')

    uptime_statistic = ServerUptimeStatistic.objects.create(server=server)
    uptime_statistic.initialize_matrix()
    uptime_statistic.save()

    messages.success(request, f"Uptime statistics created for server {server.name}")
    return redirect('dashboard_default')

@login_required
def delete_uptime_statistic(request, server_id):
    '''View to delete uptime statistics for a server.'''
    user = request.user
    server = Server.objects.get(id=server_id, user=user)

    if not server:
        messages.error(request, "Server not found")
        return redirect('dashboard_default')

    if not server.uptime_statistic.exists():
        messages.error(request, "Uptime statistics do not exist for this server")
        return redirect('dashboard_default')

    for uptime_statistic in server.uptime_statistic.all():
        uptime_statistic.delete()
    server.save()

    messages.success(request, f"Uptime statistics deleted for server {server.name}")
    return redirect('dashboard_default')

@login_required
def reset_uptime_statistic(request, server_id):
    '''View to reset uptime statistics for a server.'''
    user = request.user
    server = Server.objects.get(id=server_id, user=user)

    if not server:
        messages.error(request, "Server not found")
        return redirect('dashboard_default')

    if not server.uptime_statistic.exists():
        messages.error(request, "Uptime statistics do not exist for this server")
        return redirect('dashboard_default')

    for uptime_statistic in server.uptime_statistic.all():
        uptime_statistic.initialize_matrix()
        uptime_statistic.last_updated = datetime.now()
        uptime_statistic.save()

    messages.success(request, f"Uptime statistics reset for server {server.name}")
    return redirect('dashboard_default')
