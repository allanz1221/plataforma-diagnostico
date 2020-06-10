from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from exam.models import Exam, Subject, Section, Extra, Question, Answer, Result, Response, Settings
from exam.models import ANSWERING, TIME_UP, FINISHED
from exam.services import generate_result_for_user, get_settings, get_default_exam, finish_exam


class BaseExamTest(TestCase):
    def setUp(self):
        # create exams:
        self.test_exam = Exam.objects.create(title='Test exam', description='An exam created of development purposes')
        self.exam = Exam.objects.create(title='Real exam', description='An exam that will be answered by candidates')

        # add a two subjects to real exam:
        self.subject_math = Subject.objects.create(exam=self.exam, title="Math")
        self.subject_spanish = Subject.objects.create(exam=self.exam, title='Spanish')

        # create an extra for the next section
        self.extra_reading = Extra.objects.create(title="A really long text",
                                                  text="asdasdasdasdsadsadsadsadsadsadsadsadsadasd")

        # add a few sections to the subjects
        self.section_arithmetic = Section.objects.create(subject=self.subject_math,
                                                         title="Arithmetic",
                                                         instructions="Solve the following questions")
        self.section_series = Section.objects.create(subject=self.subject_math,
                                                     title="Series",
                                                     instructions="Complete the following series")
        self.section_reading = Section.objects.create(subject=self.subject_spanish,
                                                      title="Reading comprehension",
                                                      instructions="Read the text and answer the questions",
                                                      extra=self.extra_reading)

        # add a question to each section
        self.q1 = Question.objects.create(section=self.section_arithmetic,
                                          text="2+2=?")
        self.q2 = Question.objects.create(section=self.section_series,
                                          text="2... ____... 6...")
        self.q3 = Question.objects.create(section=self.section_reading,
                                          text="Get it?")

        # add the answers
        self.q1a1 = Answer.objects.create(question=self.q1, text="1", is_correct=False)
        self.q1a2 = Answer.objects.create(question=self.q1, text="2", is_correct=False)
        self.q1a3 = Answer.objects.create(question=self.q1, text="3", is_correct=False)
        self.q1a4 = Answer.objects.create(question=self.q1, text="4", is_correct=True)

        self.q2a1 = Answer.objects.create(question=self.q2, text="2", is_correct=False)
        self.q2a2 = Answer.objects.create(question=self.q2, text="4", is_correct=True)
        self.q2a3 = Answer.objects.create(question=self.q2, text="6", is_correct=False)

        self.q3a1 = Answer.objects.create(question=self.q3, text="Yes", is_correct=False)
        self.q3a2 = Answer.objects.create(question=self.q3, text="No", is_correct=True)

        self.user = get_user_model().objects.create_user(username='test_user', password='secret')


class ExamModelManagersTest(BaseExamTest):
    def test_base_manager_disable_record(self):
        self.assertEquals(Exam.objects.all().count(), 2)
        self.test_exam.disabled = True
        self.test_exam.save()
        self.assertEquals(Exam.objects.all().count(), 1, "Record not disabled")


class ExamModelsTest(BaseExamTest):
    def test_exam(self):
        self.assertIsNotNone(self.test_exam)
        self.assertEquals(self.test_exam.title, 'Test exam')

        self.assertIsNotNone(self.exam)
        self.assertEquals(self.exam.title, 'Real exam')

    def test_subjects(self):
        self.assertEquals(self.subject_math.exam, self.exam, "Doesn't belong to the correct exam")
        self.assertEquals(self.subject_spanish.exam, self.exam, "Doesn't belong to the correct exam")

        self.assertNotEqual(self.subject_math.exam, self.test_exam, "Doesn't belong to the correct exam")
        self.assertNotEqual(self.subject_spanish.exam, self.test_exam, "Doesn't belong to the correct exam")

    def test_sections(self):
        self.assertEquals(self.section_arithmetic.subject, self.subject_math, "Incorrect correct subject")
        self.assertEquals(self.section_series.subject, self.subject_math, "Incorrect correct subject")
        self.assertEquals(self.section_reading.subject, self.subject_spanish, "Incorrect correct subject")

        self.assertEquals(self.subject_math.section_set.count(), 2, "Wrong number of sections by subject")
        self.assertEquals(self.subject_spanish.section_set.count(), 1, "Wrong number of sections by subject")

    def test_question(self):
        self.assertEquals(self.q1.section, self.section_arithmetic, "Wrong section")
        self.assertEquals(self.q2.section, self.section_series, "Wrong section")
        self.assertEquals(self.q3.section, self.section_reading, "Wrong section")

        self.assertEquals(self.section_arithmetic.question_set.count(), 1, "Wrong number of questions")
        self.assertEquals(self.section_reading.question_set.count(), 1, "Wrong number of questions")
        self.assertEquals(self.section_series.question_set.count(), 1, "Wrong number of questions")

    def test_answers(self):
        self.assertEquals(self.q1a1.question, self.q1, "Wrong question")
        self.assertEquals(self.q1a2.question, self.q1, "Wrong question")
        self.assertEquals(self.q1a3.question, self.q1, "Wrong question")
        self.assertEquals(self.q1a4.question, self.q1, "Wrong question")

        self.assertEquals(self.q2a1.question, self.q2, "Wrong question")
        self.assertEquals(self.q2a2.question, self.q2, "Wrong question")
        self.assertEquals(self.q2a3.question, self.q2, "Wrong question")

        self.assertEquals(self.q3a1.question, self.q3, "Wrong question")
        self.assertEquals(self.q3a2.question, self.q3, "Wrong question")

        self.assertEquals(self.q1.answer_set.count(), 4, "Wrong number of answers")
        self.assertEquals(self.q2.answer_set.count(), 3, "Wrong number of answers")
        self.assertEquals(self.q3.answer_set.count(), 2, "Wrong number of answers")

        self.assertEquals(self.q1.answer_set.filter(is_correct=True).count(), 1, "Wrong number of correct answers")
        self.assertEquals(self.q2.answer_set.filter(is_correct=True).count(), 1, "Wrong number of correct answers")
        self.assertEquals(self.q3.answer_set.filter(is_correct=True).count(), 1, "Wrong number of correct answers")

    def test_result(self):
        # create a new result object
        result = Result.objects.create(user=self.user)
        self.assertEquals(result.status, ANSWERING, "Incorrect default for result")
        self.assertNotEqual(result.status, TIME_UP, "Incorrect default for result")
        self.assertNotEqual(result.status, FINISHED, "Incorrect default for result")

    def test_responses_case_1(self):
        # case 1: the perfect exam
        result = Result.objects.create(user=self.user)
        r1 = Response.objects.create(result=result, answer=self.q1a4)
        r2 = Response.objects.create(result=result, answer=self.q2a2)
        r3 = Response.objects.create(result=result, answer=self.q3a2)

        self.assertEquals(r1.answer.question.section.subject.exam, self.exam,
                          "Response doesn't belong to the correct exam")
        self.assertNotEqual(r1.answer.question.section.subject.exam, self.test_exam,
                            "Response doesn't belong to the correct exam")

        self.assertEquals(r2.result.user, self.user, "Response doesn't belong to the user")

        score = Response.objects.filter(result=result, answer__is_correct=True).count()
        self.assertEquals(score, 3, "Wrong score")

    def test_responses_case_2(self):
        # case 2: an ok exam
        result = Result.objects.create(user=self.user)
        r1 = Response.objects.create(result=result, answer=self.q1a4)
        r2 = Response.objects.create(result=result, answer=self.q2a1)
        r3 = Response.objects.create(result=result, answer=self.q3a2)

        score = Response.objects.filter(result=result, answer__is_correct=True).count()
        self.assertEquals(score, 2, "Wrong score")

    def test_responses_case_3(self):
        # case 3: failed exam
        result = Result.objects.create(user=self.user)
        r1 = Response.objects.create(result=result, answer=self.q1a1)
        r2 = Response.objects.create(result=result, answer=self.q2a1)
        r3 = Response.objects.create(result=result, answer=self.q3a1)

        score = Response.objects.filter(result=result, answer__is_correct=True).count()
        self.assertEquals(score, 0, "Wrong score")


class ExamModelMethodsTest(BaseExamTest):
    def setUp(self):
        super().setUp()
        self.result = Result.objects.create(user=self.user)
        self.r1 = Response.objects.create(result=self.result, answer=self.q1a4)
        self.r2 = Response.objects.create(result=self.result, answer=self.q2a2)
        self.r3 = Response.objects.create(result=self.result, answer=self.q3a2)

    def test_result_get_total_time(self):
        # initial status
        self.assertIsNone(self.result.get_total_time())

        # has start time, but not end time
        self.result.start_time = timezone.now()
        self.result.save()
        self.assertIsNone(self.result.get_total_time())

        # has end time, but status is still answering
        time_diff_hours = 1
        self.result.end_time = self.result.start_time + timedelta(hours=time_diff_hours)
        self.result.save()
        self.assertIsNone(self.result.get_total_time())

        # time up
        self.result.status = TIME_UP
        self.result.save()
        self.assertIsNone(self.result.get_total_time())

        # finished, has both end and start time
        self.result.status = FINISHED
        self.result.save()
        self.assertIsNotNone(self.result.get_total_time())

        # check if the difference is correct
        self.assertEquals(self.result.get_total_time(), timedelta(hours=1))
        self.assertNotEquals(self.result.get_total_time(), timedelta(hours=1, minutes=1))

    def test_result_is_past_deadline(self):
        # result past its deadline
        self.result.deadline = timezone.now() - timedelta(hours=1, minutes=30)
        self.result.save()
        self.assertTrue(self.result.is_past_deadline())

        # result finished on time
        self.result.deadline = timezone.now() + timedelta(hours=2)
        self.result.save()
        self.assertFalse(self.result.is_past_deadline())

    def test_result_get_correct_answers_count_by_subject(self):
        self.assertEquals(self.result.get_correct_answers_count_by_subject(self.subject_math.id), 2)
        self.assertEquals(self.result.get_correct_answers_count_by_subject(self.subject_spanish.id), 1)

    def test_result_get_correct_answers_count_by_section(self):
        self.assertEquals(self.result.get_correct_answers_count_by_section(self.section_arithmetic.id), 1)
        self.assertEquals(self.result.get_correct_answers_count_by_section(self.section_series.id), 1)
        self.assertEquals(self.result.get_correct_answers_count_by_section(self.section_reading.id), 1)

    def test_result_get_questions_count_by_subject(self):
        self.assertEquals(self.result.get_questions_count_by_subject(self.subject_math.id), 2)
        self.assertEquals(self.result.get_questions_count_by_subject(self.subject_spanish.id), 1)

    def test_result_get_questions_count_by_section(self):
        self.assertEquals(self.result.get_questions_count_by_section(self.section_arithmetic.id), 1)
        self.assertEquals(self.result.get_questions_count_by_section(self.section_series.id), 1)
        self.assertEquals(self.result.get_questions_count_by_section(self.section_reading.id), 1)

    def test_response_methods(self):
        self.assertEquals(self.r1.get_exam(), self.exam)
        self.assertEquals(self.r1.get_user(), self.user)

    def test_result_methods(self):
        self.assertEquals(self.result.get_correct_answers_count(), 3)
        self.assertEquals(self.result.get_questions_count(), 3)


class ExamViewsTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='ramon.parra@ues.mx',
            password='secret'
        )
        self.client.login(username=self.user.username, password='secret')

    def test_exam_home_view(self):
        # initial status
        response = self.client.get(reverse('exam:home'))
        self.assertTemplateUsed(response, 'exam_home.html')

        # user starts the exam, a result should be created
        result = Result.objects.create(user=self.user)
        result.start_time = timezone.now()
        result.deadline = result.start_time + timedelta(hours=2)
        result.save()
        self.assertEquals(result.status, ANSWERING)
        self.assertFalse(result.is_past_deadline())

        # after a result is created, it should be redirected to the answering part
        response = self.client.get(reverse('exam:home'))
        self.assertTemplateNotUsed(response, 'exam_home.html')
        self.assertRedirects(response, reverse('exam:answering'))

        # user finished the exam on time
        result.end_time = result.start_time + timedelta(minutes=50)
        result.status = FINISHED
        result.save()

        response = self.client.get(reverse('exam:home'))
        self.assertRedirects(response, reverse('exam:results'))

        # if the result reached its deadline, it should give a warning
        result.deadline = timezone.now() - timedelta(days=1)
        result.status = TIME_UP
        result.save()

        response = self.client.get(reverse('exam:home'))
        self.assertTrue(result.is_past_deadline())
        self.assertRedirects(response, reverse('exam:time_up'))

        # an admin may give the user a second chance, the last result should be disabled
        result.disabled = True
        result.save()

        response = self.client.get(reverse('exam:home'))
        self.assertTemplateUsed(response, 'exam_home.html')

        # then, the user must start again the test and a second result should be generated
        second_result = Result.objects.create(user=self.user)

        response = self.client.get(reverse('exam:home'))
        self.assertRedirects(response, reverse('exam:answering'))

    def test_exam_home_view_post(self):
        # the user should start without any result
        result = Result.objects.filter(user=self.user)
        self.assertEquals(result.count(), 0)
        self.assertIsNone(result.last())

        # once a post is made to the home view, it will create a new result and redirect the user to the answering
        # section
        response = self.client.post(reverse('exam:home'))
        self.assertRedirects(response, reverse('exam:answering'))
        result = Result.objects.filter(user=self.user)
        self.assertEquals(result.count(), 1)
        self.assertEquals(result.last().user, self.user)

        # if for any reason, another post is made to home, it should not create a second result
        response = self.client.post(reverse('exam:home'))
        result = Result.objects.filter(user=self.user)
        self.assertEquals(result.count(), 1)

        # and any other section should redirect to answering if:
        response = self.client.get(reverse('exam:home'))
        self.assertRedirects(response, reverse('exam:answering'))

        response = self.client.get(reverse('exam:finished'))
        self.assertRedirects(response, reverse('exam:home'), target_status_code=302)  # Redirects correctly to answering

        response = self.client.get(reverse('exam:results'))
        self.assertRedirects(response, reverse('exam:home'), target_status_code=302)  # Redirects correctly to answering

        response = self.client.get(reverse('exam:time_up'))
        self.assertRedirects(response, reverse('exam:home'), target_status_code=302)  # Redirects correctly to answering

    def test_exam_results_view(self):
        # without a result, it should be redirected to home
        response = self.client.get(reverse('exam:results'))
        self.assertTemplateNotUsed(response, 'exam_results.html')
        self.assertRedirects(response, reverse('exam:home'))

        # with a result, it should render the results template
        result = Result.objects.create(user=self.user)
        result.status = FINISHED
        result.save()

        response = self.client.get(reverse('exam:results'))
        self.assertTemplateUsed(response, 'exam_results.html')

        # if we disable the result, it should return to home
        result.disabled = True
        result.save()

        response = self.client.get(reverse('exam:results'))
        self.assertRedirects(response, reverse('exam:home'))

        # if we have a time up result, it should go from [home view] -> [time up view]
        result.disabled = False
        result.status = TIME_UP
        result.save()

        response = self.client.get(reverse('exam:results'))
        self.assertRedirects(response, reverse('exam:home'), target_status_code=302)  # TODO: Works on the browser?

    def test_exam_results_view_context(self):
        result = Result.objects.create(user=self.user)
        result.status = FINISHED
        result.save()

        # check if the view has a result context
        response = self.client.get(reverse('exam:results'))
        self.assertIsInstance(response.context['result'], Result)

    def test_exam_finished_view_template(self):
        # like the other views, without a result it should redirect to home
        response = self.client.get(reverse('exam:finished'))
        self.assertTemplateNotUsed(response, 'exam_finished.html')
        self.assertRedirects(response, reverse('exam:home'))

        # with a result, it should render the finished template
        result = Result.objects.create(user=self.user)
        result.status = FINISHED
        result.save()

        response = self.client.get(reverse('exam:finished'))
        self.assertTemplateUsed(response, 'exam_finished.html')

        # if the result has the status of ANSWERING or TIME_UP it should redirect to to home
        result.status = ANSWERING
        result.save()

        response = self.client.get(reverse('exam:finished'))
        self.assertRedirects(response, reverse('exam:home'), target_status_code=302)

        result.status = TIME_UP
        result.save()

        response = self.client.get(reverse('exam:finished'))
        self.assertRedirects(response, reverse('exam:home'), target_status_code=302)

    def test_exam_answering_get_view(self):
        # you can't be on the answering template if a result doesn't exist
        response = self.client.get(reverse('exam:answering'))
        self.assertRedirects(response, reverse('exam:home'))

        # and to create a result, you should post to home
        response = self.client.post(reverse('exam:home'))
        exam = Exam.objects.create(title='Test exam', description='Remember to create an exam!')
        response = self.client.get(reverse('exam:answering'))
        self.assertTemplateUsed(response, 'exam_answering.html')

        # it should always contain the result and the exam object
        self.assertIsInstance(response.context['result'], Result)
        self.assertIsInstance(response.context['exam'], Exam)

    def test_exam_error_view(self):
        pass


class ExamViewsLoadedExamTest(BaseExamTest):
    def setUp(self):
        super().setUp()
        self.client.login()
        self.client.login(username=self.user.username, password='secret')

    def test_finish_exam_ideal_scenario(self):
        # get the exam
        response = self.client.post(reverse('exam:home'))

        # it should create a result object
        result = Result.objects.filter(user=self.user).last()
        self.assertIsNotNone(result)
        self.assertEquals(result.user.id, self.user.id)
        self.assertIsNotNone(result.start_time)
        self.assertIsNone(result.end_time)
        self.assertIsNotNone(result.deadline)
        self.assertEquals(result.status, ANSWERING)

        # finish the exam as expected
        response = self.client.post(reverse('exam:answering'), {
            str(self.q1.id): str(self.q1a4.id),
            str(self.q2.id): str(self.q2a2.id),
            str(self.q3.id): str(self.q3a2.id)
        })

        responses = result.response_set.all()

        # received and created 3 responses
        self.assertEquals(responses.count(), 3)

        # all of them were correct
        self.assertEquals(result.get_correct_answers_count(), 3)

        # if we try to post again, it should return to an error so the user can see what a cheater he/she is
        response = self.client.post(reverse('exam:answering'), {
            str(self.q1.id): str(self.q1a4.id),
            str(self.q2.id): str(self.q2a2.id),
            str(self.q3.id): str(self.q3a2.id)
        })
        self.assertRedirects(response, reverse('exam:error'))

        result = Result.objects.filter(user=self.user).last()

        # and it also should not affect the number of responses
        responses = result.response_set.all()
        self.assertEquals(responses.count(), 3)

        # because the result status is finished
        self.assertEquals(result.status, FINISHED)

        # but for any reason, we can disable the result so the user can answer the exam again
        result.disabled = True
        result.save()

        # so we can get again the exam to generate another result...
        response = self.client.post(reverse('exam:home'))
        new_result = Result.objects.filter(user=self.user).last()
        self.assertNotEquals(result.id, new_result.id)

        # answer it again...
        response = self.client.post(reverse('exam:answering'), {
            str(self.q1.id): str(self.q1a4.id),
            str(self.q2.id): str(self.q2a1.id),
            str(self.q3.id): str(self.q3a1.id)
        })

        responses = result.response_set.all()

        # and see different results!
        self.assertEquals(responses.count(), 3)
        self.assertEquals(new_result.get_correct_answers_count(), 1)

        # and because we overwrote the default model manager, the admin panel should only show the last result:
        results = Result.objects.all()
        self.assertEquals(results.count(), 1)

    def test_finish_exam_time_up(self):
        # get the exam
        response = self.client.post(reverse('exam:home'))

        # it should create a result object
        result = Result.objects.filter(user=self.user).last()

        # however, we will modify its deadline
        result.deadline = timezone.now() - timezone.timedelta(days=1)
        result.save()

        # if we check it, it should be expired:
        self.assertTrue(result.is_past_deadline())

        # now, the user will finish the exam as expected
        response = self.client.post(reverse('exam:answering'), {
            str(self.q1.id): str(self.q1a4.id),
            str(self.q2.id): str(self.q2a2.id),
            str(self.q3.id): str(self.q3a2.id)
        })

        # but it will be redirected to time_up!
        self.assertRedirects(response, reverse('exam:time_up'))

        # the results will be saved as usual
        result = Result.objects.filter(user=self.user).last()
        self.assertEquals(result.response_set.count(), 3)


class ExamServicesTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='ramon.parra@ues.mx',
            password='secret'
        )
        self.client.login(username=self.user.username, password='secret')
        self.first_exam = Exam.objects.create()
        self.current_exam = Exam.objects.create()

    def test_get_settings(self):
        settings = get_settings()

        # it should never return None:
        self.assertIsNotNone(settings)

        # in the case it doesn't exist a settings object on the database, it should return the defaults
        self.assertIsNotNone(settings.current_exam)
        self.assertIsInstance(settings.current_exam, Exam)

        self.assertIsNotNone(settings.minutes_to_finish)
        self.assertIsInstance(settings.minutes_to_finish, int)

        # if we create a settings record, it should return that
        new_settings = Settings.objects.create(current_exam=self.first_exam, minutes_to_finish=60)
        new_settings.save()

        settings = get_settings()
        self.assertEquals(settings.current_exam, self.first_exam)
        self.assertEquals(settings.minutes_to_finish, 60)

        # however, if we create a second one, it will ignore the last one created
        newer_settings = Settings.objects.create(current_exam=self.current_exam, minutes_to_finish=120)
        newer_settings.save()

        settings = get_settings()
        self.assertEquals(settings.current_exam, self.current_exam)
        self.assertEquals(settings.minutes_to_finish, 120)

    def test_generate_result_for_user(self):
        # when its first called, it should return a flag and the result
        created, result = generate_result_for_user(self.user)

        self.assertTrue(created)
        self.assertIsNotNone(result)

        # the result object should contain all the necessary information to start the exam:
        self.assertIsNotNone(result.start_time)
        self.assertIsNotNone(result.deadline)
        self.assertIsNone(result.end_time)

        self.assertEquals(result.status, ANSWERING)

        # if its called again, it should return a False flag and a None result
        created, result = generate_result_for_user(self.user)

        self.assertFalse(created)
        self.assertIsNone(result)


class ExamServicesNoConfigTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='ramon.parra@ues.mx',
            password='secret'
        )
        self.client.login(username=self.user.username, password='secret')

    def test_get_default_exam(self):
        # if there is nothing configured, it should return none
        default_exam = get_default_exam()
        self.assertIsNone(default_exam)

        # if we create a new one, it should default to it
        exam1 = Exam.objects.create(title='Exam 1', description='Test exam 1')
        exam1.save()

        default_exam = get_default_exam()
        self.assertIsNotNone(default_exam)

        # once an exam is created and loaded to a settings object, it should return it as usual
        exam2 = Exam.objects.create(title='Exam 2', description='Test exam 2')
        exam2.save()

        settings = Settings.objects.create(current_exam=exam2)
        settings.save()

        default_exam = get_default_exam()
        self.assertIsNotNone(default_exam)
        self.assertIs(exam2.id, default_exam.id)
        self.assertIsNotNone(exam1.id, default_exam.id)


class ExamServicesLoadedExamTest(BaseExamTest):
    class MockRequest:
        def __init__(self, post={}):
            self.POST = post

        def keys(self):
            return self.POST.keys()

        def get(self, key):
            return self.POST.get(key)

    def setUp(self):
        super().setUp()
        self.client.login()
        self.client.login(username=self.user.username, password='secret')

    def test_finish_exam(self):
        # generate a result
        result1 = Result.objects.create(user=self.user)

        # correct post
        request = self.MockRequest({
            str(self.q1.id): str(self.q1a4.id),
            str(self.q2.id): str(self.q2a2.id),
            str(self.q3.id): str(self.q3a2.id)
        })

        finish_ok = finish_exam(request, result1)
        self.assertTrue(finish_ok)

        # incorrect post
        result2 = Result.objects.create(user=self.user)
        request = self.MockRequest({
            'a': '1',
            'b': '2',
            'c': '3'
        })
        finish_ok = finish_exam(request, result2)
        self.assertFalse(finish_ok)

        # using integers should fail
        result3 = Result.objects.create(user=self.user)
        request = self.MockRequest({
            self.q1.id: self.q1a1.id,
            self.q2.id: self.q2a1.id,
            self.q3.id: self.q3a1.id,
        })
        finish_ok = finish_exam(request, result3)
        self.assertFalse(finish_ok)

        # mixing it should fail
        result4 = Result.objects.create(user=self.user)
        request = self.MockRequest({
            self.q1.id: self.q1a1.id,
            'a': 'asdf',
            100: '1'
        })
        finish_ok = finish_exam(request, result4)
        self.assertFalse(finish_ok)

        # and it also should not create the only correct response (as it should be an atomic operation)
        self.assertEquals(result4.response_set.all().count(), 0)

    def test_finish_exam_deadline(self):
        result = Result.objects.create(user=self.user)
        result.deadline = timezone.now() - timedelta(hours=1)
        result.save()

        request = self.MockRequest({
            str(self.q1.id): str(self.q1a4.id),
            str(self.q2.id): str(self.q2a2.id),
            str(self.q3.id): str(self.q3a2.id)
        })

        finish_ok = finish_exam(request, result)
        self.assertTrue(finish_ok)

        # update the result object
        result = Result.objects.get(pk=result.id)

        # it should have a time_up flag
        self.assertEquals(result.status, TIME_UP)

        # but it should also save all the responses (just in case!)
        self.assertEquals(result.response_set.count(), 3)
