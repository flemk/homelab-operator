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
def create_network(request):
    user = request.user

    if request.method == 'POST':
        form = NetworkForm(request.POST)
        if form.is_valid():
            network = form.save(commit=False)
            network.user = user
            network.save()
            messages.success(request, f"Network {network.name} created successfully")
            return redirect('dashboard_default')
    else:
        form = NetworkForm(user=user)

    context = {
        'form': form,
        'form_title': 'Create Network',
    }
    return render(request, 'html_components/form.html', context)

@login_required
def edit_network(request, network_id):
    user = request.user
    network = Network.objects.get(id=network_id, user=user)

    if request.method == 'POST':
        form = NetworkForm(request.POST, instance=network)
        if form.is_valid():
            network = form.save()
            network.user = user
            network.save()
            messages.success(request, f"Network {network.name} updated successfully")
            return redirect('dashboard_default')
    else:
        form = NetworkForm(instance=network, user=user)

    context = {
        'form': form,
        'form_title': 'Edit Network',
        'show_delete_option': True,
        'delete_url_confirmed': f"/delete/network/{network.id}/",
        'delete_url_declined': f"/edit/network/{network.id}/",
        'delete_title': 'Delete Network',
        'delete_message':
            f"You are about to delete Network {network.name}. Do you want to proceed?",
    }
    return render(request, 'html_components/form.html', context)

@login_required
def delete_network(request, network_id):
    user = request.user
    network = Network.objects.get(id=network_id, user=user)

    if network.user != user:
        messages.error(request, "You do not have permission to delete this network")
        return redirect('dashboard_default')

    network_name = network.name
    network.delete()
    messages.success(request, f"Network {network_name} deleted successfully")
    return redirect('dashboard_default')
