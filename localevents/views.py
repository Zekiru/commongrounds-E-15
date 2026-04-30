from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.mixins import RoleRequiredMixin
from .models import Event, EventSignup
from .forms import EventForm, EventSignupForm


def event_list(request):
    events = Event.objects.all()

    context = {
        'events': events,
    }

    if request.user.is_authenticated:
        profile = request.user.profile
        created_events = Event.objects.filter(organizer=profile)
        signed_up_events = Event.objects.filter(signups__user_registrant=profile)
        all_events = Event.objects.exclude(organizer=profile).exclude(
            signups__user_registrant=profile
        )

        context = {
            'created_events': created_events,
            'signed_up_events': signed_up_events,
            'events': all_events,
        }

    return render(request, 'event_list.html', context)


def event_detail(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        raise Http404("Event does not exist")

    signups = EventSignup.objects.filter(event=event)
    signup_count = len(signups)
    is_full = signup_count >= event.event_capacity

    is_organizer = False
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile in event.organizer.all():
            is_organizer = True

    context = {
        'event': event,
        'signups': signups,
        'signup_count': signup_count,
        'is_full': is_full,
        'is_organizer': is_organizer,
    }

    return render(request, 'event_detail.html', context)


class EventCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'event_form.html'
    required_role = 'EO'

    def form_valid(self, form):
        self.object = form.save()
        self.object.organizer.add(self.request.user.profile)
        return redirect('event_detail', event_id=self.object.id)


class EventUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'event_form.html'
    pk_url_kwarg = 'event_id'
    required_role = 'EO'

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user.profile)

    def form_valid(self, form):
        self.object = form.save()

        signups = EventSignup.objects.filter(event=self.object)
        signup_count = len(signups)

        if signup_count >= self.object.event_capacity:
            self.object.status = 'Full'
        else:
            self.object.status = 'Available'

        self.object.save()

        return redirect('event_detail', event_id=self.object.id)


class BaseSignupView(View):
    def post(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise Http404("Event does not exist")

        if not self.check_capacity(event):
            return redirect(self.get_redirect_url(event))

        if not self.check_ownership(event, request.user):
            return redirect(self.get_redirect_url(event))

        signup = self.create_signup(event, request.user)

        if signup is None:
            form = EventSignupForm(request.POST)
            context = {
                'event': event,
                'form': form,
            }
            return render(request, 'event_signup.html', context)

        return redirect(self.get_redirect_url(event))

    def check_capacity(self, event):
        signups = EventSignup.objects.filter(event=event)
        return len(signups) < event.event_capacity

    def check_ownership(self, event, user):
        if user.is_authenticated:
            if user.profile in event.organizer.all():
                return False
        return True

    def create_signup(self, event, user):
        return None

    def get_redirect_url(self, event):
        return reverse('event_detail', args=[event.id])


class EventSignupView(BaseSignupView):
    def get(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise Http404("Event does not exist")

        if request.user.is_authenticated:
            return redirect('event_detail', event_id=event.id)

        form = EventSignupForm()
        context = {
            'event': event,
            'form': form,
        }
        return render(request, 'event_signup.html', context)

    def create_signup(self, event, user):
        if user.is_authenticated:
            existing_signups = EventSignup.objects.filter(
                event=event,
                user_registrant=user.profile
            )

            if len(existing_signups) == 0:
                signup = EventSignup()
                signup.event = event
                signup.user_registrant = user.profile
                signup.save()
                return signup

            return existing_signups[0]

        form = EventSignupForm(self.request.POST)

        if form.is_valid():
            signup = form.save(commit=False)
            signup.event = event
            signup.save()
            return signup

        return None

    def get_redirect_url(self, event):
        return reverse('event_detail', args=[event.id])