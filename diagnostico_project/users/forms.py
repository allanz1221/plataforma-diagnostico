from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from users.models import Candidate


class CandidateCreationForm(UserCreationForm):
    class Meta:
        model = Candidate
        fields = ('username', 'email',)


class CandidateChangeForm(UserChangeForm):
    class Meta:
        model = Candidate
        fields = ('username', 'email',)
