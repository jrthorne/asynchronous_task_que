from .mixins import EnumBase
import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

HOUR_CHOICES = zip( range(24), range(24) )
MINUTE_CHOICES = zip( range(60), range(60) )
DOM_CHOICES = []
for d in list(range(1,32)):
    DOM_CHOICES += [( d, d )]
MONTH_CHOICES = [ 
(1, _('January')), 
(2, _('February')), 
(3, _('March')), 
(4, _('April')),
(5, _('May')), 
(6, _('June')), 
(7, _('July')), 
(8, _('August')), 
(9, _('September')), 
(10, _('October')), 
(11, _('November')), 
(12, _('December'))
    ] 
YEAR_CHOICES = []
for y in list(range(1970,2001)):
    YEAR_CHOICES += [(y,y)]

class DayOfWeekEnum(EnumBase):
    # Monday is 0 and Sunday is 6.
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    choices = [
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday')
    ]


class TaskStatusEnum(EnumBase):
    PENDING = 0
    RUNNING = 10
    DONE = 20
    FAILED = 30
    KILLED = 40

    choices = [
        (PENDING, 'Pending'),
        (RUNNING, 'Running'),
        (DONE, 'Done'),
        (FAILED, 'Failed'),
        (KILLED, 'Killed')
    ]

class EventTypeEnum(EnumBase):
    # same codes as on Dojo
    ERROR = 50
    LOG = 100
    API = 300
    AUTH = 350
    DEBUG = 400
    # teaching logs are ones to do with things Teachers and students do with the app
    TEACHING = 500


    choices = [
        (ERROR, 'Error'),
        (LOG, 'Event Log'),
        (API, 'Application Programming Interface'),
        (AUTH, 'Authentication'),
        (DEBUG, 'Debugging Log'),
        (TEACHING, 'Teaching Log')
    ]


def record_event(event_type=EventTypeEnum.LOG, summary='', extra_detail='', makeme_string=None, 
                 show=True, thing=None, request=None):
    """ 
    Record System Wide Event Stuff. Not a member function, 
    becuase importing the model class everywhere is to be avoided 
    """
    if event_type == EventTypeEnum.DEBUG and not settings.DEBUG:
        return

    if makeme_string:
        try:
            string_bit = json.dumps(makeme_string, sort_keys=True, indent=4, separators=(',', ': '), default=str)
        except:
            string_bit = 'Could not dump the makeme_string'
        extra_detail += '\n=======================\n%s' % string_bit
            
    from async_que.models import Event
    evt = Event(event_type=event_type, 
                   summary=summary,
                   extra_detail=extra_detail,
                   show=show)

    if request:
        if isinstance(request.user, User):
            evt.logged_in = request.user
        ip = request.META.get('X-Real-IP', None)
        if not ip:
            ip = request.META.get('REMOTE_ADDR')
        evt.ip_address = ip or None

    evt.save()


def queue_command(command, user=None, force=False):
    # you gotta be careful of circular imports. Put in here is safer
    from .models import QueuedTask
    if force or not QueuedTask.objects.filter(command=command, status=TaskStatusEnum.PENDING).exists():
        QueuedTask.objects.create(command=command, staff_member=user)


def date_from_string(date_string, use_time=False, format=settings.DATEFORMAT):
    stripped_time    = time.strptime(date_string, format)
    my_time            = time.mktime(stripped_time)
    if not use_time:
        retval        = datetime.datetime.fromtimestamp(my_time)
        retval        = retval.date()
    else:
        retval        = datetime.date.fromtimestamp(myTime)

    return retval