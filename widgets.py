from forms.html import HtmlHelper
from advanced_admin.templatetags.advanced_admin import getattr_dot
from django.utils.html import mark_safe


class Widget(object):
    def render(self):
        return "default widget"


class DataColumn(object):
    """ Класс представляет колонку в гриде """

    def __init__(self, *args, path=None, label=None, **kwargs):
        self.path = path
        self.label = label

        super(DataColumn, self).__init__(*args, **kwargs)

    def render_cell(self, item):
        return HtmlHelper.tag('td', str(getattr_dot(item, self.path)))

    def render_header(self):
        return self.label or self.path


class CallableColumn(object):
    def __init__(self, *args, cb=None, **kwargs):
        self.cb = cb

        super(CallableColumn, self).__init__(*args, **kwargs)

    def render_column(self, item):
        return str(self.cb(item))


class ButtonColumn(DataColumn):
    """
        Buttons property must be a list of lambda functions
        Each function receives one item (model)
    """

    def __init__(self, *args, buttons=None, **kwargs):
        super(ButtonColumn, self).__init__(*args, **kwargs)
        self.buttons = buttons or list()

    def render_cell(self, item):
        out = list()

        for func in self.buttons:
            l_result = func(item)
            out.append(str(l_result))

        return HtmlHelper.tag('td', ' '.join(out))


class Grid(Widget):
    def __init__(self, *args, columns=None, data=None, table_attributes=None, **kwargs):
        # defaults
        columns = columns or list('id')
        data = data or list()

        # create properties
        self.data = data
        self.columns = list()
        self.table_attributes = table_attributes or {
            "class": "table"
        }

        # init columns
        for a in columns:
            if isinstance(a, str):
                self.columns.append(DataColumn(path=a))

            elif callable(a):
                self.columns.append(CallableColumn(cb=a))

            elif isinstance(a, DataColumn):
                self.columns.append(a)

        super(Grid, self).__init__(*args, **kwargs)

    def create_header(self):
        out = []

        for column in self.columns:
            out.append(HtmlHelper.tag('th', column.render_header()))

        return HtmlHelper.tag('tr', ''.join(out))

    def create_body(self):
        out = []

        for item in self.data:
            cells = []
            for column in self.columns:
                cells.append(column.render_cell(item))

            out.append(HtmlHelper.tag('tr', ''.join(cells)))

        return ''.join(out)

    def render(self):
        header = self.create_header()
        body = self.create_body()
        return mark_safe(HtmlHelper.tag('table', header + body, self.table_attributes))
