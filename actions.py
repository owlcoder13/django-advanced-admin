from django.db.models import Model
from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect
from advanced_admin.widgets import Grid
from .helpers import ReplaceMethodMixin
from django.contrib.messages import add_message, constants as message_constants


class Action(ReplaceMethodMixin, object):
    def __init__(self, *args, **kwargs):
        self.request = None

    def run(self, request, *args, **kwargs):
        self.request = request

    def __call__(self, request, *args, **kwargs):
        request.route_args = args
        request.route_kwargs = kwargs
        return self.run(request, *args, **kwargs)


class ListAction(Action):
    # defined view template
    template = 'advanced_admin/crud/list.html'

    def __init__(self, model_class, columns, extra_context=None, filter_form=None, *args, **kwargs):
        super(ListAction, self).__init__(*args, **kwargs)
        self.model_class = model_class  # type: Model
        self.columns = columns
        self.extra_context = extra_context or dict()
        self.filter_form = filter_form
        self.grid = None

    def get_queryset(self):
        """
        You may reorder this method to filter queryset
        """
        return self.model_class.objects

    def get_model(self):
        if self.filter_form is not None:
            filter = self.filter_form()
            filter.load(request.GET)
            m = filter.get_model()
        else:
            filter = None
            m = self.get_queryset().all()
        return m

    def create_context(self, request, context_from_run):
        context = dict()
        context.update(self.extra_context)
        context.update({
            "grid": self.grid,
            "filter": filter,
            "title": "list of %s" % self.model_class._meta.model_name,
            "columns": self.columns,
        })
        context.update(context_from_run)

        return context

    def run(self, request, *args, **kwargs):
        super().run(request, *args, **kwargs)

        m = self.get_model()
        self.grid = Grid(columns=self.columns, data=m)
        context = self.create_context(request, {"model": m})

        return render(request, self.template, context)


class ChangeAction(Action):
    template = 'advanced_admin/crud/change.html'

    def __init__(self, model_class, extra_context=None, form_class=None, redirect_url=None, back_url=None, *args,
                 **kwargs):
        super(ChangeAction, self).__init__(*args, **kwargs)
        self.model_class = model_class  # type: Type[Model]
        self.extra_context = extra_context or dict()
        self.redirect_url = redirect_url or '/admin'
        self.back_url = back_url
        self.form_class = form_class

    def get_redirect_url(self, model):
        return self.redirect_url

    def get_form(self, request, model):
        return self.form_class(instance=model)

    def get_model(self, request, *args, **kwargs):
        if 'id' in kwargs:
            model = self.model_class.objects.get(pk=kwargs['id'])
        else:
            model = self.model_class()

        return model

    def run(self, request, *args, **kwargs):
        model = self.get_model(request, *args, **kwargs)

        form = self.get_form(request, model)

        if request.method == 'POST':
            form.load(data=request.POST, files=request.FILES)
            if form.is_valid():
                form.save()
                add_message(request, message_constants.SUCCESS, 'Сохранено')
                return redirect(self.get_redirect_url(model))

        context = self.extra_context.copy()

        context.update({
            "form": form,
            "model": model,
            "title": "list of %s" % self.model_class._meta.model_name
        })

        return render(request, self.template, context)


class DeleteAction(Action):
    def __init__(self, model_class, redirect_url=None, extra_context=None, *args, **kwargs):
        super(DeleteAction, self).__init__(*args, **kwargs)
        self.model_class = model_class
        self.extra_context = extra_context or dict()
        self.redirect_url = redirect_url

    def get_redirect_url(self, model):
        return self.redirect_url

    def run(self, request, id=None, *args, **kwargs):
        if id is None:
            return HttpResponseNotFound()

        try:
            model = self.model_class.objects.get(pk=id)
            redirect_url = self.get_redirect_url(model)
            model.delete()
            return redirect(redirect_url)

        except self.model_class.DoesNotExist:
            pass

        return HttpResponseNotFound()
