import datetime

from django.conf import settings
from django_enumfield import enum
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

class DayOfWeekEnum(enum.Enum):
    # Monday is 0 and Sunday is 6.
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    labels = {
        MONDAY: 'Monday',
        TUESDAY: 'Tuesday',
        WEDNESDAY: 'Wednesday',
        THURSDAY: 'Thursday',
        FRIDAY: 'Friday',
        SATURDAY: 'Saturday',
        SUNDAY: 'Sunday'
    }
    

class TaskStatusEnum(enum.Enum):
    PENDING = 0
    RUNNING = 1
    DONE = 2
    FAILED = 3
    KILLED = 4

    labels = {
        PENDING: 'Pending',
        RUNNING: 'Running',
        DONE: 'Done',
        FAILED: 'Failed',
        KILLED: 'Killed'
    }


def queue_command(command, user=None, force=False):
    if force or not QueuedTask.objects.filter(command=command, status=TaskStatusEnum.PENDING).exists():
        QueuedTask.objects.create(command=command, queued_by=user)

def date_from_string(date_string, use_time=False, format=settings.DATEFORMAT):
    stripped_time    = time.strptime(date_string, format)
    my_time            = time.mktime(stripped_time)
    if not use_time:
        retval        = datetime.datetime.fromtimestamp(my_time)
        retval        = retval.date()
    else:
        retval        = datetime.date.fromtimestamp(myTime)

    return retval