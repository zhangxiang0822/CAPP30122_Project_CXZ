from django import template

register = template.Library()


@register.filter
def get_first(tup):
    return tup[0]

@register.filter
def get_second(tup):
    return tup[1]

@register.filter
def get_third(tup):
    return tup[2]
