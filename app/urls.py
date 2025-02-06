# app/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path("", views.login_view, name = 'login'),
    path('login/',views.login_view, name = 'login'),
    path('home/', views.home, name='home'),
    path('crear_usuario/', views.crear_usuario, name='crear_usuario'),
    path('reporte_vacantes/', views.reporte_vacantes, name='reporte_vacantes'),
    path('control_usuarios/', views.control_usuarios, name='control_usuarios'),
    path('generar_backup/', views.generar_backup, name='generar_backup'),
    path('registrar_directores/', views.registrar_directores, name='registrar_directores'),
    path('registro_vacantes/', views.registro_vacantes, name='registro_vacantes'),
    path('registro_vacantes_nee/', views.registro_vacantes_nee, name='registro_vacantes_nee'),
    path('logout/', views.custom_logout, name='logout'),
    path('registrar_colegios/', views.registrar_colegios, name = 'registrar_colegios'),
    path('editar_usuario/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar_usuario/<int:id>/', views.eliminar_usuario, name='eliminar_usuario')
]
