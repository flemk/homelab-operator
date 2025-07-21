from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.html import format_html
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Homelab, MaintenancePlan, \
    MaintenanceReport
from ..forms import MaintenancePlanForm, MaintenanceReportForm

@login_required
def maintenance(request, homelab_id):
    '''View to display maintenance plans for a specific homelab.'''
    user = request.user
    homelab = get_object_or_404(Homelab, id=homelab_id, user=user)
    
    maintenance_plans_upcoming = homelab.maintenance_plans.filter(
        scheduled_date__gte=timezone.now(), repeat_interval=0)
    maintenance_plans_repeat = homelab.maintenance_plans.filter(
        repeat_interval__gt=0)
    maintenance_plans_past = homelab.maintenance_plans.filter(
        scheduled_date__lt=timezone.now(), repeat_interval=0).order_by('-scheduled_date')
    
    reports = MaintenanceReport.objects.filter(maintenance_plan__homelab=homelab).order_by('-date')

    context = {
        'homelab': homelab,
        'maintenance_plans_upcoming': maintenance_plans_upcoming,
        'maintenance_plans_repeat': maintenance_plans_repeat,
        'maintenance_plans_past': maintenance_plans_past,
        'reports': reports,
    }
    return render(request, 'html/maintenance.html', context)

@login_required
def create_maintenance(request, homelab_id):
    '''View to create a new maintenance plan for a specific homelab.'''
    user = request.user
    homelab = get_object_or_404(Homelab, id=homelab_id, user=user)

    if request.method == 'POST':
        form = MaintenancePlanForm(request.POST, user=user, homelab=homelab)
        if form.is_valid():
            maintenance_plan = form.save(commit=False)
            maintenance_plan.homelab = homelab
            maintenance_plan.save()
            messages.success(request, "Maintenance plan created successfully")
            return redirect('maintenance', homelab_id=homelab.id)
    else:
        form = MaintenancePlanForm(user=user, homelab=homelab)

    context = {
        'form': form,
        'form_title': 'Create Maintenance Plan',
        'homelab': homelab,
    }
    return render(request, 'html_components/form.html', context)

@login_required
def edit_maintenance(request, maintenance_id):
    '''View to edit an existing maintenance plan.'''
    user = request.user
    maintenance_plan = get_object_or_404(MaintenancePlan, id=maintenance_id, homelab__user=user)
    homelab = maintenance_plan.homelab

    if request.method == 'GET' and request.GET.get('delete', '') == 'True':
        maintenance_plan.delete()
        messages.success(request, "Maintenance plan deleted successfully")
        return redirect('maintenance', homelab_id=homelab.id)

    if request.method == 'POST':
        form = MaintenancePlanForm(request.POST, instance=maintenance_plan, user=user, homelab=homelab)
        if form.is_valid():
            form.save()
            messages.success(request, "Maintenance plan updated successfully")
            return redirect('maintenance', homelab_id=homelab.id)
    else:
        form = MaintenancePlanForm(instance=maintenance_plan, user=user, homelab=homelab)

    context = {
        'form': form,
        'form_title': 'Edit Maintenance Plan',
        'show_delete_option': True,
        'delete_url_confirmed': f"/edit/maintenance/{maintenance_plan.id}/?delete=True",
        'delete_url_declined': f"/edit/maintenance/{maintenance_plan.id}/",
        'delete_title': 'Delete Maintenance Plan',
        'delete_message': f"You are about to delete Maintenance Plan {maintenance_plan.title}. Do you want to proceed?",
    }
    return render(request, 'html_components/form.html', context)

@login_required
def create_report(request, maintenance_id):
    '''View to create a new report for a specific maintenance plan.'''
    user = request.user
    maintenance_plan = get_object_or_404(MaintenancePlan, id=maintenance_id, assignee=user.profile)

    if request.method == 'POST':
        form = MaintenanceReportForm(request.POST, certifier=user.profile, maintenance_plan=maintenance_plan)
        if form.is_valid():
            report = form.save(commit=False)
            report.maintenance_plan = maintenance_plan
            report.save()
            messages.success(request, "Report created successfully")
            return redirect('maintenance', homelab_id=maintenance_plan.homelab.id)
    else:
        form = MaintenanceReportForm(certifier=user.profile, maintenance_plan=maintenance_plan)

    context = {
        'form': form,
        'form_title': 'Create Report',
        'homelab': maintenance_plan.homelab,
    }
    return render(request, 'html_components/form.html', context)

@login_required
def edit_report(request, report_id):
    '''View to edit an existing report for a specific maintenance plan.'''
    user = request.user
    report = get_object_or_404(MaintenanceReport, id=report_id, certifier=user.profile)
    maintenance_plan = report.maintenance_plan
    homelab = maintenance_plan.homelab
    immutable = report.result is not None

    if request.method == 'GET' and request.GET.get('delete', '') == 'True':
        report.delete()
        messages.success(request, "Report deleted successfully")
        return redirect('maintenance', homelab_id=homelab.id)

    if request.method == 'POST':
        messages.error(request, "Editing reports is not allowed when the report is immutable.")
        return redirect('edit_report', report_id=report_id)

        form = MaintenanceReportForm(request.POST, instance=report, certifier=user.profile, maintenance_plan=maintenance_plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Report updated successfully")
            return redirect('maintenance', homelab_id=homelab.id)
    else:
        form = MaintenanceReportForm(instance=report, certifier=user.profile, maintenance_plan=maintenance_plan, immutable=immutable)

    additional_information = []
    if immutable:
        additional_information = [{
            'title': 'Immutable Report',
            'description': format_html(
                f'This report is immutable and cannot be modified. It was created on <strong>{report.date.strftime('%Y-%m-%d %H:%M:%S')}</strong> by <strong>{report.certifier.user.username}</strong>.'),
        }]

    context = {
        'form': form,
        'form_title': 'Edit Report',
        'show_delete_option': True,
        'delete_url_confirmed': f"/edit/report/{report.id}/?delete=True",
        'delete_url_declined': f"/edit/report/{report.id}/",
        'delete_title': 'Delete Report',
        'delete_message': f"You are about to delete Report {report.id}. Do you want to proceed?",
        'additional_information': additional_information,
    }
    return render(request, 'html_components/form.html', context)
