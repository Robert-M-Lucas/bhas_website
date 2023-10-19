from dataclasses import dataclass
from datetime import tzinfo, datetime

import pytz
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


@dataclass
class EditError:
    title: str = None
    description: str = None
    start_time: str = None
    end_time: str = None

    def is_error(self):
        return self.title is not None or self.description is not None or self.start_time is not None or self.end_time is not None


def edit(request, event_id):
    if not request.user.is_authenticated:
        return redirect("/auth/login")

    error = EditError()
    saved = False
    event = Event.objects.get(id=event_id)

    zones = Zone.objects.filter(
        Q(event_id=event_id)
    ).order_by('start_time')

    if request.POST:
        title = request.POST["title"]
        description = request.POST["description"]
        start_time = request.POST["start-time"]
        end_time = request.POST["end-time"]

        if len(title) == 0:
            error.title = "Title can't be empty"
        elif len(title) > 50:
            error.title = "Title must have fewer than 50 character"
            title = title[:50]

        if len(description) == 0:
            error.title = "Description can't be empty"
        elif len(description) > 1000:
            error.title = "Description must have fewer than 1000 character"
            description = description[:1000]

        try:
            start_time = datetime.strptime(start_time, "%d/%m/%Y %H:%M:%S")
            print(start_time)
            start_time = datetime.loc(tzinfo=pytz.timezone("Europe/London"))
            start_time = start_time.astimezone(pytz.utc)
        except ValueError:
            error.start_time = "Improperly formatted date/time"
            start_time = now()

        try:
            end_time = datetime.strptime(end_time, "%d/%m/%Y %H:%M:%S")
            end_time = end_time.replace(tzinfo=pytz.timezone("Europe/London"))
        except ValueError:
            error.start_time = "Improperly formatted date/time"
            end_time = now()

        print(start_time)
        event.title = title
        event.description = description
        event.start_time = start_time
        event.end_time = end_time

        if not error.is_error():
            event.save()
            saved = True

    return render(request, "backend/edit.html",
                  {
                      "pagename": "setup",
                      "event": event,
                      "zones": zones,
                      "error": error,
                      "saved": saved
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
