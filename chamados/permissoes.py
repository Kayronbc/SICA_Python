from functools import wraps

from django.http import HttpResponseForbidden


def is_admin(user):
    return user.is_authenticated and user.is_superuser


def is_secretaria(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name="Secretaria").exists()
    )


def is_secretaria_pura(user):
    return user.is_authenticated and user.groups.filter(name="Secretaria").exists() and not user.is_superuser


def only_secretaria(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not is_secretaria(request.user):
            return HttpResponseForbidden("Acesso negado.")
        return view_func(request, *args, **kwargs)

    return _wrapped


def only_aluno_area(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if is_secretaria_pura(request.user):
            return HttpResponseForbidden("Acesso negado.")
        return view_func(request, *args, **kwargs)

    return _wrapped