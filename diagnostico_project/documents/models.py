import os

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from documents.managers import BaseManager


def get_upload_path(instance, filename):
    """Returns an upload path to organize the documents by the user's username"""
    return os.path.join('files', '{}'.format(instance.user.username), slugify(instance.category), filename)


def validate_file_type(value):
    """Check if the file to upload is a pdf or a jpeg"""
    if not value.name.endswith('.pdf') and not value.name.endswith('.jpg') and not value.name.endswith('.jpeg'):
        raise ValidationError(u'File must be an image or a pdf!')


class BaseModel(models.Model):
    """
    Base Model.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disabled = models.BooleanField(default=False)
    objects = BaseManager()

    class Meta:
        abstract = True


class Category(BaseModel):
    """
    Category Model. A category can be something like a high school certificate, a photograph, or any other document a
    user is required to upload. Each category contains an arbitrary number of documents.
    """
    name = models.CharField(blank=True, null=False, default='', max_length=255)
    description = models.CharField(blank=True, null=False, default='', max_length=255)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('disabled', 'name')

    def get_documents_by_user(self, user):
        """Returns all the uploaded documents for a user on this category"""
        documents = Document.objects.filter(user=user,
                                            category=self)
        return documents


class Document(BaseModel):
    """
    Document Model. Represents a document uploaded by a user, and each document belongs to a certain category.
    """
    file = models.FileField(upload_to=get_upload_path, validators=[validate_file_type])
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    comment = models.CharField(blank=True, default='', max_length=255)

    def __str__(self):
        return 'id: {}'.format(self.id)

    class Meta:
        ordering = ('disabled', 'user', 'category', 'created_at')
