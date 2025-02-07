# app/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('login/',views.login_view, name = 'login'),
    path('home/', views.home, name='home'),
    path('crear_usuario/', views.crear_usuario, name='crear_usuario'),
    path('reporte_vacantes/', views.reporte_vacantes, name='reporte_vacantes'),
    path('control_usuarios/', views.control_usuarios, name='control_usuarios'),
    path('generar_backup/', views.generar_backup, name='generar_backup'),
    path('registrar_vacantes/', views.registrar_vacantes, name='registrar_vacantes'),
    path('registro_vacantes_nee/', views.registro_vacantes_nee, name='registro_vacantes_nee'),
    path('logout/', views.custom_logout, name='logout'),
    path('registrar_colegios/', views.registrar_colegios, name = 'registrar_colegios'),
    path('editar_usuario/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar_usuario/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('registrar_director/', views.registrar_director, name='registrar_director'),
    path('', views.index, name='index'),  # Página principal
    path('ugel/<int:ugel_id>/colegios/', views.colegios_por_ugel, name='colegios_por_ugel'),
    path('registrar_colegios/agregar/', views.agregar_colegio, name='agregar_colegio'),
    path('registrar_colegios/editar/<int:id>/', views.editar_colegio, name='editar_colegio'),
    path('registrar_colegios/eliminar/<int:id>/', views.eliminar_colegio, name='eliminar_colegio'),
    path("cargar-datos-colegios/", views.cargar_datos_colegios, name="cargar_datos_colegios"),
]

