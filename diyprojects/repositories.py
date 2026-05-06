from django.db.models import Avg
from .models import Project, Favorite, ProjectReview, ProjectRating


class ProjectRepository:
    def get_all(self):
        return Project.objects.all()

    def get_by_category(self, category_name):
        return Project.objects.filter(category__name=category_name)

    def get_recent(self, n):
        return Project.objects.order_by('-created_on')[:n]

    def get_by_id(self, id):
        return Project.objects.get(id=id)

    # List view helper methods
    def get_projects_created_by(self, profile):
        return Project.objects.filter(creator=profile)

    def get_projects_favorited_by(self, profile):
        return Project.objects.filter(favorites__profile=profile)

    def get_projects_reviewed_by(self, profile):
        return Project.objects.filter(reviews__reviewer=profile).distinct()
        # distinct() = only shows up once even if multiple entries

    # Detail view helper methods
    def get_project_average_rating(self, project):
        avg = ProjectRating.objects.filter(
            project=project).aggregate(Avg('score'))['score__avg']
        if avg:
            return round(avg, 2)  # 2 is decimal places to round (ex: 1.00)
        else:
            return 0

    def get_project_favorites_count(self, project):
        return Favorite.objects.filter(project=project).count()

    def get_project_reviews(self, project):
        return ProjectReview.objects.filter(project=project)
