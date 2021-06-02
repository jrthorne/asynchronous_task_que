from async_que.helpers import TaskStatusEnum
from async_que.models import QueuedTask
import datetime
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management import BaseCommand, call_command
from django.utils import timezone
import multiprocessing
import subprocess
import sys
import threading
import time

OPTION_COMMAND = "command"
ONE_HOUR = datetime.timedelta(hours=1)

class TimeoutException(Exception):
    pass


def run_command_with_timeout(command, timeout_sec=settings.QUEUED_TASK_TIMEOUT):
    args = [settings.PYTHON_COMMAND, settings.BASE_DIR + '/manage.py'] + command.command.split()

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if command.status != TaskStatusEnum.RUNNING:
        command.status = TaskStatusEnum.RUNNING
        command.save()

    timer = threading.Timer(timeout_sec, proc.kill)
    timer.start()
    out, err = proc.communicate()
    command.stdout = out
    command.stderr = err
    command.save()

    if timer.is_alive():
        timer.cancel()
        return proc.returncode

    raise TimeoutException()


class Command(BaseCommand):

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        command_help = "Full command to execute"
        parser.add_argument('--'+OPTION_COMMAND, '-'+OPTION_COMMAND[0], dest=OPTION_COMMAND,
                                        help=command_help)
        return

    def handle(self, *args, **options):

        # Don't start a new command running if one already is.
        queued_tasks = QueuedTask.objects.filter(status=TaskStatusEnum.RUNNING)
        if queued_tasks.count() > 0:
            a_while_ago = timezone.now() - ONE_HOUR
            running_too_long = queued_tasks.filter(created__lte=a_while_ago)
            command = running_too_long.first()
            one_day_ago = timezone.now() - datetime.timedelta(days=1)
            if command and (command.blocking_email_sent == None or command.blocking_email_sent < one_day_ago):
                # This is blocking the queue. Send an email once per day
                from_address = settings.SERVER_EMAIL
                to = settings.SERVER_EMAIL

                if len(to) > 0:
                    try:
                        rptmsg = 'QUEUED TASK STUCK RUNNING BLOCKING QUEUE: %s' % command.command 
                        msg = EmailMessage(to=to, from_email='Backend <%s>' % from_address, body=rptmsg,
                            subject="ERROR: AUTO_MANAGEMENT_COMMAND")
                        c = msg.send()
                        print(c)
                    except Exception as ee:
                        print('ERROR SENDING STAFF NOTIFY EMAIL %s: %s' % ( to, ee ))

                command.blocking_email_sent = timezone.now()
                command.save()
            return

        command = QueuedTask.objects.filter(status=TaskStatusEnum.PENDING).order_by('created').first()

        if not command:
            return

        print('%d - RUN COMMAND: %s' % (command.pk, command))

        for i in range(settings.QUEUED_TASK_RETRIES):
            try:
                ret_val = run_command_with_timeout(command, settings.QUEUED_TASK_TIMEOUT)

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

        command.save()

        if command.status == TaskStatusEnum.FAILED:
            from_address = settings.SERVER_EMAIL
            to = settings.SERVER_EMAIL

            if len(to) > 0:
                try:
                    rptmsg = 'ERROR RUNNING QUEUED TASK: %s' % command.command 
                    msg = EmailMessage(to=to, from_email='Backend <%s>' % from_address, body=rptmsg,
                        subject="ERROR: AUTO_MANAGEMENT_COMMAND")
                    c = msg.send()
                    print(c)
                except Exception as ee:
                    print('ERROR SENDING STAFF NOTIFY EMAIL %s: %s' % ( to, ee ))