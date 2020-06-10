from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.base import View
from django.views.generic.edit import FormMixin

from documents.forms import DocumentForm
from documents.models import Document, Category


def _get_exception_message(e):
    """Returns the generic exception message"""
    return 'Surgió un error desconocido al eliminar el documento. Contacta a nuestro ' \
           'equipo técnico usando el correo: <a href="mailto:uesvirtual@ues.mx">uesvirtual@ues.mx</a> ' \
           'diciendo que surgió un error tipo: {}'.format(type(e).__name__)


class DocumentsHomeView(LoginRequiredMixin, FormMixin, ListView):
    """
    Documents Home View.
    """
    template_name = 'documents_home.html'
    model = Document
    paginate_by = 5
    form_class = DocumentForm

    def get_context_data(self, **kwargs):
        """Used to attach a 'categories' object to the context"""
        context = super(DocumentsHomeView, self).get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.all()
        })
        return context

    def get_queryset(self):
        """Filters by user"""
        query_set = super(DocumentsHomeView, self).get_queryset()
        query_set = query_set.filter(user=self.request.user)
        return query_set

    def get_success_url(self):
        """Returns the url after a successful upload"""
        return reverse('documents:home')

    def post(self, request, *args, **kwargs):
        """Handles the file upload"""
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.user = request.user
            file.save()
            messages.success(request, 'El documento "{}" se subió correctamente, ¡muchas gracias!'
                             .format(form.files['file']))
            return self.form_valid(form)
        else:
            for error in form.errors['file']:
                messages.error(request, error)
            return redirect('documents:home')


class DocumentsDeleteView(View):
    """
    Documents Delete View
    """

    def post(self, request, *args, **kwargs):
        """Deletes a document"""
        try:
            document_id = request.POST['document_id']
            document = Document.objects.filter(id=document_id).last()
            document.disabled = True
            document.save()
            messages.success(request, '¡El documento fue eliminado con éxito')
        except KeyError:
            messages.error(request, 'No se encontró el documento.')
        except Exception as e:
            messages.error(request, _get_exception_message(e))

        return redirect('documents:home')

    def dispatch(self, request, *args, **kwargs):
        """Handles the case when a user tries to delete another user's document"""
        document_id = request.POST['document_id']
        document = Document.objects.filter(id=document_id).last()

        if not document:
            messages.error(request, 'No se encontró el documento.')
            return redirect('documents:home')

        if document.user.id != self.request.user.id:
            messages.error(request, 'No tiene permiso para eliminar el documento')
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
