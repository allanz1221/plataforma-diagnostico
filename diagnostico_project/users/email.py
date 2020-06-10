from diagnostico_project import settings
from utils.email import send_non_threaded_email, send_mail


def send_welcome_email(email, name, username, password):
    send_non_threaded_email(subject='Registro a Plataforma Diagnóstico',
                            template='email/welcome.html',
                            recipient_list=[email],
                            fail_silently=False,
                            ctx={
                                'name': name,
                                'email': email,
                                'username': username,
                                'password': password,
                                'host': settings.CONFIGURED_HOST
                            })
