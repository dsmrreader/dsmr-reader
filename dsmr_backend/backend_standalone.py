#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import argparse

parser = argparse.ArgumentParser(description='Backend standalone process')

curdir = os.path.dirname(__file__)
projectdir = os.path.abspath(os.path.join(curdir, '..'))
sys.path.append(projectdir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsmrreader.settings")

import django  # noqa: E402
# from django.conf import settings
django.setup()

from dsmr_backend.backend_runner import run_mule  # noqa: E402
from django.utils.translation import gettext as _  # noqa: E402


def add_arguments(parser):
    parser.add_argument(
        '--run-once',
        action='store_true',
        dest='run_once',
        default=False,
        help=_('Forces single run, overriding Infinite Command mixin')
    )


if __name__ == "__main__":
    add_arguments(parser)
    args = vars(parser.parse_args())
    run_mule(**args)
