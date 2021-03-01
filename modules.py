from .actions import ListAction, DeleteAction, ChangeAction
from django.urls import path, reverse
from django.http.response import HttpResponse


class Module(object):
    def __init__(self, *args, url_prefix=None, root_url='admin/', context=None, route_prefix=None, **kwargs):
        self.url_prefix = url_prefix or ''
        self.context = context or dict()
        self.route_prefix = route_prefix or type(self).__name__
        self.root_url = root_url

    def menu(self):
        return list()

    def actions(self):
        return list()

    def urls(self):
        urls = list()

        for action_data in self.actions():
            action = action_data.get('action')
            url = action_data.get('url', '')
            route = action_data.get('route', None)

            p = self.url_prefix
            if url != '':
                p += '/' + url

            url_path = path(p, action)

            # set route name if exists
            if self.route_prefix:
                if route is None or route == '':
                    name_suffix = ''
                else:
                    name_suffix = route

                url_path.name = self.route_prefix + name_suffix
                print('register url name', url_path.name, p)

            urls.append(url_path)

        return urls


class CrudModule(Module):
    def __init__(
            self,
            *args,
            model_class=None,
            columns=None, name=None,
            url_name_prefix=None, context=None,
            form_class=None, filter_form=None, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.model_class = model_class
        self.name = name or model_class._meta.model_name
        self.columns = columns or ['id']
        self.form_class = form_class
        self.filter_form = filter_form

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
                "url": reverse(self.route_prefix + 'index'),
            }
        ]

    def modify_actions(self, actions):
        return actions

    def actions(self):
        breadcrumbs = list()
        breadcrumbs.append({
            "url": "/%s" % self.root_url,
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

        # bc = ButtonColumn()
        # self.columns.append(bc)

        actions = [
            {
                "action": ListAction(
                    model_class=self.model_class,
                    columns=self.columns,
                    extra_context=list_context,
                    filter_form=self.filter_form,
                ),
                "url": '',
                "route": 'index',
            },
            {
                "action": ChangeAction(
                    model_class=self.model_class,
                    extra_context=create_context,
                    form_class=self.form_class,
                    back_url='/' + self.url_prefix,
                    redirect_url='/' + self.url_prefix,
                ),
                "url": 'create',
                "route": 'create',
            },
            {
                "action": ChangeAction(
                    model_class=self.model_class,
                    extra_context=create_context,
                    form_class=self.form_class,
                    back_url='/' + self.url_prefix,
                    redirect_url='/' + self.url_prefix,
                ),
                "url": 'change/<int:id>',
                "route": 'change',
            },
            {
                "action": DeleteAction(
                    model_class=self.model_class,
                    extra_context=self.context,
                    redirect_url='/' + self.url_prefix,
                ),
                "url": 'delete/<int:id>',
                "route": 'delete',
            }
        ]

        return self.modify_actions(actions)


class PageModule(Module):
    def __init__(self, *args, label=None, action=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.label = label

    def action(self, request):
        return HttpResponse('action')

    def menu(self, *args, **kwargs):
        return [
            {
                "name": self.label,
                "url": reverse(self.route_prefix)
            }
        ]

    def actions(self):
        return [
            {
                "action": self.action,
                "url": "",
                'route': "",
            }
        ]
