#!/usr/bin/env python3
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsmrreader.settings")

    from django.core.management import execute_from_command_line

    is_testing = 'test' in sys.argv

    if is_testing:
        import coverage
        cov = coverage.coverage(
            include=['./*'],
            omit=[
                '*/__init__.py',
                '*/tests/*',
                './*/migrations/*',
                './dsmr_backend/mixins.py'
            ],
            branch=True
        )
        cov.erase()
        cov.start()

    execute_from_command_line(sys.argv)

    if is_testing:
        cov.stop()
        cov.save()
        cov.report()
        cov.html_report(directory='coverage_report/html')
