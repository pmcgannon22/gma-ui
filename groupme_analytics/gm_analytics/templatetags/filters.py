from django import template
import operator

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def div(value, arg):
    try:
        value = float(value)
        arg = float(arg)
        if arg: return value/arg
    except: pass
    return ''

@register.filter
def dictsort_val(value):
    if isinstance(value, dict):
        return sorted(value.iteritems(), key=operator.itemgetter(1), reverse=True)
    else:
        return value.items()
