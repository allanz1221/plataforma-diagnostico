from documents.models import Category, Document
from exam.models import Result, FINISHED, TIME_UP
from student_card.models import CardInfo


def exam_is_finished(user):
    result = Result.objects.filter(user=user).last()
    if result is None:
        return False

    if result.status == FINISHED or result.status == TIME_UP:
        return True

    return False


def documentation_is_finished(user):
    categories = Category.objects.all()
    for category in categories:
        if len(Document.objects.filter(user=user, category=category)) == 0:
            return False
    return True


def student_card_is_finished(user):
    card_info = CardInfo.objects.filter(user=user).last()
    if card_info is None:
        return False

    if not bool(card_info.photo) or card_info.emergency_contact_name == '' or card_info.emergency_contact_name is None \
            or card_info.emergency_phone_number == '' or card_info.emergency_phone_number is None:
        return False

    return True

