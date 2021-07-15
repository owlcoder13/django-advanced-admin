from .views import AdvancedAdmin
import os
from django.conf import settings


def get_settings_root():
    return os.environ.get('DJANGO_SETTINGS_MODULE').split('.')[0]


def import_dyn(mod_path):
    if isinstance(mod_path, str):
        mod_path = mod_path.split('.')

    return __import__('.'.join(mod_path[0:-1]), fromlist=mod_path)


class AdminService(object):
    def __init__(self):
        admin_class = AdvancedAdmin

        if hasattr(settings, 'ADVANCED_ADMIN_APP_CLASS'):
            mod_path = settings.ADVANCED_ADMIN_APP_CLASS.split('.')
            class_name = mod_path[-1]

            admin_class = getattr(import_dyn(mod_path), class_name)

        self.admin = admin_class()

    def set_admin(self, admin_app):
        self.admin = admin_app

    @property
    def routes(self):

        for app in settings.INSTALLED_APPS:
            print('search app', app)
            if app == 'advanced_admin':
                continue

            try:
                mod_path = [app, 'admin']
                m = import_dyn(mod_path)
            except ModuleNotFoundError as ex:
                pass

        return self.admin.routes


admin_service = AdminService()
