from datetime import tzinfo

from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils.timezone import now

from .models import Event, Zone

def setup(request):
    if not request.user.is_authenticated:
        return redirect("/auth/login")

    future_events = Event.objects.filter(
        Q(start_time__gte=now(), deleted=False)
    ).order_by('start_time')

    past_events = Event.objects.filter(
        Q(start_time__lt=now(), deleted=False)
    ).order_by('-start_time')

    deleted_events = Event.objects.filter(
        Q(deleted=True)
    ).order_by('-start_time')

    return render(request, "backend/setup.html",
                  {
                      "pagename": "setup",
                      "future_events": future_events,
                      "past_events": past_events,
                      "deleted_events": deleted_events,
                  }
                  )


def create_empty_event(request):
    event = Event.objects.create(
        created_by=request.user,
        start_time=now(),
        end_time=now(),
        title="New Event",
        description="Event Description"
    )
    return event


def new(request):
    if not request.user.is_authenticated:
        return redirect("/auth/login")

    event_id = create_empty_event(request).id

    return redirect(f"/setup/edit/{event_id}")


def edit(request, event_id):
    if not request.user.is_authenticated:
        return redirect("/auth/login")

    event = Event.objects.get(id=event_id)

    zones = Zone.objects.filter(
        Q(event_id=event_id)
    ).order_by('start_time')

    return render(request, "backend/edit.html",
                  {
                      "pagename": "setup",
                      "event": event,
                      "zones": zones
                  }
                  )


def delete(request, event_id):
    if not request.user.is_authenticated:
        return redirect("/auth/login")

    event = Event.objects.get(id=event_id)
    event.deleted = True
    event.save()

    return redirect("/setup")


def restore(request, event_id):
    if not request.user.is_authenticated:
        return redirect("/auth/login")

    event = Event.objects.get(id=event_id)
    event.deleted = False
    event.save()

    return redirect("/setup")
