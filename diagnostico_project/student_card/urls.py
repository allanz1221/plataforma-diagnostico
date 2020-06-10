from django.urls import path

from student_card.views import StudentCardHomeView, StudentCardUploadView, StudentInfoUpdateView, StudentCardCropView

app_name = 'student_card'
urlpatterns = [
    path('', StudentCardHomeView.as_view(), name='home'),
    path('upload', StudentCardUploadView.as_view(), name='upload'),
    path('update', StudentInfoUpdateView.as_view(), name='update'),
    path('crop', StudentCardCropView.as_view(), name='crop'),
]
