from django.contrib.auth.models import User
from django.db import models
from django_enumfield import enum

from .helpers import (
    TaskStatusEnum, 
    DayOfWeekEnum, 
    HOUR_CHOICES,
    MINUTE_CHOICES, 
    DOM_CHOICES
    )

class QueuedTask(models.Model):
    created_on = models.DateTimeField(
        'created on',
        db_index=True,
        auto_now_add=True,
        editable=False,)

    last_modified = models.DateTimeField(
        'last modified',
        db_index=True,
        auto_now=True,
        editable=False,)
    
    blocking_email_sent = models.DateTimeField(blank=True, null=True, 
        help_text='If a task is stuck running, I send an email to managers once')
    command = models.CharField(max_length=1024)
    crontask = models.ForeignKey('CronTask', blank=True, null=True, editable=False, related_name='queued_tasks')
    status = enum.EnumField(TaskStatusEnum, default=TaskStatusEnum.PENDING)
    staff_member = models.ForeignKey(User, null=True, blank=True)
    stdout = models.TextField(max_length=4096, blank=True)
    stderr = models.TextField(max_length=4096, blank=True)      

    def __unicode__(self):
        return self.command


class CronTask(models.Model):
    hour = models.PositiveSmallIntegerField(choices=HOUR_CHOICES, blank=True, null=True)
    minute = models.PositiveSmallIntegerField(choices=MINUTE_CHOICES, blank=True, null=True)
    day_of_month = models.PositiveSmallIntegerField(choices=DOM_CHOICES, blank=True, null=True, help_text="no effect atm")
    day_of_week = enum.EnumField(DayOfWeekEnum, null=True, blank=True, help_text="no effect atm")
    command = models.CharField(max_length=1024)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.command


