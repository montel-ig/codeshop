# django
from django import forms
from django.contrib.auth.models import User

# extranet
from models import Project


DELIMITERS = [(x, x) for x in [';', ',']] + [('\t', 'tab')]


class HoursUploadForm(forms.Form):

    file = forms.FileField()
    delimiter = forms.ChoiceField(choices=DELIMITERS)

    def __init__(self, user, *args, **kwargs):
        super(HoursUploadForm, self).__init__(*args, **kwargs)

        if user.is_superuser:

            def iter_coders():
                for project in Project.objects.all():
                    for user in project.coder_team.user_set.all():
                        yield user

            coders = [('0', u'-')] + [(o.id, str(o))
                                      for o in set(iter_coders())]
            self.fields['assign_hours_to'] = forms.ChoiceField(choices=coders)
