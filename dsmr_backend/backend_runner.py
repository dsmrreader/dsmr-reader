#!/usr/bin/env python3
import os
import sys

def backend_mule():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsmrreader.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line([sys.argv[0],"dsmr_backend"])


if __name__ == "__main__":
    backend_mule()
