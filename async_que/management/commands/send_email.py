from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management import BaseCommand, call_command, CommandError
from django.utils import timezone

from async_que.helpers import TaskStatusEnum
from async_que.models import QueuedTask

OPTION_EMAIL = "address"

class Command(BaseCommand):

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        command_help = "Email address to send to"
        parser.add_argument('--'+OPTION_EMAIL, '-'+OPTION_EMAIL[0], dest=OPTION_EMAIL,
                                        help=command_help)
        return

    def handle(self, *args, **options):
        self.to_email = [options.get(OPTION_EMAIL)]
        from_address = settings.SERVER_EMAIL

        if self.to_email:
            try:
                rptmsg = 'TEST RUNNING QUEUED TASK' 
                msg = EmailMessage(to=self.to_email, from_email='IntroTravel Backend <%s>' % from_address, body=rptmsg,
                    subject="ASYNCRONOUS_MANAGEMENT_COMMAND")
                c = msg.send()
                print(c)
            except Exception as ee:
                print('ERROR SENDING STAFF NOTIFY EMAIL %s: %s' % ( self.to_email, ee ))

        else:
            raise CommandError("No email address provided")
