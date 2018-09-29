from django.test import TestCase
from django.apps import apps


class TestMetaDefaultPermissions(TestCase):
    def test_default_permissions(self):
        for current_model in apps.get_app_config('dsmr_stats').get_models():
            self.assertEqual(len(current_model()._meta.default_permissions), 0, current_model)
