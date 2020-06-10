from django.urls import path

from documents.views import DocumentsHomeView, DocumentsDeleteView

app_name = 'documents'
urlpatterns = [
    path('', DocumentsHomeView.as_view(), name='home'),
    path('delete', DocumentsDeleteView.as_view(), name='delete'),
]
