from django.shortcuts import redirect
from django.views.generic import TemplateView
from .models import Project


def index(project):
    return redirect('projects/')


class ProjectListView(TemplateView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'project_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        return context


class ProjectDetailView(TemplateView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(
            id=self.kwargs['project_id']
        )
        return context
