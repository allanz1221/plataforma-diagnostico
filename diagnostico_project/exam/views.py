from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from exam.forms import NewExamForm
from exam.email import send_email_results
from exam.models import Result
from exam.models import ANSWERING, TIME_UP, FINISHED
from exam.services import generate_result_for_user, get_default_exam, finish_exam, get_settings, generate_deadline


class ExamBaseView(LoginRequiredMixin, View):
    """
    Exam Base View.
    """
    def get_user_result(self):
        return Result.objects.filter(user=self.request.user).last()


class ExamHomeView(ExamBaseView):
    """
    Exam Home View. It should be the view that welcomes the user and redirect him/her to the correct section. If a post
    is made to this view, it will create a new result.
    """
    def get(self, request, *args, **kwargs):
        """Welcome page and redirect logic"""
        result = self.get_user_result()
        if result:
            if result.status == ANSWERING:
                return redirect('exam:answering')

            if result.status == TIME_UP:
                return redirect('exam:time_up')

            if result.status == FINISHED:
                return redirect('exam:results')

        # the page should contain a new exam form
        return render(request, 'exam_home.html', {
            'result_form': NewExamForm(),
            'settings': get_settings(),
            'deadline_tmp': generate_deadline(timezone.now())
        })

    def post(self, request, *args, **kwargs):
        """Creates a new result object"""
        result = self.get_user_result()
        if not result:
            result = generate_result_for_user(request.user)

        # and redirect to the answering section
        return redirect('exam:answering')


class ExamResultsView(ExamBaseView):
    def get(self, request, *args, **kwargs):
        """Returns exam_results with the results once the exam was submitted"""
        result = self.get_user_result()

        # if it's not finished, it should return to home
        if not result or result.status != FINISHED:
            return redirect('exam:home')

        # else show the results page
        return render(request, 'exam_results.html', {
            'result': result
        })


class ExamAnsweringView(ExamBaseView):
    """
    Exam Answering View. It's the answers page of the exam.
    """
    def get(self, request, *args, **kwargs):
        """Returns the current exam to the user"""
        result = self.get_user_result()

        # only render if there is a result
        if result and result.status == ANSWERING:
            return render(request, 'exam_answering.html', {
                'exam': get_default_exam(),
                'result': result
            })

        # else it should redirect to home
        return redirect('exam:home')

    def post(self, request, *args, **kwargs):
        """Submits the exam"""
        result = self.get_user_result()

        # only accept if the status is ANSWERING
        if result.status != ANSWERING:
            return redirect('exam:error')

        ok = finish_exam(request, result)
        if not ok:
            return redirect('exam:error')

        if result.status == TIME_UP:
            return redirect('exam:time_up')

        # send an email with the results
        # try:
        #     send_email_results(result, request.user)
        # except:
        #     pass

        return redirect('exam:finished')


class ExamFinishedView(ExamBaseView):
    """
    Exam Finished View. It should inform the user that the exam was submitted correctly.
    """
    def get(self, request, *args, **kwargs):
        """Get exam finished only if the status is FINISHED"""
        result = self.get_user_result()
        if not result or result.status != FINISHED:
            return redirect('exam:home')

        return render(request, 'exam_finished.html')


class ExamTimeUpView(ExamBaseView):
    """
    Exam Time Up View. It should inform the user that the exam was submitted after its deadline.
    """
    def get(self, request, *args, **kwargs):
        """Get exam_time_up only if the status is TIME_UP"""
        result = self.get_user_result()
        if not result or result.status != TIME_UP:
            return redirect('exam:home')

        return render(request, 'exam_time_up.html', {
            'result': result
        })


class ExamErrorView(ExamBaseView):
    """
    Exam Error View. It should inform the user something wrong happened when the exam was submitted.
    """
    def get(self, request, *args, **kwargs):
        """It should only render the error page TODO: with maybe a message?"""
        result = self.get_user_result()
        return render(request, 'exam_error.html', {
            'result': result
        })

