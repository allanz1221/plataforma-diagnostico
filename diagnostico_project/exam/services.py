from django.db import transaction
from django.utils import timezone

from exam.models import Result, Settings, Exam, Response, Answer
from exam.models import ANSWERING, TIME_UP, FINISHED


class DefaultSettings():
    """
    Dummy, hardcoded settings... just in case!
    """
    def __init__(self):
        self.current_exam = Exam.objects.last()  # default to the last exam created
        self.minutes_to_finish = 120  # more than enough


def get_settings():
    """
    Get the settings
    :return:
    """
    settings = Settings.objects.last()
    if settings:
        return settings

    # return the hardcoded default settings
    return DefaultSettings()


def generate_deadline(start_time):
    """
    Generate a deadline based on the start datetime and the settings
    :return: deadline as timezone object
    """
    settings = get_settings()
    return start_time + timezone.timedelta(minutes=settings.minutes_to_finish)


def generate_result_for_user(user):
    """
    Generate results for a user
    :param user: user instance
    :return: Created flag, created result instance
    """
    if Result.objects.filter(user=user).count() == 0:
        now = timezone.now()
        result = Result.objects.create(
            user=user,
            start_time=now,
            end_time=None,
            deadline=generate_deadline(now)
        )

        return True, result

    return False, None


def get_default_exam():
    """
    Returns the default exam
    :return: exam object
    """
    settings = get_settings()
    exam = None

    if settings.current_exam:
        exam = Exam.objects.get(pk=settings.current_exam.id)

    return exam


@transaction.atomic
def finish_exam(request, result):
    """
    Finishes the exam by creating a response object of each answer sent and changing the result status to finished
    :param request: the post request the user sent
    :param result: the result for the user
    :return: True if no errors, False if there was an error
    """
    for key in request.POST.keys():
        sid = transaction.savepoint()

        try:
            if key != 'csrfmiddlewaretoken':
                if not key.isdigit():
                    raise Exception

                answer_id = int(request.POST[key])
                answer = Answer.objects.get(id=answer_id)

                # stop everything if an answer is not found
                if not answer:
                    raise Exception

                response = Response.objects.create(result=result, answer=answer)
                response.save()
        except Exception:
            # if anything wrong happens, make a rollback
            transaction.savepoint_rollback(sid)

            # and return False
            return False

    # update the result status to finished
    if not result.is_past_deadline():
        result.status = FINISHED
    else:
        result.status = TIME_UP
    result.end_time = timezone.now()
    result.save()

    # no errors! :D
    return True
