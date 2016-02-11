from django.test import TestCase

from dsmr_datalogger.dsmr import DSMR_MAPPING


class Dsmrmapping(TestCase):
    def test_mapping(self):
        """ Tests DSMR v4.2 code mapping. """
        SUPPORTED_CODES = (
            '0-0:1.0.0',
            '1-0:1.8.1',
            '1-0:2.8.1',
            '1-0:1.8.2',
            '1-0:2.8.2',
            '1-0:1.7.0',
            '1-0:2.7.0',
            '0-1:24.2.1',
            '0-0:96.14.0',
            '0-0:96.7.21',
            '0-0:96.7.9',
            '1-0:32.32.0',
            '1-0:52.32.0',
            '1-0:72.32.0',
            '1-0:32.36.0',
            '1-0:52.36.0',
            '1-0:72.36.0',
        )

        [self.assertIn(code, DSMR_MAPPING) for code in SUPPORTED_CODES]
