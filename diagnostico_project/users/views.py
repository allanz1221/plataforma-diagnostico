from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import CandidateCreationForm


class SignUpView(CreateView):
    form_class = CandidateCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
