from django.core.management.base import BaseCommand
from django.utils import timezone
from app.tasks import check_office_hours
import time
import logging
import pytz

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Checks office hours and automatically stops tasks when needed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Interval in seconds between checks (default: 60)'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        karachi_tz = pytz.timezone('Asia/Karachi')
        self.stdout.write(self.style.SUCCESS(f'Starting office hours checker (checking every {interval} seconds)...'))
        
        while True:
            try:
                current_time = timezone.now().astimezone(karachi_tz)
                self.stdout.write(f'Checking office hours at {current_time.strftime("%Y-%m-%d %H:%M:%S %Z")}...')
                
                check_office_hours()
                
                self.stdout.write(self.style.SUCCESS('Check completed successfully'))
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('\nStopping office hours checker...'))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
                logger.error(f'Error in check_office_hours command: {str(e)}')
                time.sleep(interval)  # Still sleep on error to prevent rapid retries 