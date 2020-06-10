from django.urls import path
from core.views import HomeView, DashboardView, AboutView, FaqView
from django.conf.urls.static import static

from diagnostico_project import settings

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('faq', FaqView.as_view(), name='faq'),
    path('about', AboutView.as_view(), name='about'),
    path('dashboard', DashboardView.as_view(), name='dashboard'),
]
