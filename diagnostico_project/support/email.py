from utils.email import send_mail, get_staff_emails


def send_new_ticket_posted(ticket):
    """Sends an email when a new ticket is posted"""
    email_list = get_staff_emails()
    email_list.append(ticket.user.email)

    send_mail(subject='UES Virtual - Plataforma Diagnóstico - Ticket de soporte #{} (abierto)'.format(ticket.id),
              template='email/new_ticket_posted.html',
              ctx={'ticket': ticket},
              recipient_list=email_list,
              fail_silently=True)


def send_new_admin_comment_posted(ticket, comment):
    """Sends an email to the user when a new staff comment is made"""
    email_list = [ticket.user.email]

    send_mail(subject='UES Virtual - Plataforma Diagnóstico - Ticket de soporte #{} (respuesta nueva)'.format(ticket.id),
              template='email/new_admin_comment_posted.html',
              ctx={'ticket': ticket, 'comment': comment},
              recipient_list=email_list,
              fail_silently=True)


def send_ticket_solved(ticket):
    """Sends an email to the user when a ticket is marked as solved"""
    email_list = [ticket.user.email]

    send_mail(subject='UES Virtual - Plataforma Diagnóstico - Ticket de soporte #{} (resuelto)'.format(ticket.id),
              template='email/ticket_solved.html',
              ctx={'ticket': ticket},
              recipient_list=email_list,
              fail_silently=True)


def send_ticket_working(ticket):
    """Sends an email to the user when a ticket is marked as working"""
    email_list = [ticket.user.email]

    send_mail(subject='UES Virtual - Plataforma Diagnóstico - Ticket de soporte #{} (resolviendo)'.format(ticket.id),
              template='email/ticket_working.html',
              ctx={'ticket': ticket},
              recipient_list=email_list,
              fail_silently=True)
