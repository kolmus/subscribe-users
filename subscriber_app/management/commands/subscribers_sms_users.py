from django.core.management.base import BaseCommand
from subscriber_app.models import SubscriberSMS, Client, Users

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass