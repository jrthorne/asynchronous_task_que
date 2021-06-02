from async_que.helpers import TaskStatusEnum
from async_que.models import QueuedTask, CronTask
import datetime as dt
from django.conf import settings
from django.core.management import BaseCommand
from django.db.models import Q
from django.utils.timezone import localtime, now, activate
import pytz

QUE_LOOP_MINS = 5 # You should call this job every QUE_LOOP_MINS in crontab
MINIMUM_RUN_INTERVAL = 15 # This many minutes must pass before running the task again

class Command(BaseCommand):

    def handle(self, *args, **options):
        # The office is in Sydney, but should have time zone as part of the model
        activate(pytz.timezone("Australia/Sydney"))
        hrn = localtime(now()) # here right now
        cron_jobs = CronTask.objects.filter(active=True)
        for cj in cron_jobs.all():
            cjminute = cj.minute or 0
            chron_run_after = dt.time(hour=cj.hour, minute=cjminute)
            chron_run_before = (dt.datetime.combine(dt.date(1,1,1),chron_run_after) + dt.timedelta(minutes=QUE_LOOP_MINS+1)).time()
            has_already_run = dt.datetime.now() - dt.timedelta(minutes=MINIMUM_RUN_INTERVAL+1) 
            
            # Don't duplicate a chron added pending task on the queue
            cron_task_exists = QueuedTask.objects \
               .filter(crontask=cj) \
               .filter(Q(status=TaskStatusEnum.PENDING) | Q(status=TaskStatusEnum.RUNNING) | Q(created_on__gte=has_already_run)) \
               .exists()
            if (cj.day_of_month != None and hrn.day != cj.day_of_month) or \
               (cj.day_of_week != None and hrn.weekday() != cj.day_of_week) or \
               cron_task_exists:
                continue

            if  hrn.time() >= chron_run_after and hrn.time() <= chron_run_before:
                new_task = cj.queued_tasks.create(command=cj.command)
                print('Added %s to queued tasks' % cj.command)
