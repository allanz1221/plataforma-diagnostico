from django import template
from roman import toRoman

register = template.Library()


@register.simple_tag
def get_subject_correct(result, subject_id):
    return result.get_correct_answers_count_by_subject(subject_id)


@register.simple_tag
def get_subject_total(result, subject_id):
    return result.get_questions_count_by_subject(subject_id)


@register.simple_tag
def get_section_correct(result, section_id):
    return result.get_correct_answers_count_by_section(section_id)


@register.simple_tag
def get_section_total(result, section_id):
    return result.get_questions_count_by_section(section_id)


@register.simple_tag
def roman(number):
    return toRoman(number)