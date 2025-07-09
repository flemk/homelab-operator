from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from ..models import Server, Service, Network, Homelab, \
    AppState
from ..helpers import discover_network_stream

import uuid

@login_required
def auto_discover(request, network_id=None):
    task_id = uuid.uuid4().hex
    context = {
        'network_id': network_id,
        'task_id': task_id,
    }

    return render(request, 'html/auto_discover.html', context)

@login_required
def auto_discover_results(request, network_id=None, task_id=None):
    '''View to auto discover servers and services in the user's homelab network.'''
    user = request.user
    if not user.is_superuser:
        messages.error(request, "Only admins can run discovery.")
        return redirect('dashboard_default')

    if request.method == 'POST':
        homelab_id = None
        if 'homelab_id' in request.POST:
            homelab_id = request.POST.get('homelab_id')
            try:
                homelab = Homelab.objects.get(id=homelab_id, user=user)
                user.profile.last_selected_homelab = homelab
                user.profile.save()
            except Homelab.DoesNotExist:
                messages.error(request, "Homelab not found.")
                return redirect('dashboard_default')
        if not homelab_id:
            messages.error(request, "No homelab selected.")
            return redirect('dashboard_default')

        try:
            network = Network.objects.get(id=network_id, user=user, homelab=homelab)
        except Network.DoesNotExist:
            messages.error(request, "Network not found. Possibly not defined or not in the selected homelab.")
            return redirect('dashboard_default')

        servers = []
        services = []
        for key in request.POST:
            if key.startswith('server_') and len(key.split('_')) == 2:
                checkbox_key = request.POST.get(f'{key}').strip()
                server_name = request.POST.get(f'{key}_name', '').strip()
                server_ip = request.POST.get(f'{key}_ip', '').strip()
                server_mac = request.POST.get(f'{key}_mac', '').strip() or None

                if server_name and server_ip and checkbox_key:
                    servers.append({
                        'name': server_name,
                        'ip_address': server_ip,
                        'mac_address': server_mac,
                    })
            if key.startswith('service_') and len(key.split('_')) == 3:
                checkbox_key = request.POST.get(f'{key}').strip()
                service_name = request.POST.get(f'{key}_name', '').strip()
                service_endpoint = request.POST.get(f'{key}_endpoint', '').strip()
                service_port = request.POST.get(f'{key}_port', '').strip()
                service_url = request.POST.get(f'{key}_url', '').strip()
                service_server_name = request.POST.get(f'{key}_server_name', '').strip()

                if service_name and service_endpoint and checkbox_key:
                    services.append({
                        'name': service_name,
                        'endpoint': service_endpoint,
                        'port': service_port,
                        'url': service_url,
                        'server_name': service_server_name,
                    })

        if not servers:
            messages.error(request, "No valid servers found in the form.")
            return redirect('dashboard_default')

        # Save discovered servers
        for server_data in servers:
            Server.objects.update_or_create(
                user=user,
                name=server_data['name'],
                ip_address=server_data['ip_address'],
                mac_address=server_data['mac_address'],
                homelab=homelab,
                network=network if network in homelab.networks.all() else None,
            )

        # Save discovered services
        for service_data in services:
            server = Server.objects.filter(
                user=request.user,
                ip_address=service_data['endpoint'],
                #name=service_data['server_name'],  # TODO name can be changed, not reliable
                network=network,
                homelab=homelab,
            ).first()
            if server:
                Service.objects.update_or_create(
                    server=server,
                    name=service_data['name'],
                    endpoint=service_data['endpoint'],
                    port=service_data['port'],
                    url=service_data['url'],
                )
            else:
                messages.warning(request, f"Service {service_data['name']} could not be linked to a server.")

        messages.success(request, "Auto discovered result saved successfully.")
        return redirect('dashboard_default')
    
    network = get_object_or_404(Network, id=network_id, user=request.user)
    auto_discover_network = network.subnet
    if not auto_discover_network:
        messages.error(request, "No subnet configured for auto discovery.")
        return redirect('dashboard_default')

    try:
        servers = cache.get(f"scan:{task_id}")
        cache.delete(f"scan:{task_id}")
    except Exception as e:
        messages.error(request, f"Error during auto discovery: {str(e)}")
        app_state = AppState.ensure_exists()
        app_state.add_exception(f"Auto discovery error: {str(e)}")
        return redirect('dashboard_default')
    homelabs = request.user.homelabs.all()

    context = {
        'network_id': network.id,
        'servers': servers,
        'homelabs': homelabs,
        'user': request.user,
        }

    return render(request, 'html/auto_discover_results.html', context)

@login_required
def auto_discover_stream(request, network_id, task_id):
    '''Streaming view to auto discover servers and services in the user's homelab network.'''
    user = request.user
    if not user.is_superuser:
        messages.error(request, "Only admins can run discovery.")
        return redirect('dashboard_default')

    try:
        network = Network.objects.get(id=network_id, user=user)
    except Network.DoesNotExist:
        messages.error(request, "Network not found.")
        return redirect('dashboard_default')

    auto_discover_network = network.subnet
    if not auto_discover_network:
        messages.error(request, "No subnet configured for auto discovery.")
        return redirect('dashboard_default')
    
    response_generator = discover_network_stream(auto_discover_network, task_id)
    streaming_response = StreamingHttpResponse(response_generator, content_type='text/html')
    streaming_response['X-Frame-Options'] = 'SAMEORIGIN'
    streaming_response['Cache-Control'] = 'no-cache'
    streaming_response['X-Accel-Buffering'] = 'no'
    return streaming_response
