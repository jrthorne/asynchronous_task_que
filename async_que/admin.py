from .mixins import ProtectedAdminMixin
from .models import QueuedTask, CronTask, Event
from django.contrib import admin

@admin.register(Event)
class EventAdmin(ProtectedAdminMixin, admin.ModelAdmin):
    list_display = ('created', 'summary', 'event_type', 'logged_in', 'ip_address')
    list_filter = ('event_type', 'show')
    search_fields = ('extra_detail', 'summary', 'ip_address')
    list_filter = ('event_type', 'show')
    list_per_page = 80


class QueuedTaskAdmin(admin.ModelAdmin):

    list_display = ('id', 'command', 'status', 'created', 'modified', 'crontask', 'staff_member')
    search_fields = ('command', 'id')
    list_filter = ('status',)
    list_editable = ('status', )
    readonly_fields = ('staff_member', 'stdout', 'stderr')

    actions = ['run_command_immediately']

    def run_command_immediately(self, request, queryset):
        for command in queryset:
            try:
                ret_val = run_command_with_timeout(command)
            except TimeoutException:
                print('%d - END STATUS: Killed' % command.pk)
                print('%d - RETRY: %d' % (command.pk, i + 1))
                time.sleep(settings.QUEUED_TASK_WAIT_BETWEEN_RETRIES)
            else:
                command.status = TaskStatusEnum.DONE if (ret_val == 0) else TaskStatusEnum.FAILED
                print('%d - END STATUS: %s' % (command.pk, 'Done' if (ret_val == 0) else 'Failed'))
                break
        else:
            command.status = TaskStatusEnum.KILLED

        command.staff_member = request.user
        command.save()
        self.message_user(request, "Please check your relevant tasks to see if they succeed")


class CronTaskAdmin(admin.ModelAdmin):
    list_display = ('active', 'hour', 'minute', 'day_of_month', 'day_of_week', 'command')
    list_filter = ('active', )


admin.site.register(QueuedTask, QueuedTaskAdmin)
admin.site.register(CronTask, CronTaskAdmin)