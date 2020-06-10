from django.urls import path

from support.views import SupportHomeView, SupportTicketDetailView, SupportTicketCreateView, \
    ResetExamActionView, ChangeStatusActionView, PostCommentActionView

app_name = 'support'
urlpatterns = [
    path('', SupportHomeView.as_view(), name='home'),
    path('create', SupportTicketCreateView.as_view(), name='ticket_create'),
    path('<int:pk>', SupportTicketDetailView.as_view(), name='ticket_detail'),
    path('<int:pk>/reset', ResetExamActionView.as_view(), name='reset_exam'),
    path('<int:pk>/comment', PostCommentActionView.as_view(), name='comment'),
    path('<int:pk>/change_status', ChangeStatusActionView.as_view(), name='change_status'),
]
