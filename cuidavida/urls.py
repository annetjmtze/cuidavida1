"""
URL configuration for cuidavida project.

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
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('formulario/', views.wizard, name='wizard'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    #AGREGAR EL CAMPO PARA BUSCAR, REDIRECCIONAMIENTO
    path('buscar-cp/', views.buscar_cp, name='buscar_cp'),
    path('enviar-receta/<int:paciente_id>/', views.enviar_receta, name='enviar_receta'),
    path('perfil-medico/', views.perfil_medico_view, name='perfil_medico'),
    path('programar-cita/', views.programar_cita, name='programar_cita'),
    path('valorar-medico/<int:cita_id>/', views.valorar_medico, name='valorar_medico'),
    path('crear-alerta/', views.crear_alerta, name='crear_alerta'),
    path('resolve-vital-alert/<int:alert_id>/', views.resolver_alerta, name='resolver_alerta'),
    # Nueva URL para descargar el PDF de la receta
    path('receta-pdf/<int:receta_id>/', views.download_receta_pdf, name='download_receta_pdf'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)