from django import template

register = template.Library()


def getattrdot(obj, path, default=None):
    if path is None:
        return obj

    for a in path.split('.'):
        if hasattr(obj, a):
            obj = getattr(obj, a)
        else:
            return default
    return obj


@register.simple_tag()
def render_column(column, item):
    return getattrdot(item, column)


@register.inclusion_tag('advanced_admin/templatetags/errors.html')
def render_form_errors(errors):
    return {"errors": errors}
