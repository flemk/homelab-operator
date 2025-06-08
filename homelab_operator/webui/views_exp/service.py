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
def create_service(request):
    user = request.user

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.user = user
            service.save()
            messages.success(request, f"Service {service.name} created successfully")
            return redirect('dashboard_default')
    else:
        form = ServiceForm()

    context = {
        'form': form,
        'form_title': 'Create Service',
    }
    return render(request, 'html_components/form.html', context)

@login_required
def edit_service(request, service_id):
    user = request.user
    service = Service.objects.get(id=service_id)
    if service.server.user != user:
        messages.error(request, "You do not have permission to edit this service")
        return redirect('dashboard_default')

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save()
            service.user = user
            service.save()
            messages.success(request, f"Service {service.name} updated successfully")
            return redirect('dashboard_default')
    else:
        form = ServiceForm(instance=service)

    context = {
        'form': form,
        'form_title': 'Edit Service',
        'show_delete_option': True,
        'delete_url_confirmed': f"/delete/service/{service.id}/",
        'delete_url_declined': f"/edit/service/{service.id}/",
        'delete_title': 'Delete Service',
        'delete_message':
            f"You are about to delete Service {service.name}. Do you want to proceed?",
    }
    return render(request, 'html_components/form.html', context)

@login_required
def delete_service(request, service_id):
    user = request.user
    service = Service.objects.get(id=service_id)

    if service.server.user != user:
        messages.error(request, "You do not have permission to delete this service")
        return redirect('dashboard_default')

    service_name = service.name
    service.delete()
    messages.success(request, f"Service {service_name} deleted successfully")
    return redirect('dashboard_default')
