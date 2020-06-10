from django.db import models

from core.managers import CoreBaseManager


class CoreBaseModel(models.Model):
    """
    Core Base Model.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disabled = models.BooleanField(default=False)

    objects = CoreBaseManager()

    class Meta:
        abstract = True


class FaqItem(CoreBaseModel):
    """
    Faq Item. Contains a question-answer pair.
    """
    question = models.CharField(blank=False, null=False, default='', max_length=255)
    answer = models.TextField(blank=False, null=False, default='')

    def __str__(self):
        return '{}'.format(self.question)

    class Meta:
        ordering = ('id', 'question', 'created_at')
