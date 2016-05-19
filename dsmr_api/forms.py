from django import forms


class DsmrReadingForm(forms.Form):
    telegram = forms.CharField()
