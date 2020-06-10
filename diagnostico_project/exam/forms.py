from django import forms

from exam.models import Result


class NewExamForm(forms.ModelForm):
    """
    Used to create a new result for a user
    """
    class Meta:
        model = Result
        exclude = ('user', 'status', 'start_time', 'end_time', 'deadline', 'disabled')
