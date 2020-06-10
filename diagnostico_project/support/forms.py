from django import forms

from support.models import Comment, Ticket


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', 'file')
        help_texts = {
            'text': 'El contenido del comentario',
            'file': 'Adjunta un documento adicional (jpg, png o pdf)'
        }
        labels = {
            'text': 'Comentario',
            'file': 'Documento'
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 5, 'cols': 1})
        }


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'task', 'description', 'file')
        help_texts = {
            'title': 'El título de tu ticket.',
            'task': 'Define el tipo de problema que se presentó.',
            'description': 'Describe en pocas palabras el problema.',
            'file': 'En caso de que ocupes adjuntar un archivo, como una captura de pantalla, puedes hacerlo por este '
                    'medio.',
        }
        labels = {
            'title': 'Título',
            'task': 'Tipo de problema',
            'description': 'Descripción',
            'file': 'Archivo a adjuntar'
        }
