from django.contrib import admin

from .models import QueuedTask, CronTask

class QueuedTaskAdmin(admin.ModelAdmin):

    list_display = ('id', 'command', 'status', 'created_on', 'last_modified', 'crontask', 'staff_member')
    search_fields = ('command', 'id')
    list_filter = ('status',)
    readonly_fields = ('staff_member', 'blocking_email_sent',
                       'stdout', 'stderr')

    actions = ['run_command_immediately']

    """
    def get_actions(self, request):
        actions = super(QueuedTasksdmin, self).get_actions(request)
        env = os.environ.get('CRONS_GROUP', None)
        if env == 'production':
            del actions['run_command_immediately']
        return actions
    """

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