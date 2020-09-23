from django import forms
from django.core import validators


class NullCharField(forms.CharField):
    """ Disables the ProhibitNullCharactersValidator, so we can clean it later on. """

    def __init__(self, *args, **kwargs):
        super(NullCharField, self).__init__(*args, **kwargs)
        self.validators.remove(validators.ProhibitNullCharactersValidator())


class DsmrReadingForm(forms.Form):
    telegram = NullCharField()

    def clean_telegram(self):
        """ Since we allow null characters, we should strip them right away. """
        telegram = self.cleaned_data['telegram']
        telegram = telegram.strip('\x00')
        return telegram
