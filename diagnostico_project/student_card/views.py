from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic.base import View

from student_card.forms import CardInfoForm, StudentCardEmergencyForm, PhotoCropForm, PhotoUploadForm
from student_card.models import CardInfo
from student_card.messages import get_photo_upload_failure_message, get_photo_upload_success_message, \
    get_info_updated_message
from utils.images import convert_to_base64


class StudentCardHomeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        card_info = CardInfo.objects.get_or_create(user=request.user)[0]

        emergency_form = StudentCardEmergencyForm()
        emergency_form.set_default_values(card_info)

        return render(request, 'student_card_home.html', {
            'student_card_emergency_form': emergency_form,
            'photo_crop_form': PhotoCropForm(),
            'photo_upload_form': PhotoUploadForm(),
            'card_info': card_info
        })


class StudentCardUploadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect('student_card:home')

    def post(self, request, *args, **kwargs):
        form = PhotoCropForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, get_photo_upload_success_message())
        else:
            messages.error(request, get_photo_upload_failure_message())

        return redirect('student_card:home')


class StudentCardCropView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect('student_card:home')

    def post(self, request, *args, **kwargs):
        errors = False
        file = request.FILES['file']

        if not file.name.endswith('.jpg') and not file.name.endswith('.jpeg'):
            messages.error(request, 'El archivo debe ser una imagen jpeg.')
            errors = True

        if len(file) > (2 * 1024 * 1024):
            messages.error(request, 'El archivo debe ocupar menos de 2Mb')
            errors = True

        if errors:
            return redirect('student_card:home')

        try:
            image_data = convert_to_base64(request.FILES['file'])
        except Exception:
            messages.error(request, 'Sucedió un error desconocido al leer la imagen.')
            return redirect('student_card:home')

        return render(request, 'student_card_crop.html', {
            'image_data': image_data,
            'photo_crop_form': PhotoCropForm(initial={'data': image_data})
        })


class StudentInfoUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = StudentCardEmergencyForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, get_info_updated_message())
        else:
            for key in form.errors:
                for message in form.errors[key]:
                    messages.error(request, message)

        return redirect('student_card:home')
