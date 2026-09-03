from django.core.management.base import BaseCommand
from core.services.calendar_service import sync_calendar_events

class Command(BaseCommand):
    help = 'Synchronizes default festival and holiday calendar events into DB'

    def handle(self, *args, **options):
        total, created = sync_calendar_events()
        self.stdout.write(self.style.SUCCESS(f'Successfully synchronized {total} calendar events ({created} new created).'))
