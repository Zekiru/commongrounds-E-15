from django.contrib import admin
from .models import EventType, Event, EventSignup

admin.site.register(EventType)
admin.site.register(Event)
admin.site.register(EventSignup)
