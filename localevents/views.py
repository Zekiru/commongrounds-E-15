from django.shortcuts import render
from django.http import Http404
from .models import Event


def event_list(request):
    events = Event.objects.all()
    context = {
        'events': events,
    }
    return render(request, 'event_list.html', context)


def event_detail(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        raise Http404("Event does not exist")

    context = {
        'event': event,
    }
    return render(request, 'event_detail.html', context)
