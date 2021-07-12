from .views import AdvancedAdmin
from django.conf import settings
import os


def get_settings_root():
    return os.environ.get('DJANGO_SETTINGS_MODULE').split('.')[0]


class AdminService(object):
    def __init__(self):
        self.admin = AdvancedAdmin()

    def set_admin(self, admin_app):
        self.admin = admin_app

    @property
    def routes(self):

        for app in [get_settings_root() + '.admin'] + settings.INSTALLED_APPS:
            try:
                mod_path = [app, 'admin']
                m = __import__('.'.join(mod_path[0:-1]), fromlist=mod_path)
            except ModuleNotFoundError as ex:
                pass

        return self.admin.routes


admin_service = AdminService()
