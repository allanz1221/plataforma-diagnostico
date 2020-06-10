def get_send_email_success_message(user):
    """Email sent message"""
    return 'Se le envió un correo a {} avisándole del cambio.'.format(user.email)


def get_update_status_success_message():
    """Ticket update message"""
    return 'Se actualizó correctamente el estado del ticket.'


def get_update_status_error_message(e):
    return 'Hubo un error al actualizar el estado del ticket: {}'.format(type(e).__name__)


def get_comment_success_message():
    """Comment added message"""
    return 'Se añadió correctamente el comentario.'


def get_comment_error_message():
    """Comment error message"""
    return 'Error al añadir comentario.'


def get_exam_reset_success_message():
    """Exam reset message"""
    return 'El examen fue reiniciado con éxito, ahora puede cerrar el ticket.'


def get_exam_reset_error_message():
    """Exam reset error message"""
    return 'Hubo un error al reiniciar el examen del usuario, revisa el panel de administrador.'
