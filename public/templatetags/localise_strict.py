from django import template
from datetime import datetime, timezone
import pytz

register = template.Library()

@register.simple_tag(name="localise_strict")
def localise_strict(dt: datetime):
    return dt.astimezone(pytz.timezone('Europe/London')).strftime("%d/%m/%Y %H:%M:%S")
