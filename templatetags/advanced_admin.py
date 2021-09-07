from django import template
from common.data import getattrdot

register = template.Library()




@register.simple_tag()
def render_column(column, item):
    return getattrdot(item, column)


@register.inclusion_tag('advanced_admin/templatetags/errors.html')
def render_form_errors(errors):
    return {"errors": errors}
