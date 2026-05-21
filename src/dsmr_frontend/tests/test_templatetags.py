from unittest.case import TestCase

from django.test import override_settings

from dsmr_frontend.templatetags.dsmr_frontend_extras import decimal_html


class TestDecimalHtml(TestCase):
    def test_formatting_enabled_with_decimal(self):
        """Fractional part is wrapped in a badge-decimal span when formatting is enabled."""
        result = decimal_html(1.5)
        self.assertIn('class="badge-decimal"', result)

    def test_formatting_disabled_returns_plain(self):
        """Plain localized value is returned when formatting is disabled."""
        with override_settings(DSMRREADER_DECIMAL_SIZE_FORMATTING=False):
            result = decimal_html(1.5)
            self.assertNotIn("badge-decimal", result)

    def test_integer_value_no_separator(self):
        """Values without any separator are returned as-is regardless of setting."""
        result = decimal_html(42)
        self.assertNotIn("badge-decimal", result)
        self.assertIn("42", result)

    def test_string_passthrough(self):
        """String values are accepted and formatted like any other value."""
        result = decimal_html("3.14")
        self.assertIn('class="badge-decimal"', result)

    def test_formatting_disabled_string_passthrough(self):
        with override_settings(DSMRREADER_DECIMAL_SIZE_FORMATTING=False):
            result = decimal_html("3.14")
            self.assertNotIn("badge-decimal", result)
            self.assertIn("3.14", result)
