from django.db.models import Model
from django.urls import path, include
from django.shortcuts import render, redirect
from typing import Type
from .modules import CrudModule
from forms import forms
from django.contrib.auth import authenticate, login as make_login


class LoginModel(object):
    def __init__(self):
        self.login = None
        self.password = None


class LoginForm(forms.Form):
    login = forms.Field()
    password = forms.Field(attributes={"type": "password"})

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = None
        self.request = request

    def handle(self):
        if self.is_valid():
            make_login(user=self.user, request=self.request)
            return True

        return False

    def is_valid(self):
        valid = super().is_valid()
        data = self.values

        self.user = authenticate(self.request, username=data.get('login'),
                                 password=data.get('password'))
        if self.user is None:
            self.add_field_error('login', 'No user found')

        return len(self.errors.items()) == 0


class AdvancedAdmin(object):
    def __init__(self, base_url='advanced_admin'):
        self.base_url = base_url

        self.routes = [
            path(base_url + '', self.index),
            path('login/', self.login)
        ]

        self.context = {
            "base_url": self.base_url,
        }

        self.modules = list()

    def login(self, request):
        instance = LoginModel()
        form = LoginForm(instance=instance, request=request)

        if request.method == 'POST':
            form.load(data=request.POST)
            if form.handle():
                return redirect('/' + self.base_url)

        return render(request, 'advanced_admin/login.html', {"form": form})

    def index(self, request):
        context = self.context.copy()

        context.update({
            'site': self,
            'crumbs': [{"name": "Advanced admin"}]
        })

        return render(request, 'advanced_admin/index.html', context)

    def register_crud(self,
                      model_class: Type[Model],
                      columns=None,
                      form_class=None,
                      name=None,
                      filter_form=None,
                      module_class=None, change_route_prefix=None, change_url_prefix=None):

        common_context = self.context.copy()

        common_context.update({
            "site": self,
            "url_prefix": self.base_url
        })

        if module_class is None:
            module_class = CrudModule

        app_label = model_class._meta.app_label
        model_name = model_class._meta.model_name

        module_class = module_class
        base_url = model_name

        module = module_class(
            model_class=model_class,
            context=common_context,
            form_class=form_class,
            name=name,
            columns=columns,
            filter_form=filter_form,
        )

        self.add_module(
            module,
            route_prefix=change_route_prefix or '%s.' % model_name,
            url_prefix=change_url_prefix or base_url
        )

    def add_module(self, module,
                   route_prefix=None,
                   url_prefix=None,
                   ):

        if url_prefix is None:
            url_prefix = type(module).__name__.lower()

        if route_prefix is None:
            route_prefix = type(module).__name__.lower()

        common_context = self.context.copy()
        common_context.update({
            "site": self,
            "base_url": self.base_url + module.url_prefix
        })

        module.context.update(common_context)

        route_prefix = route_prefix or module.__class__.__name__

        url_prefix = 'admin/' + url_prefix
        module.route_prefix = 'admin.' + route_prefix
        module.url_prefix = url_prefix or module.__class__.__name__

        self.modules.append(module)

        # add routes
        urls = module.urls()
        route = path('', include(urls))

        self.routes.append(route)

    def register_module(self, module_class, route_prefix=None,
                        url_prefix=None, module_params=None):
        if module_params is None:
            module_params = dict()

        module = module_class(**module_params)
        module.url_prefix = 'admin/' + url_prefix
        module.route_prefix = 'admin.' + route_prefix

        # append module
        self.modules.append(module)

        # add routes
        urls = module.urls()
        route = path('', include(urls))
        self.routes.append(route)

    def menu(self):
        for m in self.modules:
            menus = m.menu()
            yield menus
