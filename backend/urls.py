"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.views import (
    view_alimento,
    view_alimento_detail,
    view_auth_login,
    view_auth_register,
    view_avaliacao,
    view_avaliacao_detail,
    view_categoria,
    view_categoria_detail,
    view_doacao,
    view_doacao_cidades,
    view_doacao_detail,
    view_notificacao,
    view_notificacao_detail,
    view_solicitacao_doacao,
    view_solicitacao_doacao_detail,
    view_usuario,
    view_usuario_detail,
)

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("debug/", include("debug_toolbar.urls")),
    path("auth/register/", view_auth_register, name="auth_register"),
    path("auth/login/", view_auth_login, name="auth_login"),
    path("usuario/", view_usuario, name="usuario"),
    path("usuario/<int:id>/", view_usuario_detail, name="usuario_detail"),
    path("categoria/", view_categoria, name="categoria"),
    path("categoria/<int:id>/", view_categoria_detail, name="categoria_detail"),
    path("doacao/", view_doacao, name="doacao"),
    path("doacao/cidades/", view_doacao_cidades, name="doacao_cidades"),
    path("doacao/<int:id>/", view_doacao_detail, name="doacao_detail"),
    path("solicitacao-doacao/", view_solicitacao_doacao, name="solicitacao_doacao"),
    path(
        "solicitacao-doacao/<int:id>/",
        view_solicitacao_doacao_detail,
        name="solicitacao_doacao_detail",
    ),
    path("alimento/", view_alimento, name="alimento"),
    path("alimento/<int:id>/", view_alimento_detail, name="alimento_detail"),
    path("notificacao/", view_notificacao, name="notificacao"),
    path("notificacao/<int:id>/", view_notificacao_detail, name="notificacao_detail"),
    path("avaliacao/", view_avaliacao, name="avaliacao"),
    path("avaliacao/<int:id>/", view_avaliacao_detail, name="avaliacao_detail"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # url para usar o swagger, que é uma interface gráfica para explorar a API
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("", views.test),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
