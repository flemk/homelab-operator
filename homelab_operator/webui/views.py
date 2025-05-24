import os
from datetime import datetime
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Server, Service, Network, ShutdownURLConfiguration, WOLSchedule
from .forms import ServerForm, ServiceForm, NetworkForm, WOLScheduleForm, \
    ShutdownURLConfigurationForm

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
        return redirect('dashboard')

    return render(request, 'html/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    servers = Server.objects.filter(user=user)
    networks = Network.objects.filter(user=user)

    context = {
        'servers': servers,
        'networks': networks,
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
        return redirect('dashboard')
    messages.error(request, "Server not found")
    return redirect('dashboard')

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
        return redirect('dashboard')
    messages.error(request, "Server not found")
    return redirect('dashboard')

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
            return redirect('dashboard')
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
                    'title': 'A shutdown URL is configured for this server',
                    'description': 'The shutdown URL is configured separately.',
                    'link': '/edit/shutdown_url/' + str(server.shutdown_url.all().first().id) + '/',
                    'link_text': 'View',
                },
            ]
        else:
            context['additional_information'] = [
                {
                    'title': 'No shutdown URL configured',
                    'description':
                        'You can create a shutdown URL for this server to allow remote shutdown.',
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
        return redirect('dashboard')

    if server:
        server_name = server.name
        server.delete()
        messages.success(request, f"Server {server_name} deleted successfully")
        return redirect('dashboard')

    messages.error(request, "Server not found")
    return redirect('dashboard')

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
            return redirect('dashboard')
    else:
        form = ServerForm(user=user)

    context = {
        'form': form,
        'form_title': 'Create Server',
    }
    return render(request, 'html_components/form.html', context)

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
            return redirect('dashboard')
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
        return redirect('dashboard')

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save()
            service.user = user
            service.save()
            messages.success(request, f"Service {service.name} updated successfully")
            return redirect('dashboard')
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
        return redirect('dashboard')

    service_name = service.name
    service.delete()
    messages.success(request, f"Service {service_name} deleted successfully")
    return redirect('dashboard')

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
            return redirect('dashboard')
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
            return redirect('dashboard')
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
        return redirect('dashboard')

    network_name = network.name
    network.delete()
    messages.success(request, f"Network {network_name} deleted successfully")
    return redirect('dashboard')

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
            return redirect('dashboard')
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
        return redirect('dashboard')

    if request.method == 'POST':
        form = WOLScheduleForm(request.POST, instance=schedule, user=user)
        if form.is_valid():
            schedule = form.save()
            schedule.user = user
            schedule.save()
            messages.success(request, "Schedule updated successfully")
            return redirect('dashboard')
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
        return redirect('dashboard')

    schedule_id = schedule.id
    schedule.delete()
    messages.success(request, f"Schedule {schedule_id} deleted successfully")
    return redirect('dashboard')

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

    for schedule in schedules:
        server = schedule.server
        if server:
            if not server.auto_wake:
                continue
            if schedule.type == 'WAKE':
                response = server.wake()
                if response is False:
                    print(f"Magic packet sent to {server.name}" + \
                          f"(Scheduled by {schedule.user.username})")
                else:
                    print(f"Failed to send magic packet to {server.name}: {response}")
            elif schedule.type == 'SHUTDOWN':
                response = server.shutdown()
                if response is True:
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
