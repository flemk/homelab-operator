from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Server
from .forms import ServerForm

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

    context = {
        'servers': servers,
    }
    return render(request, 'html/dashboard.html', context)

@login_required
def wake(request, server_id):
    server = Server.objects.get(id=server_id)
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
def edit_server(request, server_id):
    user = request.user
    server = Server.objects.get(id=server_id)

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
