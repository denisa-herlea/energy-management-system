from django.contrib.auth.decorators import user_passes_test


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


def is_client(user):
    return user.is_authenticated and user.role == 'client'


admin_required = user_passes_test(is_admin)
client_required = user_passes_test(is_client)
