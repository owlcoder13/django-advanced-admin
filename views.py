from django.db.models import Model
from django.urls import path
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
            path(base_url + '/', self.index),
            path(base_url + '/login', self.login)
        ]

        self.modules = list()

    def login(self, request):
        instance = LoginModel()
        form = LoginForm(instance=instance, request=request)

        if request.method == 'POST':
            form.load(data=request.POST)
            if form.handle():
                return redirect('/advanced_admin')

        return render(request, 'advanced_admin/login.html', {"form": form})

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
