from django import template
import operator
from datetime import date

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def ftimestamp(ts, fmat):
    return date.fromtimestamp(float(ts)).strftime(fmat)

@register.filter
def dictsort_val(value):
    if isinstance(value, dict):
        return sorted(value.iteritems(), key=operator.itemgetter(1), reverse=True)
    else:
        return value.items()
