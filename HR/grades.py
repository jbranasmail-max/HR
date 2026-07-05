from django import template

register = template.Library()

@register.filter
def grade(value):
    try:
        value = int(value)
    except:
        return ''
    # للجانب العبادي (نظام 1-9)
    if value >= 9:
        return 'ممتاز'
    elif value == 8:
        return 'جيد جدًا'
    elif value == 7:
        return 'جيد'
    elif value >= 5:
        return 'متوسط'
    else:
        return 'ضعيف'
# templatetags/grades.py
from django import template

register = template.Library()

@register.filter
def grade(value):
    try:
        value = int(value)
    except:
        return ''
    # للجانب العبادي (نظام 1-9)
    if value >= 9:
        return 'ممتاز'
    elif value == 8:
        return 'جيد جدًا'
    elif value == 7:
        return 'جيد'
    elif value >= 5:
        return 'متوسط'
    else:
        return 'ضعيف'
