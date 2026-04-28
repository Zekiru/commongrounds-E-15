from django.contrib import admin
from .models import CommissionType, Commission


class CommissionInline(admin.TabularInline):
    model = Commission
    extra = 1


class CommissionTypeAdmin(admin.ModelAdmin):
    model = CommissionType
    list_display = ['name', 'description']
    ordering = ["name"]
    inlines = [CommissionInline,]


class CommissionAdmin(admin.ModelAdmin):
    model = Commission
    list_display = [
        'title',
        'commission_type',
        'description',
        'people_required',
        'created_on',
        'updated_on'
    ]
    ordering = ["created_on"]


admin.site.register(CommissionType, CommissionTypeAdmin)
admin.site.register(Commission, CommissionAdmin)
