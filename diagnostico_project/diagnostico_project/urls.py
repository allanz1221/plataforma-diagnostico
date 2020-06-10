"""diagnostico_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from diagnostico_project import settings

urlpatterns = [
    # django auth
    path('diagnostico/admin/', admin.site.urls),
    path('diagnostico/accounts/', include('users.urls')),
    path('diagnostico/accounts/', include('django.contrib.auth.urls')),

    # apps
    path('diagnostico/', include('core.urls')),
    path('diagnostico/exam/', include('exam.urls')),
    # path('support/', include('support.urls')),
    path('diagnostico/documents/', include('documents.urls')),
    path('diagnostico/student_card/', include('student_card.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
