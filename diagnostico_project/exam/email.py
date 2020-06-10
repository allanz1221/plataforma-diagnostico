from utils.email import send_mail


def send_email_results(result, user):
    """Send an email with the results"""
    email_list = [user.email]

    send_mail(subject='UES Virtual - Plataforma Diagnóstico - Reporte de resultados #{}'.format(result.id),
              template='email/exam_results_email.html',
              ctx={'result': result, 'user': user},
              recipient_list=email_list,
              fail_silently=True)
