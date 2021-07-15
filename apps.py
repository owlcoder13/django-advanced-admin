from django.apps import AppConfig
from django.conf import settings
import os


class DjangoAdvancedAdminConfig(AppConfig):
    name = 'advanced_admin'

    def ready(self):
        super(DjangoAdvancedAdminConfig, self).ready()
        static_path = os.path.join(settings.BASE_DIR, 'advanced_admin/static')
        settings.STATICFILES_DIR.append(static_path)
