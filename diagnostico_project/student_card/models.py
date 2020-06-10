import os

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


def get_upload_path(instance, filename):
    """Returns the upload path for this app"""
    return os.path.join('files', '{}'.format(instance.user.username), 'foto', filename)


def validate_file_type(value):
    """Check if the file to upload is a pdf or a jpeg"""
    if not value.name.endswith('.jpg') and not value.name.endswith('.jpeg'):
        raise ValidationError(u'File must be a jpg!')


class StudentCardBaseManager(models.Manager):
    """
    Base manager.
    """
    def get_queryset(self):
        """
        Replace the default query set with a new one that filters any disabled item.
        :return: queryset with everything where disabled=False is true
        """
        return super().get_queryset().filter(disabled=False)


class StudentCardBaseModel(models.Model):
    """
    Student Card Base Model
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disabled = models.BooleanField(default=False)

    objects = StudentCardBaseManager()

    class Meta:
        abstract = True


class CardInfo(StudentCardBaseModel):
    """
    Card Info.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    photo = models.ImageField(blank=True, null=True, upload_to=get_upload_path)
    emergency_contact_name = models.CharField(blank=True, null=True, max_length=255)
    emergency_phone_number = models.CharField(blank=True, null=True, max_length=255)
    organ_donor = models.BooleanField(blank=True, null=True, default=False)

    def is_complete(self):
        """Returns true if all the fields aren't null"""
        return False  # TODO!

    class Meta:
        verbose_name_plural = 'Card info'
