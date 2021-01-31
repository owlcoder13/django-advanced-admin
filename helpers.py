import types

class ReplaceMethodMixin(object):
    def replace_method(self, method, func):
        setattr(self, method, types.MethodType(func, self))