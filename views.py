from django.db.models import Model
from django.urls import path
from django.shortcuts import render, redirect
from typing import Type
from django.urls import reverse
from django.http.response import HttpResponseNotFound


class Action(object):
    def run(self, request):
        pass

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)


class AdminModule(object):
    def __init__(self):
        pass

    def urls(self):
        return []


class ListAction(Action):
    def __init__(self, model_class, columns, extra_context=None, filter_form=None):
        self.model_class = model_class  # type: Model
        self.columns = columns
        self.extra_context = extra_context or dict()
        self.filter_form = filter_form

    def run(self, request):
        breadcrumbs = list()
        breadcrumbs.append({
            "url": "/advanced_admin/",
            "name": "Advanced admin",
        })
        breadcrumbs.append({
            "name": self.model_class.__name__,
        })

        if self.filter_form is not None:
            filter = self.filter_form()
            filter.load(request.GET)
            m = filter.get_model()
        else:
            filter = None
            m = self.model_class.objects.all()

        context = dict()
        context.update(self.extra_context)
        context.update({
            "filter": filter,
            "crumbs": breadcrumbs,
            "model": m,
            "title": "list of %s" % self.model_class._meta.model_name,
            "columns": self.columns,
        })

        return render(request, 'advanced_admin/crud/list.html', context)


class ChangeAction(Action):
    def __init__(self, model_class, extra_context=None, form_class=None, redirect_url=None, back_url=None):
        self.model_class = model_class  # type: Type[Model]
        self.extra_context = extra_context or dict()
        self.redirect_url = redirect_url
        self.back_url = back_url
        self.form_class = form_class

    def run(self, request, id=None):
        breadcrumbs = list()
        breadcrumbs.append({
            "url": "/advanced_admin/",
            "name": "Advanced admin",
        })
        breadcrumbs.append({
            "name": self.model_class.__name__,
            "url": self.back_url,
        })
        breadcrumbs.append({
            "name": "create",
        })

        if id is not None:
            model = self.model_class.objects.get(pk=id)
        else:
            model = self.model_class()

        form = self.form_class(instance=model)

        if request.method == 'POST':
            form.load(data=request.POST, files=request.FILES)
            if form.is_valid():
                form.save()
                return redirect(self.redirect_url)

        context = self.extra_context.copy()

        context.update({
            "crumbs": breadcrumbs,
            "form": form,
            "model": model,
            "title": "list of %s" % self.model_class._meta.model_name
        })

        return render(request, 'advanced_admin/crud/change.html', context)


class DeleteAction(Action):
    def __init__(self, model_class, extra_context=None):
        self.model_class = model_class
        self.extra_context = extra_context or dict()

    def run(self, request, id=None):
        if id is None:
            return HttpResponseNotFound()

        try:
            model = self.model_class.objects.get(pk=id)
            model.delete()
        except self.model_class.DoesNotExist:
            return HttpResponseNotFound()

        return redirect('/' + index_url)


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


class AdvancedAdmin(object):
    def __init__(self, base_url='advanced_admin/'):
        self.base_url = base_url

        self.routes = [
            path('advanced_admin/', self.index)
        ]

        self.modules = list()

    def index(self, request):
        return render(request, 'advanced_admin/index.html', {
            'site': self,
            'crumbs': [{"name": "Advanced admin"}]
        })

    def register_crud(self, model_class: Type[Model], columns=None, form_class=None, filter_form=None):
        app_label = model_class._meta.app_label
        model_name = model_class._meta.model_name

        common_context = {
            "app_label": app_label,
            "model_name": model_name,
            "site": self,
        }

        url_prefix = 'advanced_admin/%s/%s' % (app_label, model_name)

        module = CrudModule(
            model_class=model_class,
            url_prefix=url_prefix,
            context=common_context,
            form_class=form_class,
            columns=columns,
            filter_form=filter_form
        )

        self.modules.append(module)
        self.routes += module.urls()

    def menu(self):
        for m in self.modules:
            yield m.menu()
