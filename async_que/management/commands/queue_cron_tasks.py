import datetime
import pytz

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.timezone import localtime, now, activate

from async_que.helpers import TaskStatusEnum
from async_que.models import QueuedTask, CronTask

class Command(BaseCommand):

    def handle(self, *args, **options):
        # The office is in Sydney, but should have time zone as part of the model
        activate(pytz.timezone("Australia/Sydney"))
        hrn = localtime(now()) # here right now
        cron_jobs = CronTask.objects.filter(active=True)
        for cj in cron_jobs.all():
            cjminute = cj.minute or 0
            if cj.hour != None and (hrn.hour > cj.hour or cj.hour == hrn.hour and hrn.minute >= cjminute):
                # 23 hours before assuming they only run daily
                last_run = hrn - datetime.timedelta(hours=23, minutes=59)
                cron_task_exists = QueuedTask.objects.filter(
                    command=cj.command, 
                    created_on__gt=last_run,
                    created_on__lte=hrn
                    ).exclude(crontask=None).exists()
                if not cron_task_exists:
                    new_task = cj.queued_tasks.create(command=cj.command)
