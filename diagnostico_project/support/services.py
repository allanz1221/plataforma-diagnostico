from exam.models import Result


def get_exam_results(user):
    """Gets the results of the exam"""
    return Result.objects.filter(user=user).last()


def action_reset_exam(user):
    """Resets the exam of a user"""
    try:
        result = Result.objects.filter(user=user).last()
        result.disabled = True
        result.save()
    except Exception as e:
        return False

    # return false if there are more results
    if Result.objects.filter(user=user).count() > 0:
        return False

    return True
