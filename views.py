from django.db.models import Model
from django.urls import path
from django.shortcuts import render, redirect
from typing import Type
from .modules import CrudModule
from forms import forms


class LoginModel(object):
    def __init__(self):
        self.email = None
        self.password = None


class LoginForm(forms.Form):
    email = forms.Field()
    password = forms.Field(attributes={"type": "password"})


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
        form = LoginForm(instance=instance)

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
