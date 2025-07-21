from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Homelab
from ..forms import HomelabForm

@login_required
def create_homelab(request):
    user = request.user

    if request.method == 'POST':
        form = HomelabForm(request.POST)
        if form.is_valid():
            homelab = form.save(commit=False)
            homelab.user = user
            homelab.save()
            messages.success(request, f"Homelab {homelab.name} created successfully")
            return redirect('dashboard', homelab_id=homelab.id)
    else:
        form = HomelabForm(user=user)

    context = {
        'form': form,
        'form_title': 'Create Homelab',
    }
    return render(request, 'html_components/form.html', context)

@login_required
def edit_homelab(request, homelab_id):
    user = request.user
    homelab = Homelab.objects.get(id=homelab_id, user=user)

    if request.method == 'POST':
        form = HomelabForm(request.POST, instance=homelab)
        if form.is_valid():
            homelab = form.save()
            homelab.user = user
            homelab.save()
            messages.success(request, f"Homelab {homelab.name} updated successfully")
            return redirect('dashboard', homelab_id=homelab.id)
    else:
        form = HomelabForm(instance=homelab, user=user)

    context = {
        'form': form,
        'form_title': 'Edit Homelab',
        'show_delete_option': True,
        'delete_url_confirmed': f"/delete/homelab/{homelab.id}/",
        'delete_url_declined': f"/edit/homelab/{homelab.id}/",
        'delete_title': 'Delete Homelab',
        'delete_message':
            f"You are about to delete Homelab {homelab.name}. Do you want to proceed?",
    }
    return render(request, 'html_components/form.html', context)

@login_required
def delete_homelab(request, homelab_id):
    user = request.user
    homelab = Homelab.objects.get(id=homelab_id, user=user)

    if homelab.user != user:
        messages.error(request, "You do not have permission to delete this homelab")
        return redirect('dashboard_default')

    if homelab:
        homelab_name = homelab.name
        homelab.delete()
        messages.success(request, f"Homelab {homelab_name} deleted successfully")
        return redirect('dashboard_default')

    messages.error(request, "Homelab not found")
    return redirect('dashboard_default')
