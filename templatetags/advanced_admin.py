from django import template

register = template.Library()


def getattr_dot(obj, path, default=None):
    """
        Return value by given path.
        Path must consist of dot separated strings
     """

    for a in path.split('.'):
        if hasattr(obj, a):
            obj = getattr(obj, a)
        else:
            return default
    return obj


@register.simple_tag()
def render_column(column, item):
    return getattr_dot(item, column)
