from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import json
import time

from ..models import Homelab, Ingress
from ..forms import IngressForm
from ..helpers.helpers import generate_ingress_nginx_config

@login_required
def ingress(request, homelab_id):
    """List all ingress rules for a homelab."""
    homelab = get_object_or_404(Homelab, id=homelab_id, user=request.user)
    ingresses = Ingress.objects.filter(homelab=homelab).select_related('target_service', 'target_service__server')

    context = {
        'homelab': homelab,
        'ingresses': ingresses,
    }
    return render(request, 'html/ingress.html', context)

@login_required
def create_ingress(request, homelab_id):
    """Create a new ingress rule."""
    homelab = get_object_or_404(Homelab, id=homelab_id, user=request.user)

    if request.method == 'POST':
        form = IngressForm(request.POST, user=request.user, homelab=homelab)
        if form.is_valid():
            ingress = form.save(commit=False)
            ingress.user = request.user
            ingress.homelab = homelab
            ingress.save()

            # Regenerate nginx config
            try:
                #raise NotImplementedError("Nginx config generation not implemented")
                generate_ingress_nginx_config(ingress)
                messages.success(request, f'Ingress rule "{ingress.name}" created successfully!')
            except Exception as e:
                messages.warning(request, f'Rule created but nginx config update failed: {str(e)}')

            return redirect('ingress_list', homelab_id=homelab.id)
    else:
        form = IngressForm(user=request.user, homelab=homelab)

    context = {
        'form': form,
        'form_title': 'Create Ingress',
    }
    return render(request, 'html_components/form.html', context)

@login_required
def edit_ingress(request, ingress_id):
    """Edit an existing ingress rule."""
    ingress = get_object_or_404(Ingress, id=ingress_id, user=request.user)
    
    if request.method == 'POST':
        form = IngressForm(request.POST, instance=ingress, user=request.user, homelab=ingress.homelab)
        if form.is_valid():
            form.save()
            
            # Regenerate nginx config
            try:
                raise NotImplementedError("Nginx config generation not implemented")
                generate_nginx_config()
                messages.success(request, f'Ingress rule "{ingress.name}" updated successfully!')
            except Exception as e:
                messages.warning(request, f'Rule updated but nginx config update failed: {str(e)}')
            
            return redirect('ingress_list', homelab_id=ingress.homelab.id)
    else:
        form = IngressForm(instance=ingress, user=request.user, homelab=ingress.homelab)
    
    context = {
        'form': form,
        'form_title': 'Create Ingress',
        'show_delete_option': True,
        'delete_url_confirmed': f"/delete/ingress/{ingress.id}/",
        'delete_url_declined': f"/edit/ingress/{ingress.id}/",
        'delete_title': 'Delete Ingress',
        'delete_message': f"You are about to delete Ingress {ingress.name}. Do you want to proceed?",
    }
    return render(request, 'html_components/form.html', context)

@login_required
def delete_ingress(request, ingress_id):
    """Delete an ingress rule."""
    ingress = get_object_or_404(Ingress, id=ingress_id, user=request.user)
    homelab_id = ingress.homelab.id

    ingress.delete()

    # Regenerate nginx config
    try:
        raise NotImplementedError("Nginx config generation not implemented")
        generate_nginx_config()
        messages.success(request, f'Ingress rule "{ingress.name}" deleted successfully!')
    except Exception as e:
        messages.warning(request, f'Rule deleted but nginx config update failed: {str(e)}')

    return redirect('ingress_list', homelab_id=homelab_id)
