from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models

from exam.managers import BaseManager

# constants
ANSWERING = 0
TIME_UP = 1
FINISHED = 2


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disabled = models.BooleanField(default=False)
    objects = BaseManager()

    class Meta:
        abstract = True


class Exam(BaseModel):
    """
    The exam class. It defines an exam that can be applied to any number of candidates. It should be related to any
    number of subjects. The title should be something like period where it should be applied (like 2019-01).
    """
    title = models.CharField(null=False, blank=True, default='', max_length=255)
    description = models.TextField(null=False, blank=True, default='')

    def __str__(self):
        return '{}'.format(self.title)


class Settings(BaseModel):
    """
    Before starting to apply exams, there should be a settings instance. This instance dictates the current settings of
    the platform, like the current exam and how many minutes should take to finish it.
    """
    current_exam = models.ForeignKey(Exam, null=False, on_delete=models.CASCADE)
    minutes_to_finish = models.PositiveIntegerField(null=False, blank=False, default=120)

    def __str__(self):
        return 'Settings {}'.format(self.id)

    class Meta:
        verbose_name_plural = 'Settings'


class Extra(BaseModel):
    """
    Each instance represents anything extra that can be attached to a subject. Like a long text that a user should read
    before answering the questions, a series of equations, etc.
    """
    title = models.CharField(default='', blank=True, null=False, max_length=255)
    text = models.TextField(default='', blank=True, null=False)
    image = models.ImageField(blank=True, null=True, upload_to='exam/')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)


class Subject(BaseModel):
    """
    The subject class. An exam can have any number of subjects, and each subject can have any number of sections. A
    subject may be something like "Math".
    """
    exam = models.ForeignKey(Exam, null=False, on_delete=models.CASCADE)
    title = models.CharField(default='', blank=True, null=False, max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('exam__id', 'id', 'title', 'created_at',)


class Section(BaseModel):
    """
    The section class. A subject may have an arbitrary number of sections, and each section may have an arbitrary number
    of questions. A section can be something like "Arithmetic".
    """
    title = models.CharField(default='', blank=True, null=False, max_length=255)
    instructions = models.TextField(default='', blank=True, null=False)
    extra = models.ForeignKey(Extra, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    subject = models.ForeignKey(Subject, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return '%s::%s' % (self.subject, self.title)

    class Meta:
        ordering = ('subject', 'id')


class Question(BaseModel):
    """
    The question model. A section can have any number of questions, and each question can have any number of answers. A
    question should be something like: "2+2=?". If necessary, a question can have an image.
    """
    text = models.TextField(default='', blank=True, null=False)
    image = models.ImageField(blank=True, null=True, upload_to='exam/')
    section = models.ForeignKey(Section, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return '%s::%s::%s...' % (self.section.subject.title, self.section.title, self.text[0:10])

    class Meta:
        ordering = ('-section__subject__id', '-section__id', 'id')


class Answer(BaseModel):
    """
    The answer model. A question can have any number of answers, and each answer may or may not be correct. An answer
    can be something like "2". If necessary, it can have an image.
    """
    text = models.TextField(default='', blank=True, null=False)
    image = models.ImageField(blank=True, null=True, upload_to='exam/')
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return '%s::%s... (%s)' % (self.question,
                                self.text[0:10] if self.text else '',
                                'correct' if self.is_correct else 'incorrect')

    class Meta:
        ordering = ('question__id', 'id', 'created_at')


class Result(BaseModel):
    """
    The result model. Each time a candidate starts to answer the exam a new Result instance should be created. By
    default, its status will be "ANSWERING". Once the candidate finishes his/her exam, the status should be changed to
    "FINISHED", however, if the candidate runs out of time it should be changed to "TIME_UP". This model is used to
    dynamically generate the results in the admin panel.
    """
    STATUS_CHOICES = (
        (ANSWERING, 'Answering'),
        (TIME_UP, 'Time up'),
        (FINISHED, 'Finished'),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    status = models.IntegerField(default=ANSWERING, choices=STATUS_CHOICES, blank=False, null=False)
    start_time = models.DateTimeField(null=True, auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True, default=None)
    deadline = models.DateTimeField(null=True, default=timezone.now() + timezone.timedelta(minutes=120))

    @property
    def last_response(self):
        return Response.objects.select_related('answer', 'answer__question', 'answer__question__section',
                                               'answer__question__section__subject',
                                               'answer__question__section__subject__exam') \
            .filter(result_id=self.id)\
            .last()

    @property
    def exam(self):
        if not self.last_response:
            return None

        return self.last_response.answer.question.section.subject.exam

    def get_exam(self):
        """Returns the related exam object"""
        if not self.last_response:
            return None

        return self.exam

    @property
    def responses(self):
        return Response.objects.select_related('result', 'answer',
                                               'answer__question',
                                               'answer__question__section').filter(result_id=self.id)

    @property
    def questions(self):
        return Question.objects.select_related('section', 'section__subject').filter(section__subject__exam_id=self.exam.id)

    def get_correct_answers_count(self):
        """Returns the number of correct answers"""
        return self.responses.filter(answer__is_correct=True).count()

    def get_correct_answers_count_by_subject(self, subject_id):
        """Returns the number of correct answers by subject"""
        return self.responses.filter(answer__question__section__subject__id=subject_id,
                                     answer__is_correct=True).count()

    def get_correct_answers_count_by_section(self, section_id):
        """Returns the number of correct answers by section"""
        return self.responses.filter(answer__question__section__id=section_id,
                                     answer__is_correct=True).count()

    def get_questions_count(self):
        """Returns the number of questions"""
        if not self.exam:
            return 0

        return self.questions.count()

    def get_questions_count_by_subject(self, subject_id):
        """Returns the number of questions by subject"""
        if not self.exam:
            return 0
        return self.questions.filter(section__subject__id=subject_id).count()

    def get_questions_count_by_section(self, section_id):
        """Returns the number of questions by section"""
        if not self.exam:
            return 0
        return self.questions.filter(section_id=section_id).count()

    def get_total_time(self):
        """Get the total time between start_time and end_time"""
        if self.status != FINISHED:
            return None

        if not self.start_time or not self.end_time:
            return None

        return self.end_time - self.start_time

    def is_past_deadline(self):
        """See if this result is past its deadline"""
        if self.status == TIME_UP:
            return True

        if self.status == FINISHED:
            return False

        return timezone.now() > self.deadline

    def __str__(self):
        return '{} ({})'.format(self.pk, self.user)

    class Meta:
        ordering = ('user', 'disabled')


class Response(BaseModel):
    """
    The response model. Each response is an answer chosen by a candidate, they are used to calculate the score
    dynamically.
    """
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def get_exam(self):
        return self.answer.question.section.subject.exam

    def get_user(self):
        return self.result.user

    def __str__(self):
        return '{} ({})'.format(self.result.user, self.answer.is_correct)

    class Meta:
        ordering = ('result', '-answer__question__id')
