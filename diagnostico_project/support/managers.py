from django.db import models


class SupportBaseManager(models.Manager):
    """
    Base manager.
    """
    def get_queryset(self):
        """
        Replace the default query set with a new one that filters any disabled item.
        :return: queryset with everything where disabled=False is true
        """
        return super().get_queryset().filter(disabled=False)
