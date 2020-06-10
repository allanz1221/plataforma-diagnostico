from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, ListView

from core.models import FaqItem
from utils.services import exam_is_finished, documentation_is_finished, student_card_is_finished


class HomeView(TemplateView):
    """
    The homepage view. It should be the first page that a user sees.
    """
    template_name = 'core_home.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Return to dashboard if user is logged in.
        """
        if request.user.is_authenticated:
            return redirect('core:dashboard')

        return super().dispatch(request, *args, **kwargs)


class AboutView(TemplateView):
    """
    The about section. It should contain credits, licences, etc.
    """
    template_name = 'core_about.html'


class DashboardView(LoginRequiredMixin, View):
    """
    Dashboard view. Once the user is logged in, it should provide information such as: platform news, what it should do
    next, etc.
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'core_dashboard.html', {
            'exam': exam_is_finished(request.user),
            'documents': documentation_is_finished(request.user),
            'student_card': student_card_is_finished(request.user)
        })


class FaqView(LoginRequiredMixin, ListView):
    """Lists the frequently asked questions"""
    template_name = 'core_faq.html'
    model = FaqItem
