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
def create_schedule(request):
    user = request.user

    if request.method == 'POST':
        form = WOLScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = user
            schedule.save()
            messages.success(request, "Schedule created successfully")
            return redirect('dashboard_default')
    else:
        form = WOLScheduleForm(user=user)

    context = {
        'form': form,
        'form_title': 'Create Schedule',
    }
    return render(request, 'html_components/form.html', context)

@login_required
def edit_schedule(request, schedule_id):
    user = request.user
    schedule = WOLSchedule.objects.get(id=schedule_id)

    if schedule.user != user:
        messages.error(request, "You do not have permission to edit this schedule")
        return redirect('dashboard_default')

    if request.method == 'POST':
        form = WOLScheduleForm(request.POST, instance=schedule, user=user)
        if form.is_valid():
            schedule = form.save()
            schedule.user = user
            schedule.save()
            messages.success(request, "Schedule updated successfully")
            return redirect('dashboard_default')
    else:
        form = WOLScheduleForm(instance=schedule, user=user)

    context = {
        'form': form,
        'form_title': 'Edit Schedule',
        'show_delete_option': True,
        'delete_url_confirmed': f"/delete/schedule/{schedule.id}/",
        'delete_url_declined': f"/edit/schedule/{schedule.id}/",
        'delete_title': 'Delete Schedule',
        'delete_message':
            f"You are about to delete Schedule {schedule.id} for {schedule.server.name}. " + \
                "Do you want to proceed?",
    }
    return render(request, 'html_components/form.html', context)

@login_required
def delete_schedule(request, schedule_id):
    user = request.user
    schedule = WOLSchedule.objects.get(id=schedule_id)

    if schedule.user != user:
        messages.error(request, "You do not have permission to delete this schedule")
        return redirect('dashboard_default')

    schedule_id = schedule.id
    schedule.delete()
    messages.success(request, f"Schedule {schedule_id} deleted successfully")
    return redirect('dashboard_default')
