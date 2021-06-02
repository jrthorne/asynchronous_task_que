from .helpers import (
    TaskStatusEnum, 
    DayOfWeekEnum, 
    HOUR_CHOICES,
    MINUTE_CHOICES, 
    DOM_CHOICES,
    EventTypeEnum
    )
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class QueuedTask(models.Model):
    """
    see management commands run_pending_commands and queue_chron_tasks
    """
    created = models.DateTimeField(
        verbose_name=_('Created'), 
        db_index=True,
        auto_now_add=True,
        editable=False,)

    modified = models.DateTimeField(
        verbose_name=_('Modified'),
        db_index=True,
        auto_now=True,
        editable=False,)
    
    command = models.CharField(verbose_name=_('Command'), max_length=1024)
    crontask = models.ForeignKey('CronTask', verbose_name=_('CronTask'), blank=True, null=True, editable=False, related_name='queued_tasks', on_delete=models.SET_NULL)
    status = models.IntegerField(verbose_name=_('Status'), choices=TaskStatusEnum.choices, default=TaskStatusEnum.PENDING)
    staff_member = models.ForeignKey(User, verbose_name=_('Staff Member'), null=True, blank=True, on_delete=models.SET_NULL)
    stdout = models.TextField(verbose_name=_('Standard Output'), max_length=4096, blank=True)
    stderr = models.TextField(verbose_name=_('Standard Error'), max_length=4096, blank=True)      

    def __str__(self):
        return self.command


class CronTask(models.Model):
    """
    see management commands run_pending_commands and queue_chron_tasks
    """
    hour = models.PositiveSmallIntegerField(verbose_name=_('Hour'), choices=HOUR_CHOICES)
    minute = models.PositiveSmallIntegerField(verbose_name=_('Minute'), choices=MINUTE_CHOICES, blank=True, null=True)
    day_of_month = models.PositiveSmallIntegerField(verbose_name=_('Day Of Month'), choices=DOM_CHOICES, blank=True, null=True, help_text="no effect atm")
    day_of_week = models.PositiveSmallIntegerField(verbose_name=_('Day Of Week'), choices=DayOfWeekEnum.choices, null=True, blank=True, help_text="no effect atm")
    command = models.CharField(verbose_name=_('Command'), max_length=1024)
    active = models.BooleanField(verbose_name=_('Active'), default=True,
                    help_text='Disabled if unchecked')

    def __str__(self):
        return self.command

class Event(models.Model):

    SUMMARY_LENGTH = 132 # So Event: - summary is no more than one line

    def __str__(self):
        return '%d:- %s' % (self.id, self.summary)

    logged_in = models.ForeignKey(User, verbose_name=_('User'), null=True, blank=True, on_delete=models.PROTECT)
    created = models.DateTimeField(verbose_name=_('Created'), db_index=True, auto_now_add=True, editable=False)
    event_type = models.PositiveIntegerField(verbose_name=_('Event Type'), choices=EventTypeEnum.choices, default=EventTypeEnum.LOG)
    summary = models.CharField(verbose_name=_('Summary'), max_length=SUMMARY_LENGTH, help_text=_('Text Shown in Staff Event Log'))
    show = models.BooleanField(verbose_name=_('Show'), default=False, help_text=_('Show in Staff Event Log'))
    ip_address = models.GenericIPAddressField(verbose_name=_('IP Address'), blank=True, null=True)
    extra_detail = models.TextField(verbose_name=_('Extra Detail'), blank=True)

    class Meta:
        ordering = [ '-created' ]

    def save(self, *args, **kwargs):
        if len(self.summary) > self.SUMMARY_LENGTH:
            self.summary = self.summary[:self.SUMMARY_LENGTH]

        return super(Event, self).save(*args, **kwargs)


