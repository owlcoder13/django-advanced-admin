from .actions import ListAction, DeleteAction, ChangeAction
from django.urls import path


class Module(object):
    def urls(self):
        return []

    def menu(self):
        return list()


class CrudModule(Module):
    def __init__(self, model_class, columns=None, name=None,
                 url_name_prefix=None, url_prefix='', context=None,
                 form_class=None, filter_form=None):
        self.model_class = model_class
        self.name = name or model_class._meta.model_name
        self.columns = columns or ['id']
        self.url_name_prefix = url_name_prefix or ''
        self.url_prefix = url_prefix or ''
        self.context = context
        self.form_class = form_class
        self.filter_form = filter_form

    def menu(self):
        return [
            {
                "name": self.model_class._meta.model_name,
                "url": '/' + self.url_prefix,
            }
        ]

    def modify_actions(self, actions):
        return actions

    def actions(self):
        actions = {
            '': ListAction(
                model_class=self.model_class,
                columns=self.columns,
                extra_context=self.context,
                filter_form=self.filter_form
            ),
            'create': ChangeAction(
                model_class=self.model_class,
                extra_context=self.context,
                form_class=self.form_class,
                back_url='/' + self.url_prefix,
                redirect_url='/' + self.url_prefix
            ),
            'change/<int:id>': ChangeAction(
                model_class=self.model_class,
                extra_context=self.context,
                form_class=self.form_class,
                back_url='/' + self.url_prefix,
                redirect_url='/' + self.url_prefix
            ),
            'delete': DeleteAction(model_class=self.model_class, extra_context=self.context),
        }

        return self.modify_actions(actions)

    def urls(self):
        urls = list()

        for key, action in self.actions().items():
            p = "/".join([self.url_prefix, key])
            name = '.'.join([self.url_name_prefix, key])
            urls.append(path(p, action, name=name))

        return urls
