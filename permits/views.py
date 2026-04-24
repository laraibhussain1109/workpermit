from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import GovernmentIDForm, WorkPermitForm
from .models import WorkPermitRequest


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)


@login_required
def dashboard(request):
    form = WorkPermitForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        permit = form.save(commit=False)
        permit.requested_by = request.user
        permit.save()
        messages.success(request, 'Work permit request submitted successfully.')
        return redirect('dashboard')

    permits = WorkPermitRequest.objects.filter(requested_by=request.user)
    return render(request, 'permits/dashboard.html', {'form': form, 'permits': permits})


@login_required
def request_detail(request, pk):
    permit = get_object_or_404(WorkPermitRequest, pk=pk, requested_by=request.user)

    if permit.status == WorkPermitRequest.Status.APPROVED and not hasattr(permit, 'government_id'):
        gov_form = GovernmentIDForm(request.POST or None, request.FILES or None)
        if request.method == 'POST' and gov_form.is_valid():
            gov = gov_form.save(commit=False)
            gov.permit_request = permit
            gov.save()
            messages.success(request, 'Government ID submitted successfully.')
            return redirect('request_detail', pk=permit.pk)
    else:
        gov_form = None

    return render(request, 'permits/request_detail.html', {'permit': permit, 'gov_form': gov_form})


@staff_required
@login_required
def admin_panel(request):
    permits = WorkPermitRequest.objects.select_related('requested_by', 'reviewed_by').all()
    return render(request, 'permits/admin_panel.html', {'permits': permits})


@staff_required
@login_required
def review_request(request, pk, action):
    permit = get_object_or_404(WorkPermitRequest, pk=pk)
    if permit.status != WorkPermitRequest.Status.PENDING:
        messages.warning(request, 'This request has already been reviewed.')
        return redirect('admin_panel')

    if action == 'approve':
        permit.status = WorkPermitRequest.Status.APPROVED
        messages.success(request, f'Request #{permit.id} approved.')
    elif action == 'reject':
        permit.status = WorkPermitRequest.Status.REJECTED
        messages.error(request, f'Request #{permit.id} rejected.')
    else:
        messages.error(request, 'Invalid action.')
        return redirect('admin_panel')

    permit.reviewed_by = request.user
    permit.reviewed_at = timezone.now()
    permit.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])
    return redirect('admin_panel')
