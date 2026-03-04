from django.http import HttpResponseForbidden

def is_secretaria(user):
    return user.is_superuser or user.groups.filter(name="Secretaria").exists()

def only_secretaria(view_func):
    def _wrapped(request, *args, **kwargs):
        if not is_secretaria(request.user):
            return HttpResponseForbidden("Acesso negado.")
        return view_func(request, *args, **kwargs)
    return _wrapped