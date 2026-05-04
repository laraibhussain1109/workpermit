from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import GovernmentIDForm, WorkPermitForm
from .models import DepartmentMembership, WorkPermitRequest


def _role(user):
    membership = getattr(user, 'department_membership', None)
    return membership.role if membership else None


@login_required
def dashboard(request):
    permits = WorkPermitRequest.objects.filter(requested_by=request.user)
    return render(request, 'permits/dashboard.html', {'permits': permits})


@login_required
def create_request(request):
    form = WorkPermitForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        permit = form.save(commit=False)
        permit.requested_by = request.user
        permit.save()
        messages.success(request, f'Request submitted successfully. ID: {permit.request_id}')
        return redirect('dashboard')
    return render(request, 'permits/create_request.html', {'form': form})


@login_required
def request_detail(request, pk):
    permit = get_object_or_404(WorkPermitRequest, pk=pk, requested_by=request.user)
    return render(request, 'permits/request_detail.html', {'permit': permit})


@login_required
def manager_panel(request):
    membership = getattr(request.user, 'department_membership', None)
    if not membership or membership.role != DepartmentMembership.Role.MANAGER:
        return redirect('dashboard')
    permits = WorkPermitRequest.objects.filter(department=membership.department, status=WorkPermitRequest.Status.PENDING_MANAGER)
    return render(request, 'permits/admin_panel.html', {'permits': permits, 'panel_name': 'Department Manager'})


@login_required
def gm_panel(request):
    if _role(request.user) != DepartmentMembership.Role.GENERAL_MANAGER:
        return redirect('dashboard')
    permits = WorkPermitRequest.objects.filter(status=WorkPermitRequest.Status.PENDING_GENERAL_MANAGER)
    return render(request, 'permits/admin_panel.html', {'permits': permits, 'panel_name': 'General Manager'})


@login_required
def security_panel(request):
    if _role(request.user) != DepartmentMembership.Role.SECURITY:
        return redirect('dashboard')
    permits = WorkPermitRequest.objects.filter(status=WorkPermitRequest.Status.APPROVED)
    return render(request, 'permits/security_panel.html', {'permits': permits})


@login_required
def review_request(request, pk, action):
    permit = get_object_or_404(WorkPermitRequest, pk=pk)
    role = _role(request.user)
    now = timezone.now()
    if role == DepartmentMembership.Role.MANAGER and permit.status == WorkPermitRequest.Status.PENDING_MANAGER:
        permit.manager_reviewed_by = request.user
        permit.manager_reviewed_at = now
        permit.status = WorkPermitRequest.Status.PENDING_GENERAL_MANAGER if action == 'approve' else WorkPermitRequest.Status.REJECTED_MANAGER
    elif role == DepartmentMembership.Role.GENERAL_MANAGER and permit.status == WorkPermitRequest.Status.PENDING_GENERAL_MANAGER:
        permit.gm_reviewed_by = request.user
        permit.gm_reviewed_at = now
        permit.status = WorkPermitRequest.Status.APPROVED if action == 'approve' else WorkPermitRequest.Status.REJECTED_GENERAL_MANAGER
    permit.save()
    return redirect('dashboard')


@login_required
def security_capture(request, pk):
    if _role(request.user) != DepartmentMembership.Role.SECURITY:
        return redirect('dashboard')
    permit = get_object_or_404(WorkPermitRequest, pk=pk, status=WorkPermitRequest.Status.APPROVED)
    form = GovernmentIDForm(request.POST or None, request.FILES or None, instance=getattr(permit, 'government_id', None))
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.permit_request = permit
        obj.save()
        messages.success(request, 'Government ID + visitor photo recorded.')
        return redirect('security_panel')
    return render(request, 'permits/security_capture.html', {'permit': permit, 'gov_form': form})
