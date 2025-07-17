from django.core.management.base import BaseCommand
from customers.tasks import ingest_data

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        ingest_data()
        self.stdout.write(self.style.SUCCESS('Ingestion task dispatched to Celery'))