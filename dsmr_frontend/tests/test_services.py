from unittest.case import TestCase

import dsmr_frontend.services


class TestServices(TestCase):
    def test_hex_color_to_rgb(self):
        self.assertEqual(
            dsmr_frontend.services.hex_color_to_rgb(hex_color='#C8C864'),
            (200, 200, 100)
        )
