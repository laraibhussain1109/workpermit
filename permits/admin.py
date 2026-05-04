from django.contrib import admin

from .models import Department, DepartmentMembership, GovernmentID, WorkPermitRequest

admin.site.register(Department)
admin.site.register(DepartmentMembership)


@admin.register(WorkPermitRequest)
class WorkPermitRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'location', 'requested_by', 'department', 'status', 'manager_reviewed_by', 'gm_reviewed_by')


@admin.register(GovernmentID)
class GovernmentIDAdmin(admin.ModelAdmin):
    list_display = ('permit_request', 'id_type', 'id_number', 'submitted_at')
