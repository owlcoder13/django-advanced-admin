from .actions import ListAction, DeleteAction, ChangeAction
from django.urls import path


class Module(object):
    def __init__(self, *args, url_prefix=None, context=None, **kwargs):
        self.url_prefix = url_prefix or ''
        self.context = context or dict()

    def urls(self):
        return []

    def menu(self):
        return list()

    def urls(self):
        urls = list()

        for key, action in self.actions().items():
            p = "/".join([self.url_prefix, key])
            urls.append(path(p, action))

        return urls


class CrudModule(Module):
    def __init__(
        self,
        *args,
        model_class=None,
        columns=None, name=None,
        url_name_prefix=None, context=None,
        form_class=None, filter_form=None, base_url=None, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.model_class = model_class
        self.name = name or model_class._meta.model_name
        self.columns = columns or ['id']
        self.url_name_prefix = url_name_prefix or ''
        self.form_class = form_class
        self.filter_form = filter_form
        self.base_url = base_url

        # context for models, and urls
        app_label = model_class._meta.app_label
        model_name = model_class._meta.model_name

        self.context.update({
            "app_label": app_label,
            "model_name": model_name,
        })

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

        breadcrumbs = list()
        breadcrumbs.append({
            "url": "/%s/" % self.base_url,
            "name": "Advanced admin",
        })
        breadcrumbs.append({
            "name": self.model_class.__name__,
            "url": '/' + self.url_prefix,
        })

        list_context = self.context.copy()
        list_context['crumbs'] = breadcrumbs

        create_bc = breadcrumbs.copy()
        create_bc.append({
            "name": 'create',
        })

        create_context = self.context.copy()
        create_context['crumbs'] = create_bc

        change_bc = breadcrumbs.copy()
        change_bc.append({
            "name": 'change',
        })
        change_context = self.context.copy()
        change_context['crumbs'] = change_bc

        actions = {
            '': ListAction(
                model_class=self.model_class,
                columns=self.columns,
                extra_context=list_context,
                filter_form=self.filter_form
            ),
            'create': ChangeAction(
                model_class=self.model_class,
                extra_context=create_context,
                form_class=self.form_class,
                back_url='/' + self.url_prefix,
                redirect_url='/' + self.url_prefix
            ),
            'change/<int:id>': ChangeAction(
                model_class=self.model_class,
                extra_context=change_context,
                form_class=self.form_class,
                back_url='/' + self.url_prefix,
                redirect_url='/' + self.url_prefix
            ),
            'delete': DeleteAction(model_class=self.model_class, extra_context=self.context),
        }

        return self.modify_actions(actions)


class PageModule(Module):
    def __init__(self, *args, label=None, action=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.label = label
        self.action = action

    def menu(self, *args, **kwargs):
        return [
            {
                "name": self.label,
                "url": '/' + self.url_prefix
            }
        ]

    def actions(self):
        return {
            "": self.action
        }
