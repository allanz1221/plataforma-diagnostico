import csv
import io
import os
import logging
import glob
from datetime import datetime

from zipfile import ZipFile

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import forms
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path

from documents.models import Category
from exam.models import Result
from users.email import send_welcome_email
from users.forms import CandidateCreationForm, CandidateChangeForm
from users.models import Candidate
from utils.services import documentation_is_finished, student_card_is_finished


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def register_user_from_row(row):
    user, created = Candidate.objects.get_or_create(username=row['cve_ni'])
    if created:
        user.email = row['email']
        user.nombre = row['nombre']
        user.apellido_paterno = row['apell_pat']
        user.apellido_materno = row['apell_mat']

        nacimiento = row['fechaNac'].split('/')
        user.nacimiento = '{}-{}-{}'.format(nacimiento[2], nacimiento[1], nacimiento[0])

        user.telefono = row['telefono']
        user.celular = row['celular']
        user.sexo = row['sexo']
        user.sangre = row['tip_san']
        user.curp = row['curp']
        user.nss = row['NSS']
        user.edo_civil = row['edoCivil']
        user.nacionalidad = row['nacionalidad']

        user.periodo = row['per_esc']
        user.unidad = row['cve_ua']
        user.folio = row['folio']
        user.siglas = row['siglas']
        user.save()

    # skip if the user is already created
    return 0


class ExamStatusFilter(admin.SimpleListFilter):
    """Filters the Result Status"""
    title = 'examen'
    parameter_name = 'examen'

    def lookups(self, request, model_admin):
        return (
            ('Sin contestar', 'Sin contestar'),
            ('Fuera de tiempo', 'Fuera de tiempo'),
            ('Contestando', 'Contestando'),
            ('Terminado', 'Terminado'),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == 'Terminado':
            return queryset.filter(result__status=2, result__disabled=False)
        elif value == 'Fuera de tiempo':
            return queryset.filter(result__status=1, result__disabled=False)
        elif value == 'Contestando':
            return queryset.filter(result__status=0, result__disabled=False)
        elif value == 'Sin contestar':
            return queryset.exclude(result__isnull=False, result__disabled=False)

        return queryset


class DocumentsStatusFilter(admin.SimpleListFilter):
    """Filters the Document Status"""
    title = 'documentacion'
    parameter_name = 'documentacion'

    def lookups(self, request, model_admin):
        return (
            ('Pendiente', 'Pendiente'),
            ('Terminado', 'Terminado'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        categories = Category.objects.all()

        done_queryset = queryset
        for category in categories:
            done_queryset = queryset.filter(document__category_id=category.id,
                                            document__disabled=False)
        if value == 'Pendiente':
            return queryset.difference(done_queryset)
        elif value == 'Terminado':
            return done_queryset

        return queryset


class StudentCardStatusFilter(admin.SimpleListFilter):
    """Filters the Student Card Status"""
    title = 'credencial'
    parameter_name = 'credencial'

    def lookups(self, request, model_admin):
        return (
            ('Pendiente', 'Pendiente'),
            ('Terminado', 'Terminado'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        done_queryset = queryset
        for candidate in queryset:
            if not student_card_is_finished(candidate):
                done_queryset = done_queryset.exclude(id=candidate.id)

        if value == 'Pendiente':
            return queryset.difference(done_queryset)
        elif value == 'Terminado':
            return done_queryset

        return queryset


class CandidateAdmin(UserAdmin):
    add_form = CandidateCreationForm
    form = CandidateChangeForm
    model = Candidate
    change_list_template = 'admin/candidates_change_list.html'
    search_fields = ('username', 'email', 'apellido_paterno', 'apellido_materno', 'nombre')
    list_filter = ('is_staff', 'periodo', 'siglas', 'email_sent', ExamStatusFilter, DocumentsStatusFilter,
                   StudentCardStatusFilter)
    ordering = ('periodo', 'siglas', 'username')
    list_display = (
        'username', 'periodo', 'siglas', 'apellido_paterno', 'apellido_materno', 'nombre', 'email', 'examen',
        'documentacion', 'credencial', 'email_sent')
    fieldsets = (
        ('Candidate', {
            'fields': (
                'password', 'apellido_paterno', 'apellido_materno', 'nombre', 'email', 'nacimiento',
                'telefono', 'celular', 'sexo', 'sangre', 'curp', 'nss', 'nacionalidad',
                'unidad', 'periodo', 'siglas'
            )
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')})
    )
    actions = ['send_registration_email', 'download_candidate_files', 'reset_candidate_exam', 'generate_general_report']

    def send_registration_email(self, request, queryset):
        for candidate in queryset:
            password = Candidate.objects.make_random_password()
            candidate.set_password(password)
            candidate.email_sent = True
            candidate.save()
            send_welcome_email(candidate.email, candidate.nombre, candidate.username, password)

        self.message_user(request, 'Se enviaron {} correos'.format(len(queryset)))
        return redirect('.')

    def download_candidate_files(self, request, queryset):
        response = HttpResponse(content_type='application/zip')
        zip_file = ZipFile(response, 'w')

        for candidate in queryset:
            path = os.path.join('media', 'files', candidate.username)
            dir_list = glob.glob(path)

            for directory in dir_list:
                zipdir(directory, zip_file)

        zip_file.close()
        return response

    def reset_candidate_exam(self, request, queryset):
        resets = 0
        for candidate in queryset:
            result = Result.objects.filter(user_id=candidate.id).last()
            if result:
                result.disabled = True
                result.save()
                resets += 1

        self.message_user(request, 'Se resetearon {} exámene(s)'.format(resets))
        return redirect('.')

    def generate_general_report(self, request, queryset):
        field_names = ['clave_aspirante', 'periodo', 'siglas', 'apellido_paterno', 'apellido_materno', 'nombre', 'email',
                       'examen_status', 'examen_puntuacion', 'documentacion', 'credencial']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={} ({}).csv'.format('Reporte de resultados',
                                                                                    str(datetime.utcnow()))
        writer = csv.writer(response)
        writer.writerow(field_names)

        for candidate in queryset:
            row = []

            result = Result.objects.filter(user_id=candidate.id, disabled=False).last()

            for field in field_names:
                if field == 'clave_aspirante':
                    row.append(candidate.username)
                elif field == 'periodo':
                    row.append(candidate.periodo)
                elif field == 'siglas':
                    row.append(candidate.siglas)
                elif field == 'apellido_paterno':
                    row.append(candidate.apellido_paterno)
                elif field == 'apellido_materno':
                    row.append(candidate.apellido_materno)
                elif field == 'nombre':
                    row.append(candidate.nombre)
                elif field == 'email':
                    row.append(candidate.email)
                elif field == 'examen_status':
                    row.append(self.examen(candidate))
                elif field == 'examen_puntuacion':
                    if result:
                        row.append(str(result.get_correct_answers_count()))
                    else:
                        row.append('0')
                elif field == 'documentacion':
                    row.append(self.documentacion(candidate))
                elif field == 'credencial':
                    row.append(self.credencial(candidate))

            writer.writerow(row)
        return response

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]

            if not csv_file.name.endswith('.csv'):
                self.message_user(request, 'El archivo no es un csv válido')
                return redirect('..')

            if csv_file.multiple_chunks():
                self.message_user(request, 'El archivo es demasiado grande')
                return redirect('..')

            file_data = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(file_data))

            line_count = 0
            for row in reader:
                line_count += register_user_from_row(row)
            self.message_user(request, 'Se importaron correctamente {} usuario(s)'.format(line_count - 1))
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}

        return render(
            request, "admin/csv_form.html", payload
        )

    def examen(self, obj):
        """Returns the exam status"""
        result = Result.objects.filter(user_id=obj.id, disabled=False).last()
        if not result:
            return 'Sin contestar'
        if result.status == 2:
            return 'Terminado'
        elif result.status == 1:
            return 'Fuera de tiempo'
        else:
            return 'Contestando'

    def documentacion(self, obj):
        """Returns the documentation status"""
        return 'Terminado' if documentation_is_finished(obj) else 'Pendiente'

    def credencial(self, obj):
        """Returns the student card status"""
        return 'Terminado' if student_card_is_finished(obj) else 'Pendiente'


admin.site.register(Candidate, CandidateAdmin)
