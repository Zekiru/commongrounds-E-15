from django.db import models
from django.urls import reverse
from accounts.models import Profile
from django.core.validators import MinValueValidator, MaxValueValidator

from commongrounds.storage import CloudinaryStorage

STATUS_CHOICES = [
    ('Backlog', 'Backlog'),
    ('To-Do', 'To-Do'),
    ('Done', 'Done')
]


class ProjectCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'project category'
        verbose_name_plural = 'project categories'


class Project(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        null=True
    )
    creator = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='projects'
    )
    description = models.TextField()
    materials = models.TextField()
    steps = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('diyprojects:project_detail', args=[str(self.id)])

    class Meta:
        ordering = ["-created_on"]
        verbose_name = 'project'
        verbose_name_plural = 'projects'


class Favorite(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='favorited_projects'
    )

    date_favorited = models.DateField(auto_now_add=True)
    project_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Backlog'
    )

    def __str__(self):
        return f"{self.profile.display_name} favorited {self.project.title}"


class ProjectReview(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    reviewer = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='reviews_written'
    )

    comment = models.TextField()
    image = models.ImageField(
        upload_to='images/',
        storage=CloudinaryStorage(), 
        null=True, blank=True)


class ProjectRating(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='ratings'
    )

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='ratings_given'
    )

    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    def __str__(self):
        return f"{self.score}/10 by {self.profile.display_name}"
