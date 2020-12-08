from django import template

register = template.Library()


@register.simple_tag()
def render_column(column, item):
    return getattr(item, column)
