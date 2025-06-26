import os
from datetime import datetime
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from ..models import Server, Service, Network, ShutdownURLConfiguration, WOLSchedule, Homelab, Wiki
from ..forms import ServerForm, ServiceForm, NetworkForm, WOLScheduleForm, \
    ShutdownURLConfigurationForm, HomelabForm, WikiForm

def public_wiki(request, wiki_id):
    wiki = get_object_or_404(Wiki, id=wiki_id)
    if wiki.public:
        context = {
            'wiki': wiki,
        }
        return render(request, 'html/public_wiki.html', context)
    else:
        return redirect('dashboard_default')
    
@login_required
def create_wiki(request, homelab_id):
    user = request.user
    homelab = Homelab.objects.get(id=homelab_id, user=user)

    if request.method == 'POST':
        form = WikiForm(request.POST)
        if form.is_valid():
            wiki = form.save(commit=False)
            wiki.homelab = homelab
            wiki.save()
            messages.success(request, f"Wiki for {homelab.name} created successfully")
            return redirect('dashboard', homelab_id=homelab.id)
    else:
        form = WikiForm()

    context = {
        'form': form,
        'form_title': 'Create Wiki',
    }
    return render(request, 'html_components/form.html', context)

@login_required
def edit_wiki(request, wiki_id):
    user = request.user
    wiki = Wiki.objects.get(id=wiki_id, homelab__user=user)

    if request.method == 'POST':
        form = WikiForm(request.POST, instance=wiki)
        if form.is_valid():
            wiki = form.save()
            messages.success(request, f"Wiki {wiki.title} updated successfully")
            return redirect('dashboard', homelab_id=wiki.homelab.id)
    else:
        form = WikiForm(instance=wiki)

    context = {
        'form': form,
        'form_title': 'Edit Wiki',
        'show_delete_option': True,
        'delete_url_confirmed': f"/delete/wiki/{wiki.id}/",
        'delete_url_declined': f"/edit/wiki/{wiki.id}/",
        'delete_title': 'Delete Wiki',
        'delete_message':
            f"You are about to delete Wiki {wiki.title}. Do you want to proceed?",
    }
    return render(request, 'html_components/form.html', context)

@login_required
def delete_wiki(request, wiki_id):
    user = request.user
    wiki = Wiki.objects.get(id=wiki_id, homelab__user=user)

    if wiki.homelab.user != user:
        messages.error(request, "You do not have permission to delete this wiki")
        return redirect('dashboard', homelab_id=wiki.homelab.id)

    if wiki:
        wiki_title = wiki.title
        wiki.delete()
        messages.success(request, f"Wiki {wiki_title} deleted successfully")
    else:
        messages.error(request, "Wiki not found")

    return redirect('dashboard', homelab_id=wiki.homelab.id)
