from django import template

register = template.Library()

@register.filter
def addstr(arg1, arg2):
    return str(arg1) + str(arg2)

@register.filter
def getprev(num):
    return int(num)-1

@register.filter
def getnext(num):
    return int(num)+1