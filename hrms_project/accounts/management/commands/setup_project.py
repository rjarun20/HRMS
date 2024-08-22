from django.core.management.base import BaseCommand
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Sets up necessary project directories'

    def handle(self, *args, **kwargs):
        logs_dir = settings.LOGS_DIR
        os.makedirs(logs_dir, exist_ok=True)
        self.stdout.write(self.style.SUCCESS(f'Successfully created logs directory at {logs_dir}'))