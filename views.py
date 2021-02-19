from django.db.models import Model
from django.urls import path, include
from django.shortcuts import render, redirect
from typing import Type
from .modules import CrudModule
from forms import forms
from django.contrib.auth import authenticate, login as make_login
from main.models import User


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

        return False

    def is_valid(self):
        valid = super().is_valid()

        self.user = authenticate(self.request, username=self.login.value,
                                 password=self.password.value)
        if self.user is None:
            self.add_error('login', 'No user found')

        return len(self.errors.items()) == 0


class AdvancedAdmin(object):
    def __init__(self, base_url='advanced_admin'):
        self.base_url = base_url

        self.routes = [
            path(base_url + '', self.index),
            path(base_url + 'login', self.login)
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
                      filter_form=None,
                      module_class=None):

        common_context = self.context.copy()

        common_context.update({
            "site": self,
            "base_url": self.base_url
        })

        if module_class is None:
            module_class = CrudModule

        app_label = model_class._meta.app_label
        model_name = model_class._meta.model_name

        url_prefix = '%s' % (
            model_name
        )

        module_class = module_class

        module = module_class(
            model_class=model_class,
            url_prefix=url_prefix,
            context=common_context,
            form_class=form_class,
            columns=columns,
            filter_form=filter_form,
            base_url=self.base_url,
            route_name='fuck',

        )

        self.add_module(module,
                        route_name=model_name,
                        url_prefix=model_name
                        )

    def add_module(self, module, route_name=None, url_prefix=None):

        common_context = self.context.copy()
        common_context.update({
            "site": self,
            "base_url": self.base_url
        })

        module.context.update(common_context)

        route_name = route_name or module.__class__.__name__

        module.route_name = 'admin.' + route_name
        module.url_prefix = url_prefix or module.__class__.__name__

        self.modules.append(module)

        # add routes
        urls = module.urls()
        route = path(self.base_url, include(urls))

        self.routes.append(route)

    def menu(self):
        for m in self.modules:
            menus = m.menu()
            yield menus
