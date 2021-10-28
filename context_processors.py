from advanced_admin.admin import admin_service


def context_processor(request):
    return {"admin": admin_service.admin}
