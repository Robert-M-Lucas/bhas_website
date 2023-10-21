from django.shortcuts import render

from dataclasses import dataclass
from datetime import tzinfo, datetime

import pytz
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils.timezone import now

from backend.models import Event, Zone, SocietyMessage, Position


def setup(request):
    if not request.user.is_authenticated:
        return redirect("/auth/login")

    society_message = SocietyMessage.get_message()

    message_error = None

    if request.POST:
        society_message = request.POST['society-message']

        if len(society_message) > 50:
            message_error = "The message must be 50 characters or less"
        elif len(society_message.strip()) == 0:
            message_error = "The message must contain something"

        if message_error is None:
            print(society_message)
            SocietyMessage.set_message(society_message)
            return redirect("/setup")

    future_events = Event.objects.filter(
        Q(start_time__gte=now(), deleted=False)
    ).order_by('start_time')

    past_events = Event.objects.filter(
        Q(start_time__lt=now(), deleted=False)
    ).order_by('-start_time')

    deleted_events = Event.objects.filter(
        Q(deleted=True)
    ).order_by('-start_time')

    return render(request, "setup/setup.html",
                  {
                      "pagename": "setup",
                      "future_events": future_events,
                      "past_events": past_events,
                      "deleted_events": deleted_events,
                      "society_message": society_message,
                      "message_error": message_error
                  }
                  )


def create_empty_event(request):
    event = Event.objects.create(
        created_by=request.user,
        start_time=now(),
        end_time=now(),
        title="New Event",
        description="Event Description",
        center=Position(0.0, 0.0).to_string()
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
    position: str = None

    def is_error(self):
        return self.title is not None or self.description is not None or self.start_time is not None or self.end_time is not None or self.position is not None


def edit(request, event_id):
    if not request.user.is_authenticated:
        return redirect("/auth/login")

    error = EditError()
    saved = False

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return render(request, "404.html")

    zones = Zone.objects.filter(
        Q(event_id=event_id)
    ).order_by('start_time')

    if request.POST:
        title = request.POST["title"]
        description = request.POST["description"]
        start_time = request.POST["start-time"]
        end_time = request.POST["end-time"]
        latitude = request.POST["latitude"]
        longitude = request.POST["longitude"]

        post_dict = dict(request.POST)
        for k in ["title", "description", "start-time", "end-time", "latitude", "longitude"]: post_dict.pop(k)
        print(post_dict)

        print(request.POST)

        if len(title) == 0:
            error.title = "Title can't be empty"
        elif len(title) > 50:
            error.title = "Title must have fewer than 50 character"
            title = title[:50]

        if len(description) == 0:
            error.description = "Description can't be empty"
        elif len(description) > 1000:
            error.description = "Description must have fewer than 1000 character"
            description = description[:1000]

        try:
            start_time = datetime.strptime(start_time, "%d/%m/%Y %H:%M:%S")
            try:
                start_time = pytz.timezone("Europe/London").localize(start_time)
            except pytz.exceptions.AmbiguousTimeError:
                start_time = start_time = pytz.timezone("Europe/London").localize(start_time, is_dst=False)
        except ValueError:
            error.start_time = "Improperly formatted date/time"
            start_time = now()

        try:
            end_time = datetime.strptime(end_time, "%d/%m/%Y %H:%M:%S")
            try:
                end_time = pytz.timezone("Europe/London").localize(end_time)
            except pytz.exceptions.AmbiguousTimeError:
                end_time = pytz.timezone("Europe/London").localize(end_time, is_dst=False)
        except ValueError:
            error.end_time = "Improperly formatted date/time"
            end_time = now()

        if end_time < start_time and error.end_time is None:
            error.end_time = "Event ends before it start"
            end_time = start_time

        position = "0.0,0.0"
        try:
            position = Position(float(latitude), float(longitude)).to_string()
        except ValueError:
            error.position = "Latitude and longitude must be formatted as two valid decimals"

        event.title = title
        event.description = description
        event.start_time = start_time
        event.end_time = end_time
        event.center = position

        if not error.is_error():
            event.save()
            saved = True

    return render(request, "setup/edit.html",
                  {
                      "pagename": "setup",
                      "event": event,
                      "center": Position.from_string(event.center),
                      "zones": zones,
                      "error": error,
                      "saved": saved,
                      "now": now()
                  }
                  )


def edit_zones(request, event_id):
    if not request.user.is_authenticated:
        return redirect("/auth/login")

    return render(request, "setup/edit_zones.html")


def delete(request, event_id):
    if not request.user.is_authenticated:
        return redirect("/auth/login")

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return render(request, "404.html")
    event.deleted = True
    event.save()

    return redirect("/setup")


def restore(request, event_id):
    if not request.user.is_authenticated:
        return redirect("/auth/login")

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return render(request, "404.html")
    event.deleted = False
    event.save()

    return redirect("/setup")
