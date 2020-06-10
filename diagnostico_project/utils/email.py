import threading

from diagnostico_project import settings

from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import get_template

from utils.lists import list_remove_duplicates


class EmailThread(threading.Thread):
    """
    Email Thread.
    """
    def __init__(self, subject, body, from_email, recipient_list, fail_silently):
        self.subject = subject
        self.body = body
        self.recipient_list = recipient_list
        self.from_email = from_email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, self.body, self.from_email, self.recipient_list)
        msg.content_subtype = 'html'
        msg.send(self.fail_silently)


def get_staff_emails():
    """Gets a list with all the admin emails"""
    return list(map(lambda x: x.email, get_user_model().objects.filter(is_staff=True).all()))


def send_mail(subject, template, ctx, recipient_list, fail_silently=False, *args, **kwargs):
    """Sends an email using a thread"""
    ctx['host'] = settings.CONFIGURED_HOST
    body = get_template(template).render(ctx)
    from_email = settings.EMAIL_FROM
    recipient_list = list_remove_duplicates(recipient_list)

    EmailThread(subject, body, from_email, recipient_list, fail_silently).start()


def send_non_threaded_email(subject, template, ctx, recipient_list, fail_silently=False, *args, **kwargs):
    body = get_template(template).render(ctx)
    from_email = settings.EMAIL_FROM
    msg = EmailMessage(subject, body, from_email, recipient_list)
    msg.content_subtype = 'html'
    msg.send(fail_silently=fail_silently)
