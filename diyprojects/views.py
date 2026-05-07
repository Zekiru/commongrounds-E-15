from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Project, Favorite, ProjectRating
from .repositories import ProjectRepository
from .forms import ProjectCreateForm, ProjectUpdateForm, ProjectReviewForm, ProjectRatingForm


def index(request):
    return redirect('diyprojects:project_list')


class ProjectListView(ListView):
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = ProjectRepository()

    def get_queryset(self):
        return self.repo.get_all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_projects = list(self.get_queryset())

        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
            profile = self.request.user.profile
            context['created_projects'] = list(
                self.repo.get_projects_created_by(profile))
            context['favorited_projects'] = list(
                self.repo.get_projects_favorited_by(profile))
            context['reviewed_projects'] = list(
                self.repo.get_projects_reviewed_by(profile))

            interacted = context['created_projects'] + \
                context['favorited_projects'] + context['reviewed_projects']
            interacted_ids = {p.id for p in (interacted)}
            context['projects'] = [
                p for p in all_projects if p.id not in interacted_ids]
        else:
            context['projects'] = all_projects
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = ProjectRepository()

    def get_object(self, queryset=None):
        return self.repo.get_by_id(self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()

        context['average_rating'] = self.repo.get_project_average_rating(
            project)
        context['favorites_count'] = self.repo.get_project_favorites_count(
            project)
        context['reviews'] = self.repo.get_project_reviews(project)
        context['is_creator'] = False

        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
            profile = self.request.user.profile
            context['is_creator'] = (project.creator == profile)
            context['review_form'] = ProjectReviewForm(user=self.request.user)
            context['rating_form'] = ProjectRatingForm(user=self.request.user)

        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        profile = request.user.profile
        project = self.get_object()

        if 'toggle_favorite' in request.POST:
            fav = Favorite.objects.filter(project=project, profile=profile)
            if fav.exists():
                fav.delete()
            else:
                Favorite.objects.create(project=project, profile=profile)

        elif 'submit_review' in request.POST:
            form = ProjectReviewForm(
                request.POST, request.FILES, user=request.user)
            if form.is_valid():
                review = form.save(commit=False)
                review.project = project
                review.reviewer = profile
                review.save()

        elif 'submit_rating' in request.POST:
            form = ProjectRatingForm(request.POST, user=request.user)
            if form.is_valid():
                ProjectRating.objects.update_or_create(
                    project=project, profile=profile,
                    defaults={'score': form.cleaned_data['score']}
                )

        return redirect('diyprojects:project_detail', pk=project.pk)


class ProjectCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Project
    template_name = 'projects/project_form.html'
    form_class = ProjectCreateForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = ProjectRepository()

    def test_func(self):
        if not hasattr(self.request.user, 'profile'):
            return False
        return self.request.user.profile.role == 'PC'

    def form_valid(self, form):
        form.instance.creator = self.request.user.profile
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['title', 'category', 'description', 'materials', 'steps']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = ProjectRepository()

    def get_object(self, queryset=None):
        return self.repo.get_by_id(self.kwargs.get('pk'))

    def test_func(self):
        if not hasattr(self.request.user, 'profile'):
            return False

        profile = self.request.user.profile
        project = self.get_object()
        return profile.role == 'PC' and project.creator == profile
