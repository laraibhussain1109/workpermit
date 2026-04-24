from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import GovernmentIDForm, WorkPermitForm
from .models import WorkPermitRequest

@login_required
def dashboard(request):
    permits = WorkPermitRequest.objects.filter(requested_by=request.user)
    context = {
        'approved_permits': permits.filter(status=WorkPermitRequest.Status.APPROVED),
        'pending_permits': permits.filter(status=WorkPermitRequest.Status.PENDING),
        'rejected_permits': permits.filter(status=WorkPermitRequest.Status.REJECTED),
    }
    return render(request, 'permits/dashboard.html', context)


@login_required
def create_request(request):
    form = WorkPermitForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        permit = form.save(commit=False)
        permit.requested_by = request.user
        permit.save()
        messages.success(request, f'Work permit request submitted successfully. Request ID: {permit.request_id}')
        return redirect('dashboard')

    return render(request, 'permits/create_request.html', {'form': form})


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
