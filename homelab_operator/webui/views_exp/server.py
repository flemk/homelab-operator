import os
from datetime import datetime
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from ..models import Server, Service, Network, ShutdownURLConfiguration, WOLSchedule, Homelab
from ..forms import ServerForm, ServiceForm, NetworkForm, WOLScheduleForm, \
    ShutdownURLConfigurationForm, HomelabForm

@login_required
def edit_server(request, server_id):
    user = request.user
    server = Server.objects.get(id=server_id, user=user)

    if request.method == 'POST':
        form = ServerForm(request.POST, instance=server)
        if form.is_valid():
            server = form.save()
            server.user = user
            server.save()
            messages.success(request, f"Server {server.name} updated successfully")
            return redirect('dashboard_default')
    else:
        form = ServerForm(instance=server, user=user)

    additional_information = []
    if server.shutdown_url:
        if server.shutdown_url.all().first():
            additional_information.append(
                {
                    'title': 'A Shutdown Adapter is configured for this server',
                    'description': 'A shutdown URL is configured as Shutdown Adapter. It can be configured separately.',
                    'links': [
                        {
                            'url': '/edit/shutdown_url/' + str(server.shutdown_url.all().first().id) + '/',
                            'label': 'View',
                        }
                    ]
                }
            )
        else:
            additional_information.append(
                {
                    'title': 'No Shutdown Adapter configured',
                    'description':
                        'You can create a Shutdown Adapter for this server to allow remote shutdown.',
                    'links': [
                        {
                            'url': f'/create/shutdown_url/{server.id}',
                            'label': 'Create Shutdown Adapter',
                        }
                    ]
                }
            )

    if server.uptime_statistic.all():
        additional_information.append(
            {
                'title': 'Uptime Statistics',
                'description': 'This server has uptime statistics enabled.',
                'links': [
                    {
                        'url': f'/reset/uptime_statistic/{server.id}/',
                        'label': 'Reset',
                        'fa_icon': 'fa-rotate',
                    },
                    {
                        'url': f'/delete/uptime_statistic/{server.id}/',
                        'label': 'Delete',
                        'fa_icon': 'fa-trash-can',
                    }
                ]
            }
        )
    else:
        additional_information.append(
            {
                'title': 'No Uptime Statistics',
                'description': 'Uptime statistics are not enabled for this server.',
                'links': [
                    {
                        'url': f'/create/uptime_statistic/{server.id}/',
                        'label': 'Enable',
                        'fa_icon': 'fa-plus',
                    }
                ]
            }
        )
    
    if server.maintenance_plans.all():
        additional_information.append(
            {
                'title': 'Maintenance Plans',
                'description': 'This server has maintenance plans configured.',
                'links': [
                    {
                        'url': f'/edit/maintenance_plan/{server.maintenance_plans.all().first().id}/',
                        'label': 'View',
                    },
                ]
            }
        )
    else:
        additional_information.append(
            {
                'title': 'No Maintenance Plans',
                'description': 'No maintenance plans are configured for this server.',
                'links': [
                    {
                        'url': f'/create/maintenance_plan/{server.id}/',
                        'label': 'Create Maintenance Plan',
                        'fa_icon': 'fa-plus',
                    }
                ]
            }
        )

    context = {
        'form': form,
        'form_title': 'Edit Server',
        'show_delete_option': True,
        'delete_url_confirmed': f"/delete/server/{server.id}/",
        'delete_url_declined': f"/edit/server/{server.id}/",
        'delete_title': 'Delete Server',
        'delete_message': f"You are about to delete Server {server.name}. Do you want to proceed?",
        'additional_information': additional_information,
    }
    return render(request, 'html_components/form.html', context)

@login_required
def delete_server(request, server_id):
    user = request.user
    server = Server.objects.get(id=server_id, user=user)

    if server.user != user:
        messages.error(request, "You do not have permission to delete this server")
        return redirect('dashboard_default')

    if server:
        server_name = server.name
        server.delete()
        messages.success(request, f"Server {server_name} deleted successfully")
        return redirect('dashboard_default')

    messages.error(request, "Server not found")
    return redirect('dashboard_default')

@login_required
def create_server(request):
    user = request.user

    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            server = form.save(commit=False)
            server.user = user
            server.save()
            messages.success(request, f"Server {server.name} created successfully")
            return redirect('dashboard_default')
    else:
        form = ServerForm(user=user)

    context = {
        'form': form,
        'form_title': 'Create Server',
    }
    return render(request, 'html_components/form.html', context)
