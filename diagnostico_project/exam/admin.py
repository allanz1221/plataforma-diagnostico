import csv
from datetime import datetime

from django.contrib import admin
from django.http import HttpResponse

from exam.models import Settings, Extra, Exam, Subject, Section, Question, Answer, Response, Result


class ResponseInLine(admin.TabularInline):
    model = Response


class AnswerInLine(admin.TabularInline):
    model = Answer


class QuestionInLine(admin.TabularInline):
    model = Question


class SectionInLine(admin.TabularInline):
    model = Section


class SubjectInline(admin.TabularInline):
    model = Subject


class SettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'current_exam', 'minutes_to_finish', 'created_at', 'updated_at')


class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at', 'updated_at', 'disabled')
    search_fields = ('title', 'description')
    inlines = [SubjectInline]


class ExtraAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'disabled')
    search_fields = ('title',)


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam',)
    search_fields = ('title',)
    list_filter = ('exam__title',)
    inlines = [SectionInLine]

    def exam(self, obj):
        return obj.exam.title


class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam', 'subject',)
    search_fields = ('title',)
    list_filter = ('subject__exam__title', 'subject__title',)
    inlines = [QuestionInLine]

    def exam(self, obj):
        return obj.subject.exam.title


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'get_section', 'get_subject',)
    search_fields = ('text',)
    list_filter = ('section__subject__exam__title', 'section__subject__title', 'section__title',)
    inlines = [AnswerInLine]

    def get_section(self, obj):
        return obj.section.title

    def get_subject(self, obj):
        return obj.section.subject.title

    get_section.short_description = 'Section'
    get_section.admin_order_field = 'section__title'
    get_subject.short_description = 'Subject'
    get_subject.admin_order_field = 'section__subject__title'


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_correct', 'get_question', 'get_section', 'get_subject',)
    search_fields = ('text',)
    list_filter = ('question__section__subject__exam__title', 'question__section__subject__title',
                   'question__section__title', 'is_correct',)

    def get_question(self, obj):
        return obj.question

    def get_section(self, obj):
        return obj.question.section.title

    def get_subject(self, obj):
        return obj.question.section.subject.title

    get_question.short_description = 'Question'
    get_question.admin_order_field = 'question__text'
    get_section.short_description = 'Section'
    get_section.admin_order_field = 'question__section__title'
    get_subject.short_description = 'Subject'
    get_subject.admin_order_field = 'question__section__subject__title'


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('result', 'answer', 'created_at',)
    list_filter = ('answer__question__section__subject__exam__title', 'result__user__username', 'answer__is_correct')


class ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_name', 'first_name', 'start_time',
                    'end_time', 'deadline', 'time', 'score', 'total', 'status')
    search_fields = ('user__username',)
    inlines = [ResponseInLine]
    actions = ['export_as_csv']

    def last_name(self, obj):
        return obj.user.last_name

    def first_name(self, obj):
        return obj.user.first_name

    def exam(self, obj):
        return obj.get_exam()

    def total(self, obj):
        return obj.get_questions_count()

    def score(self, obj):
        return obj.get_correct_answers_count()

    def time(self, obj):
        return obj.get_total_time()

    def export_as_csv(self, request, queryset):
        field_names = ['user', 'last_name', 'first_name', 'start_time', 'end_time', 'deadline', 'time', 'score',
                       'total', 'status']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={} ({}).csv'.format('Reporte de resultados', str(datetime.utcnow()))
        writer = csv.writer(response)
        writer.writerow(field_names)

        for obj in queryset:
            row = []
            for field in field_names:
                if field == 'score':
                    row.append(self.score(obj))
                elif field == 'total':
                    row.append(self.total(obj))
                elif field == 'exam':
                    row.append(self.exam(obj))
                elif field == 'time':
                    row.append(self.time(obj))
                elif field == 'last_name':
                    row.append(obj.user.last_name)
                elif field == 'first_name':
                    row.append(obj.user.first_name)
                else:
                    row.append(str(getattr(obj, field)))
            writer.writerow(row)

        return response


class TimeRecordAdmin(admin.ModelAdmin):
    list_display = ('result', 'start_time', 'deadline', 'end_time', 'disabled')


admin.site.register(Settings, SettingsAdmin)
admin.site.register(Extra, ExtraAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Result, ResultAdmin)
