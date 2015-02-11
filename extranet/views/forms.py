# django
from django import forms


DELIMITERS = [(x, x) for x in [';', ',']] + [('\t', 'tab')]


class HoursUploadForm(forms.Form):
    file = forms.FileField()
    delimiter = forms.ChoiceField(choices=DELIMITERS)
