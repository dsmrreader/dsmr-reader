""" Tests with PostgreSQL backend. """
from dsmrreader.config.test import *


# Use for TESTING only: ALTER USER dsmrreader CREATEDB;
DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'

# For some reason nosetests can't handle postgresql.
del TEST_RUNNER
