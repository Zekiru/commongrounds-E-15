from django.contrib import admin
from .models import CommissionType, Commission, Job, JobApplication


class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0


class JobInline(admin.TabularInline):
    model = Job
    extra = 1


class CommissionInline(admin.TabularInline):
    model = Commission
    extra = 0


class CommissionTypeAdmin(admin.ModelAdmin):
    model = CommissionType
    list_display = ['name', 'description']
    ordering = ["name"]
    inlines = [CommissionInline]


class CommissionAdmin(admin.ModelAdmin):
    model = Commission
    list_display = [
        'title',
        'type',
        'maker',
        'people_required',
        'status',
        'jobs_status',
        'created_on',
        'updated_on'
    ]
    inlines = [JobInline]


class JobAdmin(admin.ModelAdmin):
    model = Job
    inlines = [JobApplicationInline]


class JobApplicationAdmin(admin.ModelAdmin):
    model = JobApplication


admin.site.register(CommissionType, CommissionTypeAdmin)
admin.site.register(Commission, CommissionAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(JobApplication, JobApplicationAdmin)
