import typing

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
    zones: typing.Dict[int, str] = None

    def is_error(self):
        return self.title is not None or self.description is not None or self.start_time is not None or self.end_time is not None or self.position is not None or self.zones is not None

@dataclass
class ZoneEditError:
    title: str = None
    index: str = None
    time: str = None

def time_from_strict_string(string):
    error = None
    time = None
    dtime = None
    try:
        dtime = datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")
    except ValueError as e:
        try:
            dtime = datetime.strptime(string, "%Y-%m-%dT%H:%M")
        except ValueError as e:
            print(e)
            error = "Improperly formatted date/time"
            time = now()

    if error is None:
        try:
            time = pytz.timezone("Europe/London").localize(dtime)
        except pytz.exceptions.AmbiguousTimeError:
            time = pytz.timezone("Europe/London").localize(dtime, is_dst=False)


    return time, error

def edit(request, event_id):
    if not request.user.is_authenticated:
        return redirect("/auth/login")

    error = EditError()
    saved = False

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return render(request, "404.html")

    if request.POST:
        title = request.POST["title"]
        description = request.POST["description"]
        start_time = request.POST["start-time"]
        end_time = request.POST["end-time"]
        latitude = request.POST["latitude"]
        longitude = request.POST["longitude"]

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

        start_time, error.start_time = time_from_strict_string(start_time)
        end_time, error.end_time = time_from_strict_string(end_time)

        if end_time < start_time:
            if error.end_time is None:
                error.end_time = "Event ends before it start"
            end_time = start_time

        position = "0.0,0.0"
        try:
            position = Position(float(latitude), float(longitude)).to_string()
        except ValueError:
            error.position = "Latitude and longitude must be formatted as two valid decimals"

        post_dict = dict(request.POST)
        for k in ["title", "description", "start-time", "end-time", "latitude", "longitude"]: post_dict.pop(k)

        for key in post_dict.keys():
            match = "title-zone-"
            if len(key) < len(match) or key[:len(match)] != match:
                continue

            name = key[len(match):]
            if name == "x": continue

            z_title = request.POST[f"title-zone-{name}"]
            z_index = request.POST[f"index-zone-{name}"]
            z_start_time, z_start_time_error = time_from_strict_string(request.POST[f"start-time-zone-{name}"])
            z_end_time, z_end_time_error = time_from_strict_string(request.POST[f"end-time-zone-{name}"])
            z_circular = f"circular-zone-{name}" in post_dict.keys()

            z_title_error = None
            if len(z_title) > 50:
                z_title = z_title[:50]
                z_title_error = "Zone name must be shorter than 50 characters"
            elif len(z_title) == 0:
                z_title = "New Zone"
                z_title_error = "Zone name must be at least one chatacter"

            if z_start_time_error:
                z_start_time = now()
            if z_end_time_error:
                z_end_time = now()

            if z_start_time_error is None: z_start_time_error = z_end_time_error

            z_time_error = z_start_time_error

            if z_start_time > z_end_time:
                z_end_time = z_start_time
                if z_time_error is None:
                    z_time_error = "Zone ends before it starts"

            z_index_error = None
            try:
                z_index = int(z_index)
            except ValueError:
                z_index = 0
                z_index_error = "Index must be an integer greater than 0"
            if z_index < 0:
                z_index = 0
                z_index_error = "Index must be an integer greater than 0"

            z_coords = "0.0,0.0"

            rad = ""
            if z_circular:
                rad = "100.0"

            z_id = None
            if name[0] == "*":
                z_id = Zone.objects.create(
                    created_by=request.user,
                    event_id=event,
                    start_time=z_start_time,
                    end_time=z_end_time,
                    title=z_title,
                    index=z_index,
                    is_circle=z_circular,
                    points_or_center=z_coords,
                    hole_points_or_radius=rad
                ).id
            else:
                z_id = int(name)
                zone = Zone.objects.get(id=z_id)
                zone.start_time = z_start_time
                zone.end_time = z_end_time
                zone.title = z_title
                zone.index = z_index
                zone.is_circle = z_circular
                zone.points_or_center = z_coords
                zone.hole_points_or_radius = rad
                zone.save()

            if z_time_error or z_index_error or z_title_error:
                if error.zones is None:
                    error.zones = {}
                error.zones[z_id] = ZoneEditError(
                    z_title_error,
                    z_index_error,
                    z_time_error
                )

        event.title = title
        event.description = description
        event.start_time = start_time
        event.end_time = end_time
        event.center = position

        event.save()
        saved = True

    zones = Zone.objects.filter(
        Q(event_id=event_id)
    ).order_by('start_time')

    z_list = []
    for z in zones:
        e = None
        if error.zones is not None and z.id in error.zones.keys():
            e = error.zones[z.id]
        z_list.append({"z": z, "error": e})

    return render(request, "setup/edit.html",
                  {
                      "pagename": "setup",
                      "event": event,
                      "center": Position.from_string(event.center),
                      "zones": z_list,
                      "error": error,
                      "saved": saved,
                      "now": now()
                  }
                  )


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
