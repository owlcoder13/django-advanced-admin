from django.http.response import HttpResponseForbidden
from django.shortcuts import redirect
from .helpers import get_settings_value


class Middleware(object):

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        response = self.get_response(request)

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path
        white_list_urls = ['/admin/login']

        if path in white_list_urls:
            return None

        if request.path.startswith('/admin') and \
                (request.user.is_anonymous or not request.user.is_admin()):
            if request.user.is_authenticated:
                return HttpResponseForbidden()
            else:
                return redirect(get_settings_value('ADVANCED_ADMIN_LOGIN_URL', '/admin/login'))

        return None
