"""
URL configuration for sica_config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from chamados.views import meus_chamados
from django.contrib.auth import views as auth_views
from chamados.views import meus_chamados, chamados_secretaria
from chamados.views import abrir_chamado
from chamados.views import detalhe_chamado
from chamados.views import minha_area


urlpatterns = [
    path('admin/', admin.site.urls),
    path("meus-chamados/", meus_chamados, name="meus_chamados"),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("secretaria/chamados/", chamados_secretaria, name="chamados_secretaria"),
    path("abrir-chamado/", abrir_chamado, name="abrir_chamado"),
    path("chamado/<int:id>/", detalhe_chamado, name="detalhe_chamado"),
    path("minha-area/", minha_area, name="minha_area"),
]
