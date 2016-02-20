from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, **options):
        import dsmr_backup.services.backup
        dsmr_backup.services.backup.check()
        dsmr_backup.services.backup.sync()
