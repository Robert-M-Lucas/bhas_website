from django import template
from datetime import datetime, timezone

import pytz

register = template.Library()


def is_dst(dt, timezone="Europe/London"):
    if dt is None:
        dt = datetime.utcnow()
    timezone = pytz.timezone(timezone)
    timezone_aware_date = timezone.localize(dt, is_dst=False)
    return timezone_aware_date.tzinfo._dst.seconds != 0


@register.simple_tag(name="localise")
def localise(dt: datetime):
    return dt.astimezone(pytz.timezone('Europe/London')).strftime("%b. %#d, %Y, %#I:%M %p")
