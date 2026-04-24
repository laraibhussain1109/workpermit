from django.contrib import admin
from django.utils import timezone

from .models import GovernmentID, WorkPermitRequest


@admin.register(WorkPermitRequest)
class WorkPermitRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'location', 'requested_by', 'status', 'created_at')
    list_filter = ('status', 'country_code', 'created_at')
    search_fields = ('request_id', 'location', 'contractor_name', 'contact_person', 'requested_by__username')
    readonly_fields = ('request_id', 'reviewed_by', 'reviewed_at', 'created_at')
    actions = ('approve_requests', 'reject_requests')

    @admin.action(description='Approve selected requests')
    def approve_requests(self, request, queryset):
        updated = queryset.filter(status=WorkPermitRequest.Status.PENDING).update(
            status=WorkPermitRequest.Status.APPROVED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f'{updated} request(s) approved.')

    @admin.action(description='Reject selected requests')
    def reject_requests(self, request, queryset):
        updated = queryset.filter(status=WorkPermitRequest.Status.PENDING).update(
            status=WorkPermitRequest.Status.REJECTED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f'{updated} request(s) rejected.')


@admin.register(GovernmentID)
class GovernmentIDAdmin(admin.ModelAdmin):
    list_display = ('permit_request', 'id_type', 'id_number', 'submitted_at')
    search_fields = ('id_number', 'permit_request__requested_by__username')
