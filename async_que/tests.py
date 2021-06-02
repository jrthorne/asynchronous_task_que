from .helpers import (
    TaskStatusEnum, queue_command, record_event
    )
from .models import QueuedTask, Event
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.test import TestCase

TEST_IP = '127.0.0.1'

class FakeUser(object):

    @property
    def is_authenticated(self):
        return False

    @property
    def is_anonymous(self):
        return True


class FakeRequest(object):

    def __init__(self, user, get_key=None):
        self.session = SessionStore()
        self.session.create()
        # set any necessary session parameters here
        if user:
            self.user = user
        else:
            self.user = FakeUser()
        self.META = {
                    'X-Real-IP': TEST_IP,
                    'HTTP_HOST': 'async.com',
                    'PATH_INFO': 'app' 
                    }
        self.GET = {}  
        if get_key:
            self.GET[get_key] = 'nonesense'
        self.POST = {}


class TestQueue(TestCase):

    def setUp(self):
        self.que_command = 'my_test_management_command'

    def test_queue_task(self):
        # ./manage.py test async_que.tests.TestQueue.test_queue_task
        queue_command(self.que_command)
        self.assertTrue(QueuedTask.objects.filter(command=self.que_command, status=TaskStatusEnum.PENDING).exists())


class TestLog(TestCase):

    def setUp(self):
        self.user_email = 'test@async.com'
        self.user = User.objects.create_user(username='test', email=self.user_email)
        self.user.set_password('password')
        self.user.save()

    def test_log_event(self):
        # ./manage.py test async_que.tests.TestLog.test_log_event
        # FakeRequest was designed for something more complex
        request = FakeRequest(user=self.user)
        TESTING = 'Testing'
        TESTING_DETAIL = 'This is a test'
        record_event(summary=TESTING, extra_detail=TESTING_DETAIL, request=request)
        # assume events are being logged synchronously
        event = Event.objects.last()
        self.assertEqual(event.logged_in, self.user)
        self.assertEqual(event.ip_address, TEST_IP)
        self.assertEqual(event.summary, TESTING)
        self.assertEqual(event.extra_detail, TESTING_DETAIL)

        