from django.shortcuts import render, redirect
from django.utils.timezone import now

from backend.models import Event


def index(request):
    active_events = Event.objects.filter(start_time__lt=now(), end_time__gt=now(), deleted=False)
    if len(active_events) == 0:
        active_event = None
    else:
        active_event = active_events[0]

    future_event = None
    if active_event is None:
        future_events = Event.objects.filter(start_time__gt=now(), deleted=False)
        if len(future_events) == 0:
            future_event = None
        else:
            future_event = future_events[0]

    return render(request, 'public/index.html',
                  {
                      "pagename": "status",
                      "active_event": active_event,
                      "future_event": future_event
                  }
                  )


def status(request):
    return redirect('/')