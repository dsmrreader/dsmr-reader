from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db import models
from solo.models import SingletonModel

from dsmr_backend.mixins import ModelUpdateMixin
from dsmr_backend.signals import backend_restart_required


class BackendSettings(ModelUpdateMixin, SingletonModel):
    language = models.CharField(
        max_length=32,
        default="nl",
        choices=settings.LANGUAGES,
        verbose_name=_("Language"),
        help_text=_("The language used in backend processes"),
    )
    automatic_update_checker = models.BooleanField(
        default=True,
        verbose_name=_("Automatically check for updates"),
        help_text=_(
            "Whether the application checks once in a while for new DSMR-reader release in GitHub"
        ),
    )
    process_sleep = models.DecimalField(
        default=1,
        max_digits=4,
        decimal_places=1,
        verbose_name=_("Backend process sleep"),
        help_text=_(
            "The number of seconds the application will sleep after completing a backend run."
        ),
    )
    disable_gas_capability = models.BooleanField(
        default=False,
        verbose_name=_("Disable gas capability"),
        help_text=_(
            "Whether to disable gas capability. E.g.: you’ve switched from using gas to an alternative energy source."
        ),
    )
    disable_electricity_returned_capability = models.BooleanField(
        default=False,
        verbose_name=_("Disable electricity returned capability"),
        help_text=_(
            "Whether to disable electricity return capability. E.g.: When your smart meter erroneous reports "
            "electricity returned data, but you do not own any solar panels."
        ),
    )
    restart_required = models.BooleanField(
        default=False,
        verbose_name=_("Process restart required"),
        help_text=_(
            "Whether the backend process requires a restart. It should occur automatically."
        ),
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _("Backend configuration")


@receiver(backend_restart_required)
def _on_backend_restart_required_signal(**kwargs):
    backend_settings = BackendSettings.get_solo()
    backend_settings.restart_required = True
    # DO NOT CHANGE: Keep this save() due signal firing!
    backend_settings.save(update_fields=["restart_required"])


class EmailSettings(ModelUpdateMixin, SingletonModel):
    """Outgoing email settings."""

    email_from = models.EmailField(
        max_length=255,
        default=None,
        null=True,
        blank=True,
        verbose_name=_("Email from"),
        help_text=_("The email address you want to send any emails from"),
    )
    email_to = models.EmailField(
        max_length=255,
        default=None,
        null=True,
        blank=True,
        verbose_name=_("Email to"),
        help_text=_("The email address you want to send any emails to"),
    )
    host = models.CharField(
        max_length=255,
        default=None,
        null=True,
        blank=True,
        verbose_name=_("Host"),
        help_text=_("The hostname of the server used to send emails with"),
    )
    port = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_("Port"),
        help_text=_("The port used by the email server to send mail"),
    )
    username = models.CharField(
        max_length=255,
        default=None,
        null=True,
        blank=True,
        verbose_name=_("Username"),
        help_text=_(
            "Optional: The username required to authenticate on the email server"
        ),
    )
    password = models.CharField(
        max_length=255,
        default=None,
        null=True,
        blank=True,
        verbose_name=_("Password"),
        help_text=_(
            "Optional: The password required to authenticate on the email server"
        ),
    )
    use_tls = models.BooleanField(
        default=False,
        verbose_name=_("Use TLS"),
        help_text=_(
            "Optional: Whether to use a TLS (secure) connection when talking to the SMTP server. "
            "This is used for explicit TLS connections, generally on port 587"
        ),
    )
    use_ssl = models.BooleanField(
        default=False,
        verbose_name=_("Use SSL"),
        help_text=_(
            "Optional: Whether to use an implicit TLS (secure) connection when talking to the SMTP server. "
            "In most email documentation this type of TLS connection is referred to as SSL. "
            "It is generally used on port 465"
        ),
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _("Email configuration")
