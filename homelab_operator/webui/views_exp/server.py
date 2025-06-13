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

    context = {
        'form': form,
        'form_title': 'Edit Server',
        'show_delete_option': True,
        'delete_url_confirmed': f"/delete/server/{server.id}/",
        'delete_url_declined': f"/edit/server/{server.id}/",
        'delete_title': 'Delete Server',
        'delete_message': f"You are about to delete Server {server.name}. Do you want to proceed?",
    }
    if server.shutdown_url:
        if server.shutdown_url.all().first():  # TODO this caused some issues
            context['additional_information'] = [
                {
                    'title': 'A Shutdown Adapter is configured for this server',
                    'description': 'A shutdown URL is configured as Shutdown Adapter. It can be configured separately.',
                    'link': '/edit/shutdown_url/' + str(server.shutdown_url.all().first().id) + '/',
                    'link_text': 'View',
                },
            ]
        else:
            context['additional_information'] = [
                {
                    'title': 'No shutdown URL configured',
                    'description':
                        'You can create a Shutdown Adapter for this server to allow remote shutdown.',
                    'link': f'/create/shutdown_url/{server.id}',
                    'link_text': 'Create Shutdown URL',
                },
            ]
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
