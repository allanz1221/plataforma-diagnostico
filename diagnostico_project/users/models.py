from django.contrib.auth.models import AbstractUser
from django.db import models

BLOOD_AP = 'A+'
BLOOD_AN = 'A-'
BLOOD_BP = 'B+'
BLOOD_BN = 'B-'
BLOOD_OP = 'O+'
BLOOD_ON = 'O-'
BLOOD_ABP = 'AB+'
BLOOD_ABN = 'AB-'

SEX_CHOICES = (
    ('M', 'Hombre'),
    ('F', 'Mujer'),
    ('O', 'Otro'),
)

BLOOD_TYPE_CHOICES = (
    (BLOOD_AP, 'A+'),
    (BLOOD_AN, 'A-'),
    (BLOOD_BP, 'B+'),
    (BLOOD_BN, 'B-'),
    (BLOOD_OP, 'O+'),
    (BLOOD_ON, 'O-'),
    (BLOOD_ABP, 'AB+'),
    (BLOOD_ABN, 'AB-'),
)


class Candidate(AbstractUser):
    # personal info
    nombre = models.CharField(max_length=255, blank=True, null=True)
    apellido_paterno = models.CharField(max_length=255, blank=True, null=True)
    apellido_materno = models.CharField(max_length=255, blank=True, null=True)
    nacimiento = models.DateField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    sexo = models.CharField(choices=SEX_CHOICES, max_length=1, blank=True, null=True)
    sangre = models.CharField(choices=BLOOD_TYPE_CHOICES, max_length=3, blank=True, null=True)
    curp = models.CharField(max_length=18, blank=True, null=True)
    nss = models.CharField(max_length=11, blank=True, null=True)
    edo_civil = models.CharField(max_length=255, blank=True, null=True)
    nacionalidad = models.CharField(max_length=255, blank=True, null=True)

    # ues info
    unidad = models.CharField(max_length=4, blank=True, null=True)
    # "clave_ni" should be the username!
    folio = models.CharField(max_length=8, blank=True, null=True)
    clave_ni = models.CharField(max_length=20, blank=True, null=True)
    clave_pa = models.CharField(max_length=6, blank=True, null=True)
    periodo = models.CharField(max_length=6, blank=True, null=True)
    siglas = models.CharField(max_length=6, blank=True, null=True)  # major

    email_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Aspirante'
        verbose_name_plural = 'Aspirantes'
        ordering = ('periodo', 'siglas', 'username',)
