from django.db.models import Model
from django.urls import reverse
from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect


class Action(object):
    def run(self, request):
        pass

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)


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
