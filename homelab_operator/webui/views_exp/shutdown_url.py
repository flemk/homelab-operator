from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Server, ShutdownURLConfiguration
from ..forms import ShutdownURLConfigurationForm

@login_required
def create_shutdown_url(request, server_id):
    user = request.user
    server = Server.objects.get(id=server_id, user=user)

    if not server:
        messages.error(request, "Server not found")
        return redirect('dashboard_default')

    if request.method == 'POST':
        form = ShutdownURLConfigurationForm(request.POST)
        if form.is_valid():
            shutdown_url = form.save(commit=False)
            shutdown_url.server = server
            shutdown_url.save()
            messages.success(request, f"Shutdown URL created successfully for {server.name}")
            return redirect('dashboard_default')
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
        return redirect('dashboard_default')

    if request.method == 'POST':
        form = ShutdownURLConfigurationForm(request.POST, instance=shutdown_url)
        if form.is_valid():
            shutdown_url = form.save()
            messages.success(request, f"Shutdown URL {shutdown_url.name} updated successfully")
            return redirect('dashboard_default')
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
        return redirect('dashboard_default')

    shutdown_url_name = shutdown_url.name
    shutdown_url.delete()
    messages.success(request, f"Shutdown URL {shutdown_url_name} deleted successfully")
    return redirect('dashboard_default')
