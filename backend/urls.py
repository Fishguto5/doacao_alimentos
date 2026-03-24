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

import debug_toolbar
from django.contrib import admin
from django.urls import include, path
from core.views import *
from . import views
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('debug/', include('debug_toolbar.urls')),
    path('person/', view_person, name='person'),
    path('usuario/', view_usuario, name='usuario'),
    path('categoria/', view_categoria, name='categoria'),
    path('doacao/', view_doacao, name='doacao'),
    path('solicitacao-doacao/', view_solicitacao_doacao, name='solicitacao_doacao'),
    path('alimento/', view_alimento, name='alimento'),
    path('notificacao/', view_notificacao, name='notificacao'),
    path('avaliacao/', view_avaliacao, name='avaliacao'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # url para usar o swagger, que é uma interface gráfica para explorar a API
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('', views.test),      
]
