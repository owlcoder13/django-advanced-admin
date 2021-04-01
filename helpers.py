import types
from django.conf import settings


class ReplaceMethodMixin(object):
    def replace_method(self, method, func):
        setattr(self, method, types.MethodType(func, self))


def get_settings_value(key, default_value=None):
    if hasattr(settings, key):
        return getattr(settings, key)
    else:
        return default_value
