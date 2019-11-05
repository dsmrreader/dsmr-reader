import logging

from django.core.mail.backends.smtp import EmailBackend
from django.core import mail

from dsmr_backend.models.settings import EmailSettings


logger = logging.getLogger('commands')


def send(to, subject, body, attachment=None):
    """ Sends an email using the outgoing email settings. """
    email_settings = EmailSettings.get_solo()

    logger.debug(
        'Email: Preparing to send email using mail server %s:%s',
        email_settings.host,
        email_settings.port
    )
    email_backend = EmailBackend(
        host=email_settings.host,
        port=email_settings.port,
        username=email_settings.username,
        password=email_settings.password,
        use_tls=email_settings.use_tls,
        use_ssl=email_settings.use_ssl
    )

    # Force translations.
    message = mail.EmailMessage(
        subject=subject,
        body=body,
        from_email=to,
        to=[to],
        connection=email_backend,
    )

    if attachment:
        message.attach_file(attachment)

    logger.debug('Email backup: Sending an email to %s (%s)', to, subject)
    message.send()
