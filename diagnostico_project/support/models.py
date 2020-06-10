import os

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

# constants:
from support.managers import SupportBaseManager

PENDING = 'pending'
WORKING = 'working'
SOLVED = 'solved'


def get_upload_path(instance, filename):
    """Returns the upload path for this app"""
    return os.path.join('support', '{}'.format(instance.user.username), filename)


def validate_file_type(value):
    """Check if the file to upload is a pdf or a jpeg"""
    if not value.name.endswith('.pdf') and not value.name.endswith('.jpg') and not value.name.endswith('.jpeg') \
            and not value.name.endswith('.png'):
        raise ValidationError(u'File must be an image or a pdf!')


class SupportBaseModel(models.Model):
    """
    Support Base Model.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disabled = models.BooleanField(default=False)

    objects = SupportBaseManager()

    class Meta:
        abstract = True


class Task(SupportBaseModel):
    """
    Task Model. It's used to describe the kind of task an admin should do. Example: "reset an exam",
    "check an error", etc.
    """
    title = models.CharField(blank=True, null=False, default='', max_length=255)

    def __str__(self):
        return '{}'.format(self.title)

    class Meta:
        ordering = ('title',)


class Ticket(SupportBaseModel):
    """
    Ticket Model. A ticket an user can open. Each ticket has a task to describe it and the user that opened it.
    """
    STATUS_CHOICES = (
        (SOLVED, 'Solved'),
        (WORKING, 'Working'),
        (PENDING, 'Pending'),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    title = models.CharField(default='', null=False, blank=False, max_length=255)
    description = models.TextField(default='', blank=False)
    file = models.FileField(upload_to=get_upload_path, validators=[validate_file_type], blank=True)
    status = models.CharField(default=PENDING, choices=STATUS_CHOICES, blank=False, null=False, max_length=20)

    def __str__(self):
        return '({}) {}: {}'.format(self.id, self.user, self.description[:50])

    def get_absolute_url(self):
        return reverse('support:ticket_detail', args=[str(self.id)])

    class Meta:
        ordering = ('created_at',)


class Comment(SupportBaseModel):
    """
    Comment Model. Each ticket should have any number of comments, so the admin and the user can talk to
    each other.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(default='', blank=False)
    file = models.FileField(upload_to=get_upload_path, validators=[validate_file_type], blank=True)

    def __str__(self):
        return '({}) {}: {}'.format(self.ticket.id, self.user, self.text[:50])

    class Meta:
        ordering = ('ticket', 'created_at')
