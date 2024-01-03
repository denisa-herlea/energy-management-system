import os
import django

from django.core.management.base import BaseCommand
from ...consumers import start_message_consumer


class Command(BaseCommand):
    help = 'Starts the message consumer for processing measurements.'

    def handle(self, *args, **options):
        start_message_consumer()
