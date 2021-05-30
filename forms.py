from forms import forms


class FormRenderer(forms.BootstrapFormRenderer):
    """
    Adopt to bootstrap-5
    """
    form_group_class = "mb-3"
    form_error_class = 'form-error'


class BaseForm(forms.Form):
    """
    Base class to all admin forms
    """

    def __init__(self, *args, renderer_class=None, **kwargs):
        super().__init__(*args, renderer_class=FormRenderer, **kwargs)
