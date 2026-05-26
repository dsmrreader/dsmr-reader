import os

from django.utils.translation import gettext_lazy as _
from django import forms

import dsmr_backup.services.backup


class BackupSettingsAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get("daily_backup"):
            return cleaned_data

        folder = cleaned_data.get("folder")
        if folder is None:
            return cleaned_data

        backup_directory = dsmr_backup.services.backup.get_backup_directory(backup_directory=folder)

        if not os.path.exists(backup_directory):
            try:
                os.makedirs(backup_directory)
            except IOError as exc:
                raise forms.ValidationError(
                    _("Failed to create this directory, please check permissions: {}").format(backup_directory)
                ) from exc

        return cleaned_data
