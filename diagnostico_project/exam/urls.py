from django.urls import path
from exam.views import ExamHomeView, ExamErrorView, ExamTimeUpView, ExamResultsView, ExamFinishedView, ExamAnsweringView

app_name = 'exam'
urlpatterns = [
    path('', ExamHomeView.as_view(), name='home'),
    path('error', ExamErrorView.as_view(), name='error'),
    path('timeup', ExamTimeUpView.as_view(), name='time_up'),
    path('results', ExamResultsView.as_view(), name='results'),
    path('finished', ExamFinishedView.as_view(), name='finished'),
    path('answering', ExamAnsweringView.as_view(), name='answering'),
]
