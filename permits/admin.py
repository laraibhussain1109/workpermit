from django.contrib import admin

from .models import GovernmentID, WorkPermitRequest


@admin.register(WorkPermitRequest)
class WorkPermitRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'location', 'requested_by', 'status', 'created_at')
    list_filter = ('status', 'country_code', 'created_at')
    search_fields = ('location', 'contractor_name', 'contact_person', 'requested_by__username')


@admin.register(GovernmentID)
class GovernmentIDAdmin(admin.ModelAdmin):
    list_display = ('permit_request', 'id_type', 'id_number', 'submitted_at')
    search_fields = ('id_number', 'permit_request__requested_by__username')
