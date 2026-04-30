from django.urls import path
from .views import index, ProjectListView, ProjectDetailView

urlpatterns = [
    path('', index, name='index'),
    path(
        'projects/',
        ProjectListView.as_view(),
        name='project_list'
    ),
    path(
        'project/<int:project_id>/',
        ProjectDetailView.as_view(),
        name='project_detail'
    ),
]
