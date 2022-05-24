import logging
from typing import NoReturn

from django.core.mail.backends.smtp import EmailBackend
from django.core import mail

from dsmr_backend.models.settings import EmailSettings


logger = logging.getLogger('dsmrreader')


def send(email_from: str, email_to: str, subject: str, body: str, attachment: str = None) -> NoReturn:
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

    # Prevent hanging processes, ensure there is always a timeout set.
    email_backend.timeout = email_backend.timeout if email_backend.timeout is not None else 30

    message = mail.EmailMessage(
        subject=subject,
        body=body,
        from_email=email_from,
        to=[email_to],
        connection=email_backend,
    )

    if attachment:
        message.attach_file(attachment)

    logger.debug('Email backup: Sending an email to %s (%s)', email_to, subject)
    message.send()
