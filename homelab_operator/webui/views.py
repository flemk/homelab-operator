import os
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Server, Service, Network
from .forms import ServerForm, ServiceForm, NetworkForm, WOLScheduleForm
from datetime import datetime
from .models import WOLSchedule, Server

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
        if response is True:
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
    }
    return render(request, 'html_components/form.html', context)

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
    }
    return render(request, 'html_components/form.html', context)

@login_required
def create_schedule(request):
    user = request.user

    if request.method == 'POST':
        form = WOLScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = user
            schedule.save()
            messages.success(request, f"Schedule created successfully")
            return redirect('dashboard')
    else:
        form = WOLScheduleForm(user=user)

    context = {
        'form': form,
        'form_title': 'Create Schedule',
    }
    return render(request, 'html_components/form.html', context)

def cron(request, api_key):
    # This function will be called by the cron job
    # It should check the schedules and send WOL packets if needed
    # TODO make this callable locally only

    if api_key != os.environ.get('API_KEY', 'DEFAULT_API_KEY'):
        return HttpResponseForbidden("Unauthorized access")

    now = datetime.now()
    schedules = WOLSchedule.objects.filter(
        enabled=True,
        schedule_time__hour=now.hour,
        schedule_time__minute__gte=(now.minute - 5) % 60,
        schedule_time__minute__lte=(now.minute + 5) % 60
    )

    for schedule in schedules:
        server = schedule.server
        if server:
            if schedule.type == 'WAKE':
                response = server.wake()
                if response is False:
                    print(f"Magic packet sent to {server.name} (Scheduled by {schedule.user.username})")
                else:
                    print(f"Failed to send magic packet to {server.name}: {response}")
            elif schedule.type == 'SHUTDOWN':
                response = server.shutdown()
                if response is True:
                    print(f"Shutdown command sent to {server.name} (Scheduled by {schedule.user.username})")
                else:
                    print(f"Failed to send shutdown command to {server.name}: {response}")
        else:
            print(f"Server not found for schedule ID {schedule.id}")

    return HttpResponse("Cron job executed successfully")