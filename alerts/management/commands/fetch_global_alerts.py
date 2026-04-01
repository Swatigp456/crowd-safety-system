# alerts/management/commands/fetch_global_alerts.py
from django.core.management.base import BaseCommand
from alerts.services import RealTimeAlertManager
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch real-time global alerts from various APIs'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Fetching global real-time alerts...'))
        
        manager = RealTimeAlertManager()
        saved_count = manager.process_and_save_alerts()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully saved {saved_count} new global alerts')
        )