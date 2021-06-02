from async_que.helpers import record_event
from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
    	extra_detail = """
    	'The test management command just ran (test_mgt_com.py).'
    	'The test management command just ran (test_mgt_com.py).'
    	'The test management command just ran (test_mgt_com.py).'
    	'The test management command just ran (test_mgt_com.py).'
    	'The test management command just ran (test_mgt_com.py).'
    	'The test management command just ran (test_mgt_com.py).'
    	"""
    	record_event(summary='Test Management Command', 
    		extra_detail=extra_detail)
    	print(extra_detail)