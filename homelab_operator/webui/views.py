import os
from datetime import datetime
from datetime import datetime
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Server, Service, Network, ShutdownURLConfiguration, WOLSchedule, Homelab
from .forms import ServerForm, ServiceForm, NetworkForm, WOLScheduleForm, \
    ShutdownURLConfigurationForm, HomelabForm, UserProfileForm

from .views_exp.homelab import create_homelab, edit_homelab, delete_homelab
from .views_exp.server import edit_server, delete_server, create_server
from .views_exp.service import create_service, edit_service, delete_service
from .views_exp.network import create_network, edit_network, delete_network
from .views_exp.schedule import create_schedule, edit_schedule, delete_schedule
from .views_exp.shutdown_url import create_shutdown_url, edit_shutdown_url, delete_shutdown_url
from .views_exp.wiki import create_wiki, edit_wiki, delete_wiki

def login_view(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return dashboard(request)
        context['login_error'] = 'Invalid credentials'

    if request.user.is_authenticated:
        return redirect('dashboard', homelab_id=None)

    return render(request, 'html/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def edit_profile(request):
    '''View to edit the user's profile.'''
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('dashboard_default')
    else:
        form = UserProfileForm(instance=profile, user=user)

    context = {
        'form': form,
        'user': user,
        'form_title': 'Edit User Profile',
    }
    return render(request, 'html_components/form.html', context)

@login_required
def dashboard(request, homelab_id=None):
    '''Dashboard view for the user, showing servers, networks, and homelabs.'''
    user = request.user

    if homelab_id is None:
        if user.profile.last_selected_homelab:
            homelab_id = user.profile.last_selected_homelab.id
        elif user.homelabs.exists():
            homelab_id = user.homelabs.first().id
        else:
            messages.info(request, "No homelabs found for this user")
            context = {
                'homelab': None,
                'homelabs': None,
            }
            return render(request, 'html/dashboard.html', context)
    else:
        user.profile.last_selected_homelab = Homelab.objects.get(id=homelab_id)
        user.profile.save()

    homelab = user.homelabs.get(id=homelab_id)
    homelabs = user.homelabs.all()
    servers = homelab.servers.all()
    networks = homelab.networks.all()
    
    context = {
        'servers': servers,
        'networks': networks,
        'homelabs': homelabs,
        'homelab': homelab,
        'wiki': homelab.wiki.first() if homelab.wiki.exists() else None,
        'user_show_wiki': user.profile.show_wiki,
        'user_show_networks': user.profile.show_networks,
    }
    return render(request, 'html/dashboard.html', context)

@login_required
def wake(request, server_id):
    user = request.user
    server = Server.objects.get(id=server_id, user=user)
    if server:
        response = server.wake()
        if response is False:
            messages.success(request, f"Magic packet sent to {server.name}")
        else:
            messages.error(request, f"Failed to send magic packet to {server.name}: {response}")
        return redirect('dashboard_default')
    messages.error(request, "Server not found")
    return redirect('dashboard_default')

@login_required
def shutdown(request, server_id):
    user = request.user
    server = Server.objects.get(id=server_id, user=user)
    if server:
        response = server.shutdown()
        if response is False:
            messages.success(request, f"Shutdown command sent to {server.name}")
        else:
            messages.error(request, f"Failed to send shutdown command to {server.name}: {response}")
        return redirect('dashboard_default')
    messages.error(request, "Server not found")
    return redirect('dashboard_default')

@login_required
def create_shutdown_url(request, server_id):
    user = request.user
    server = Server.objects.get(id=server_id, user=user)

    if not server:
        messages.error(request, "Server not found")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ShutdownURLConfigurationForm(request.POST)
        if form.is_valid():
            shutdown_url = form.save(commit=False)
            shutdown_url.server = server
            shutdown_url.save()
            messages.success(request, f"Shutdown URL created successfully for {server.name}")
            return redirect('dashboard')
    else:
        form = ShutdownURLConfigurationForm(server=server)

    context = {
        'form': form,
        'form_title': f'Create Shutdown URL for {server.name}',
    }
    return render(request, 'html_components/form.html', context)

@login_required
def edit_shutdown_url(request, shutdown_url_id):
    user = request.user
    shutdown_url = ShutdownURLConfiguration.objects.get(id=shutdown_url_id)

    if shutdown_url.server.user != user:
        messages.error(request, "You do not have permission to edit this shutdown URL")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ShutdownURLConfigurationForm(request.POST, instance=shutdown_url)
        if form.is_valid():
            shutdown_url = form.save()
            messages.success(request, f"Shutdown URL {shutdown_url.name} updated successfully")
            return redirect('dashboard')
    else:
        form = ShutdownURLConfigurationForm(instance=shutdown_url)

    context = {
        'form': form,
        'form_title': f'Edit Shutdown URL for {shutdown_url.server.name}',
        'show_delete_option': True,
        'delete_url_confirmed': f"/delete/shutdown_url/{shutdown_url.id}/",
        'delete_url_declined': f"/edit/shutdown_url/{shutdown_url.id}/",
        'delete_title': 'Delete Shutdown URL',
        'delete_message':
            f"You are about to delete Shutdown URL {shutdown_url.name}. Do you want to proceed?",
    }
    return render(request, 'html_components/form.html', context)

@login_required
def delete_shutdown_url(request, shutdown_url_id):
    user = request.user
    shutdown_url = ShutdownURLConfiguration.objects.get(id=shutdown_url_id)

    if shutdown_url.server.user != user:
        messages.error(request, "You do not have permission to delete this shutdown URL")
        return redirect('dashboard')

    shutdown_url_name = shutdown_url.name
    shutdown_url.delete()
    messages.success(request, f"Shutdown URL {shutdown_url_name} deleted successfully")
    return redirect('dashboard')

def cron(request, api_key):
    '''This function will be called by the cron job
    It should check the schedules and send WOL packets if needed'''
    # TODO make this callable locally only

    if api_key != os.environ.get('API_KEY', 'DEFAULT_API_KEY'):
        return HttpResponseForbidden("Forbidden", status=403)

    now = datetime.now()
    minute_window = [(now.minute + offset) % 60 for offset in range(-5, 6)]
    minute_window = [(now.minute + offset) % 60 for offset in range(-5, 6)]
    schedules = WOLSchedule.objects.filter(
        enabled=True,
        schedule_time__hour=now.hour,
        schedule_time__minute__in=minute_window
    )

    for schedule in schedules.all():
        if schedule.repeat:
            if schedule.repeat_type == 'daily':
                # schedule should be executed every day, no action needed
                continue
            if schedule.repeat_type == 'weekly':
                if schedule.schedule_time.weekday() != now.weekday():
                    schedules.exclude(id=schedule.id)
            elif schedule.repeat_type == 'monthly':
                if schedule.schedule_time.month != now.month \
                    and schedule.schedule_time.day != now.day:
                    schedules.exclude(id=schedule.id)
        else:
            if schedule.schedule_time.date() != now.date():
                schedules.exclude(id=schedule.id)

    for schedule in schedules:
        server = schedule.server
        if server:
            if not server.auto_wake:
                continue
            if not server.auto_wake:
                continue
            if schedule.type == 'WAKE':
                response = server.wake()
                if response is False:
                    print(f"Magic packet sent to {server.name}" + \
                          f"(Scheduled by {schedule.user.username})")
                    print(f"Magic packet sent to {server.name}" + \
                          f"(Scheduled by {schedule.user.username})")
                else:
                    print(f"Failed to send magic packet to {server.name}: {response}")
            elif schedule.type == 'SHUTDOWN':
                response = server.shutdown()
                if response is True:
                    print(f"Shutdown command sent to {server.name} " + \
                          f"(Scheduled by {schedule.user.username})")
                    print(f"Shutdown command sent to {server.name} " + \
                          f"(Scheduled by {schedule.user.username})")
                else:
                    print(f"Failed to send shutdown command to {server.name}: {response}")
        else:
            print(f"Server not found for schedule ID {schedule.id}")

    return HttpResponse("OK", status=200)

@login_required
def confirm(request):
    if request.method == 'POST':
        redirect_url_confirmed = request.POST.get('redirect_url_confirmed')
        redirect_url_declined = request.POST.get('redirect_url_declined')
        title = request.POST.get('title')
        message = request.POST.get('message')

        context = {
            'redirect_url_confirmed': redirect_url_confirmed,
            'redirect_url_declined': redirect_url_declined,
            'title': title,
            'message': message,
        }
        return render(request, 'html_components/confirm.html', context)
    return HttpResponseBadRequest()
