from django.db import models
from accounts.models import Profile
from commongrounds.storage import CloudinaryStorage


class EventType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Event(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Full', 'Full'),
        ('Done', 'Done'),
        ('Cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        EventType,
        null=True,
        on_delete=models.SET_NULL
    )
    organizer = models.ManyToManyField(Profile)

    event_image = models.ImageField(
        upload_to='images/',
        storage=CloudinaryStorage(),
        null=True,
        blank=True,
        max_length=500
    )

    description = models.TextField()
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    event_capacity = models.PositiveIntegerField()
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default='Available'
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title


class EventSignup(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='signups'
    )
    user_registrant = models.ForeignKey(
        Profile,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='event_signups'
    )
    new_registrant = models.CharField(max_length=255, blank=True)

    def __str__(self):
        if self.user_registrant:
            return self.user_registrant.display_name
        return self.new_registrant
