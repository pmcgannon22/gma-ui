from django import template
import operator
from datetime import date

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(unicode(key))

@register.filter
def ftimestamp(ts, fmat):
    return date.fromtimestamp(float(ts)).strftime(fmat)

@register.filter
def fname(name, fmat):
    fmat = fmat.lower()
    try:
        nsplit = name.split(" ")
        if fmat == "fi l":
            return "%s %s" % (nsplit[0][0], nsplit[1])
        elif fmat == "fi.li.":
            return "%s.%s." % (nsplit[0][0], nsplit[1][0])
        elif fmat == "f li":
            return "%s %s" % (nsplit[0], nsplit[1][0])
        else:
            return name
    except IndexError:
        return name

@register.filter
def dictsort_val(value):
    if isinstance(value, dict):
        return sorted(value.iteritems(), key=operator.itemgetter(1), reverse=True)
    else:
        return value.items()
