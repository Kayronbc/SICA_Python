"""
URL configuration for sica_config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

from chamados.views import (
    abrir_chamado,
    chamados_secretaria,
    detalhe_chamado,
    meus_chamados,
    minha_area,
)

urlpatterns = [
    path("", RedirectView.as_view(url="/minha-area/", permanent=False)),
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("minha-area/", minha_area, name="minha_area"),
    path("meus-chamados/", meus_chamados, name="meus_chamados"),
    path("abrir-chamado/", abrir_chamado, name="abrir_chamado"),
    path("chamado/<int:id>/", detalhe_chamado, name="detalhe_chamado"),
    path("secretaria/chamados/", chamados_secretaria, name="chamados_secretaria"),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)