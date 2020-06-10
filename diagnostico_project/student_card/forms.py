import base64
import io
import re

from PIL import Image
from django import forms
from django.core.validators import RegexValidator

from student_card.models import CardInfo


class CardInfoForm(forms.ModelForm):
    """
    Card Info Form.
    """
    class Meta:
        model = CardInfo
        fields = ('user', 'emergency_contact_name', 'emergency_phone_number')


class StudentCardEmergencyForm(forms.Form):
    emergency_contact = forms.CharField(max_length=255, label='Nombre', required=False)
    emergency_telephone = forms.CharField(max_length=20, min_length=10, label='Teléfono', required=False,
                                          validators=[RegexValidator(r'^\d*$', 'Ingrese sólo dígitos como número de '
                                                                               'emergencia.')])
    organ_donor = forms.BooleanField(label='Donador de órganos', required=False)

    def set_default_values(self, card_info):
        self.fields.get('emergency_contact').initial = card_info.emergency_contact_name
        self.fields.get('emergency_telephone').initial = card_info.emergency_phone_number
        self.fields.get('organ_donor').initial = card_info.organ_donor

    def save(self, user):
        card_info = CardInfo.objects.get_or_create(user=user)[0]

        card_info.emergency_contact_name = self.cleaned_data.get('emergency_contact')
        card_info.emergency_phone_number = self.cleaned_data.get('emergency_telephone')
        card_info.organ_donor = self.cleaned_data.get('organ_donor')

        card_info.save()
        return card_info


class PhotoCropForm(forms.Form):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())
    data = forms.CharField(widget=forms.HiddenInput())

    def save(self, user):
        card_info = CardInfo.objects.get_or_create(user=user)[0]

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')
        data = self.cleaned_data.get('data')

        image_data = re.sub('^data:image/.+;base64,', '', data)
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
        cropped_image = image.crop((x, y, w + x, h + y))
        resized_image = cropped_image.resize((200, 300), Image.ANTIALIAS)
        blob = io.BytesIO()
        resized_image.save(blob, 'JPEG')
        card_info.photo.save(str(user.username) + '.jpg', blob)
        card_info.save()
        blob.close()

        return card_info


class PhotoUploadForm(forms.Form):
    max_upload_limit = 5 * 1024 * 1024
    file = forms.ImageField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')

        if len(file) > self.max_upload_limit:
            self.add_error('file', 'El archivo debe de ocupar menos de 5Mb')
