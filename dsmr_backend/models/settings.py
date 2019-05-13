from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db import models
from solo.models import SingletonModel


class BackendSettings(SingletonModel):
    language = models.CharField(
        max_length=32,
        default='nl',
        choices=settings.LANGUAGES,
        verbose_name=_('The language used in backend processes'),
    )


class EmailSettings(SingletonModel):
    """ Outgoing email settings. """
    email_to = models.EmailField(
        max_length=255,
        default=None,
        null=True,
        blank=True,
        help_text=_('The email address you want to send any emails to')
    )
    host = models.CharField(
        max_length=255,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('Host'),
        help_text=_('The hostname of the server used to send emails with')
    )
    port = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('Port'),
        help_text=_('The port used by the email server to send mail')
    )
    username = models.CharField(
        max_length=255,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('Username'),
        help_text=_('Optional: The username required to authenticate on the email server')
    )
    password = models.CharField(
        max_length=255,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('Password'),
        help_text=_('Optional: The password required to authenticate on the email server')
    )
    use_tls = models.BooleanField(
        default=False,
        verbose_name=_('Use TLS'),
        help_text=_('Optional: Whether the email server uses TLS for encryption')
    )
    use_ssl = models.BooleanField(
        default=False,
        verbose_name=_('Use SSL'),
        help_text=_('Optional: Whether the email server uses SSL for encryption')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Email configuration')
