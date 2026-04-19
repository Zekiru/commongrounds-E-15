from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=63)
    email_address = models.EmailField()
    ROLES = [
        ("A", "Anonymous"),
        ("MS", "Market Seller"),
        ("EO", "Event Organizer"),
        ("BC", "Book Contributor"),
        ("PC", "Project Creator"),
        ("CM", "Commission Maker"),
    ]
    role = models.CharField(max_length=20, choices=ROLES, default="A")

    def __str__(self):
        return self.display_name


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            display_name=instance.username,
            email_address=instance.email
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
