from django import forms

from documents.models import Document


class DocumentForm(forms.ModelForm):
    """
    Document Form. Uploads a document
    """
    max_upload_limit = 5 * 1024 * 1024

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        if len(file) > self.max_upload_limit:
            self.add_error('file', 'El archivo debe de ocupar menos de 5Mb')

    class Meta:
        model = Document
        fields = ('category', 'comment', 'file')
        help_texts = {
            'category': 'El tipo de documento',
            'comment': 'Escribe un comentario acerca del archivo',
            'file': 'El archivo que vas a subir'
        }
        labels = {
            'category': 'Tipo de documento',
            'comment': 'Comentarios / Notas acerca del documento',
            'file': 'Archivo'
        }
