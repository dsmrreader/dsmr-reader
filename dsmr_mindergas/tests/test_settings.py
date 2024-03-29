from django.conf import settings
from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_mindergas.models.settings import MinderGasSettings


class TestSettings(TestCase):
    """Tests for settings defaults."""

    def setUp(self):
        self.instance = MinderGasSettings().get_solo()

    def test_admin(self):
        """Model should be registered in Django Admin."""
        self.assertTrue(site.is_registered(MinderGasSettings))

    def test_to_string(self):
        self.assertNotEqual(
            str(self.instance), "{} object".format(self.instance.__class__.__name__)
        )

    def test_export(self):
        self.assertFalse(self.instance.export)

    def test_auth_token(self):
        self.assertIsNone(self.instance.auth_token)

    def test_handle_settings_update_hook(self):
        sp = ScheduledProcess.objects.get(
            module=settings.DSMRREADER_MODULE_MINDERGAS_EXPORT
        )
        self.assertFalse(sp.active)

        self.instance.export = True
        self.instance.save()

        sp.refresh_from_db()
        self.assertTrue(sp.active)
