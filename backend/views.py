from dataclasses import dataclass

from django.db.models import Q
from django.http import HttpResponse
from django.utils.timezone import now

from .models import Event, Zone, SocietyMessage, Position

"""
Position

latitude: float
longitude: float
"""

"""
Circle

index int
position Position
radius float
"""

"""
Polygon

index int
points [Position]
holePoints [Position]
"""

"""
Entire

societyMessage string
gameState bool
nextGame int // -1 means no next game
center Position
circles [Circle]
polygons [Polygon]
nextZone int // Negative if game ending
"""


@dataclass
class Circle:
    index: int
    center: Position
    radius: float

    def as_json(self):
        return f'{{"index":{self.index},{self.center.as_json()},"radius":{self.radius}}}'


@dataclass
class Polygon:
    index: int
    points: [Position]
    hole_points: [Position]

    def as_json(self):
        json = f'{{"index":{self.index},"points":['
        json += ','.join([pos.as_json() for pos in self.points])
        json += f'],"holePoints":['
        json += ','.join([pos.as_json() for pos in self.hole_points])
        json += f']}}'
        return json


@dataclass
class Entire:
    society_message: str
    game_state: bool
    next_game: int
    center: Position
    circles: [Circle]
    polygons: [Polygon]
    next_zone: int

    def as_json(self):
        json = f'{{"societyMessage":"{self.society_message}","gameState":{str(self.game_state).lower()},"nextGame":{self.next_game},"center":{self.center.as_json()},"circles":['
        json += ','.join([circle.as_json() for circle in self.circles])
        json += f'],"polygons":['
        json += ','.join([polygon.as_json() for polygon in self.polygons])
        json += f'],"nextZone":{self.next_zone}}}'
        return json


def app_status(request):
    try:
        society_message = SocietyMessage.objects.get(deleted=False).message
    except SocietyMessage.DoesNotExist:
        SocietyMessage.objects.create(message="Welcome to Bath Hide and Seek")
        society_message = "Welcome to Bath Hide and Seek"

    current_game = Event.objects.filter(
        Q(start_time__lt=now(), deleted=False)
    ).order_by('-start_time')

    if len(current_game) == 0:
        current_game = None
    else:
        current_game = current_game[0]

    game_in_progress = current_game is not None and current_game.end_time > now()

    next_game = -1
    center = Position(0, 0)
    circles = []
    polygons = []
    next_zone = 0
    if game_in_progress:
        center = Position.from_string(current_game.center)

        active_zones = Zone.objects.filter(
            Q(start_time__lt=now(), end_time__gt=now(), deleted=False)
        )

        for zone in active_zones:
            if zone.is_circle:
                circles.append(Circle(
                    zone.index,
                    Position.from_string(zone.points_or_center),
                    float(zone.hole_points_or_radius)
                ))
            else:
                points = [Position.from_string(x) for x in zone.points_or_center_radius.split(';')]
                hole_points = [Position.from_string(x) for x in zone.hole_points_or_radius.split(';')]

                polygons.append(Polygon(
                    zone.index,
                    points,
                    hole_points
                ))

        next_zones = Zone.objects.filter(
            Q(start_time__gt=now(), deleted=False)
        ).order_by('start_time')

        if len(next_zones) == 0:
            # Negative to indicate game end
            next_zone = -int((current_game.end_time - now()).total_seconds())
        else:
            next_zone = next_zones[0]
            next_zone = int((next_zone.start_time - now()).total_seconds())

    else:
        next_events = Event.objects.filter(
            Q(start_time__gt=now(), deleted=False)
        ).order_by('start_time')

        if len(next_events) > 0:
            next_game = int((next_events[0].start_time - now()).total_seconds())

    json = Entire(
        society_message=society_message,
        game_state=game_in_progress,
        next_game=next_game,
        center=center,
        circles=circles,
        polygons=polygons,
        next_zone=next_zone
    ).as_json()

    return HttpResponse(json)
