from django.contrib import admin
from .models import ProjectCategory, Project


class ProjectCategoryAdmin(admin.ModelAdmin):
    model = ProjectCategory
    list_display = ['name', 'description']
    ordering = ["name"]


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    list_display = [
        'title',
        'category',
        'description',
        'materials',
        'steps',
        'created_on',
        'updated_on'
    ]
    ordering = ["-created_on"]


admin.site.register(ProjectCategory, ProjectCategoryAdmin)
admin.site.register(Project, ProjectAdmin)
