from .actions import ListAction, DeleteAction, ChangeAction
from django.urls import path, reverse
from django.http.response import HttpResponse
from advanced_admin.widgets import ButtonColumn
from forms.html import HtmlHelper
from django.core.paginator import Paginator
from django.db.models import Model
from advanced_admin.widgets import Grid
from django.shortcuts import render, redirect
from advanced_admin.icons import Icon


class AdminMenuItem(object):
    def __init__(self, name=None, url=None):
        self.name = name
        self.url = url


class Module(object):
    def __init__(self, *args, url_prefix=None, root_url='admin/', context=None, route_prefix=None, **kwargs):
        self.url_prefix = url_prefix or ''
        self.context = context or dict()
        self.route_prefix = route_prefix or type(self).__name__
        self.root_url = root_url

    def menu(self):
        return list()

    def actions(self):
        return dict()

    def urls(self):
        urls = list()

        acts = self.actions()

        if not isinstance(acts, dict):
            raise Exception("Value return from module.actions() must be dict: %s" % self)

        for _, action_data in acts.items():
            if not isinstance(action_data, dict):
                raise Exception('action_data from method actions must be a dict in module ' + type(self).__name__)

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

                # Add dots between route parts
                if name_suffix is not None and name_suffix != '':
                    name_suffix = '.%s' % name_suffix

                url_path.name = self.route_prefix + name_suffix

            urls.append(url_path)

        return urls


class CrudButtonColumn(ButtonColumn):
    def __init__(self, *args,
                 update_url=None,
                 delete_url=None,
                 **kwargs):
        super(CrudButtonColumn, self).__init__()
        self.buttons += [
            lambda item: HtmlHelper.tag('a',
                                        Icon.update,
                                        {
                                            "href": update_url(item),

                                        }
                                        ),
            lambda item: HtmlHelper.tag('a',
                                        Icon.delete,
                                        {
                                            "onclick": "return confirm('Are you sure?')",
                                            "href": delete_url(item),

                                        }
                                        )
        ]


class CrudModule(Module):
    model_class = None
    name = None

    def __init__(
            self,
            *args,
            model_class=None,
            columns=None, name=None,
            url_name_prefix=None, context=None,
            form_class=None, filter_form=None, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.model_class = model_class or self.model_class
        self.name = name or self.name or self.model_class._meta.model_name
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
            AdminMenuItem(name=self.name, url=reverse(self.route_prefix + '.index'))
        ]

    def modify_actions(self, actions):
        return actions

    def get_columns(self):
        cols = self.columns.copy()

        update_url = lambda item: reverse('admin.%s.change' % self.model_class.__name__.lower(), args=[item.id])
        delete_url = lambda item: reverse('admin.%s.delete' % self.model_class.__name__.lower(), args=[item.id])
        button_column = CrudButtonColumn(update_url=update_url, delete_url=delete_url)

        cols.append(button_column)

        return cols

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

        # print('route prefix', self.route_prefix)
        # list_context['create_url'] = '/' + self.url_prefix + '/create'

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

        self.get_columns()

        url_prefix = self.url_prefix

        class _ListAction(ListAction):
            def create_context(self, request, context_from_run):
                context = super(_ListAction, self).create_context(request, context_from_run)
                context.update({'create_url': '/' + url_prefix + '/create'})
                return context

        actions = {
            'index': {
                "action": _ListAction(
                    model_class=self.model_class,
                    columns=self.get_columns(),
                    extra_context=list_context,
                    filter_form=self.filter_form,
                ),
                "url": '',
                "route": 'index',
            },
            'create': {
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
            'update': {
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
            'delete': {
                "action": DeleteAction(
                    model_class=self.model_class,
                    extra_context=self.context,
                    redirect_url='/' + self.url_prefix,
                ),
                "url": 'delete/<int:id>',
                "route": 'delete',
            }
        }

        return self.modify_actions(actions)


class PageModule(Module):
    def __init__(self, *args, label=None, action=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.label = label

    def action(self, request):
        return HttpResponse('action')

    def menu(self, *args, **kwargs):
        return [
            AdminMenuItem(name=self.label, url=reverse(self.route_prefix))
        ]

    def actions(self):
        return {
            "index": {
                "action": self.action,
                "url": "",
                'route': "",
            }
        }


class Crud2Module(Module):
    index_template = 'advanced_admin/crud/list.html'
    change_template = 'advanced_admin/crud/change.html'

    def __init__(self, *args, name=None, model_class=None,
                 form_class=None, page_size=10, columns=None,
                 filter_form_class=None, redirect_url=None, order_by=None,
                 extra_context=None,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.model_class = model_class  # type: type  # The main model class
        self.form_class = form_class  # form class for change action
        self.name = name or self.model_class._meta.model_name  # Name of the module
        self.page_size = page_size  # How much elements show listing page
        self.columns = columns or ['id']  # which columns showing grid
        self.model = None  # internal variable for storing model or list of models
        self.grid = None  # grid widget
        self.request = None  # store current request
        self.filter_form = None  # current index filter
        self.filter_form_class = filter_form_class  # index filter form class
        self.is_filtered = False  # has filter property?
        self.args = list()  # store current arguments
        self.kwargs = dict()  # store current kw arguments
        self.is_new = False  # is new record for change action
        self.redirect_url = redirect_url  # redirect after form save
        self.form = None  # form instance
        self.is_delete = False  # is delete action
        self.paginator = None
        self.page_obj = None
        self.order_by = order_by
        self.extra_context = extra_context or dict()

    def index_create_context(self):
        self.context = self.extra_context.copy()

        self.context = {
            "model": self.model,
            "grid": self.grid,
            'paginator': self.paginator,
            'page_obj': self.page_obj,
            "title": "list of %s" % self.model_class._meta.model_name,
            'create_url': reverse('%s.create' % self.route_prefix)
        }

    def get_columns(self):
        columns = self.columns.copy()
        print('route prefix', self.route_prefix)

        update_url = lambda item: reverse('%s.change' % self.route_prefix, args=[item.id])
        delete_url = lambda item: reverse('%s.delete' % self.route_prefix, args=[item.id])
        button_column = CrudButtonColumn(update_url=update_url, delete_url=delete_url)
        columns.append(button_column)
        return columns

    def index_fetch_model(self):
        self.model = self.index_get_model(self.request)
        self.paginator = Paginator(self.model, self.page_size)
        self.page_obj = self.paginator.get_page(self.request.GET.get('page'))

        self.grid = Grid(columns=self.get_columns(), data=list(self.page_obj))

    def action_index(self, request):
        self.request = request

        self.prepare_filter()
        self.index_fetch_model()
        self.index_create_context()

        return render(request, self.index_template, self.context)

    def prepare_filter(self):
        if self.filter_form_class:
            self.filter_form = self.filter_form_class()
            self.filter_form.load(self.request.GET)

    def menu(self, *args, **kwargs):
        return [
            AdminMenuItem(name=self.name, url=reverse(self.route_prefix))
        ]

    def get_queryset(self, request):
        """
            You may reorder this method to filter queryset
        """

        qs = self.model_class.objects

        if self.order_by:
            qs.order_by(*self.order_by)

        return qs

    def index_get_model(self, request):
        model = self.get_queryset(request).all()
        return model

    def change_get_model(self):
        id = self.kwargs.get('id', None)

        if id is None:
            self.is_new = True
            model_class = self.model_class
            new_model = model_class()
            self.model = new_model
        else:
            self.model = self.model_class.objects.get(pk=id)

        return self.model

    def get_form(self):
        form_class = self.form_class
        return form_class(instance=self.model)

    def redirect(self, model):
        return redirect(self.redirect_url or reverse(self.route_prefix))

    def after_save(self, form):
        pass

    def before_save(self, form):
        pass

    def handle_form(self, form):
        if self.request.method == 'POST':
            form.load(data=self.request.POST, files=self.request.FILES)
            if form.is_valid():
                self.before_save(form)
                form.save()
                self.after_save(form)

                return self.redirect(self.model)
        return None

    def action_change(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

        model = self.change_get_model()
        self.form = self.get_form()

        response = self.handle_form(self.form)
        if response is not None:
            return response

        context = self.get_change_context()

        return render(request, self.change_template, context)

    def get_change_context(self):
        ctx = self.extra_context.copy()

        ctx.update({
            "model": self.model,
            "form": self.form,
            "is_new": self.is_new,
        })

        return ctx

    def action_delete(self, request, *args, **kwargs):
        self.is_delete = True
        self.change_get_model()
        self.model.delete()
        return self.redirect(self.model)

    def actions(self):
        return {
            'index': {
                "action": self.action_index,
                "url": "",
                'route': "",
            },
            'update': {
                "action": self.action_change,
                "url": "<int:id>/change",
                'route': "change",
            },
            'create': {
                "action": self.action_change,
                "url": "create",
                'route': "create",
            },
            'delete': {
                "action": self.action_delete,
                "url": "<int:id>/delete",
                'route': "delete",
            }
        }
