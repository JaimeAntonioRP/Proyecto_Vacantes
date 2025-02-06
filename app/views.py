from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Usuario
from .forms import UsuarioForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib.auth.hashers import make_password
import csv
import datetime

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Usa .get() para evitar el error si no se envía 'email'
        password = request.POST.get('password')  # Usa .get() para evitar el error si no se envía 'password'

        # Verifica si se han proporcionado ambos campos
        if not email or not password:
            messages.error(request, "Correo y contraseña son obligatorios.")
            return redirect('login')

        # Autentica al usuario usando el email y la contraseña
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect('login')

        # Verifica que el usuario esté activo
        if usuario.estado != 'ACTIVO':
            messages.error(request, "Su cuenta está inactiva.")
            return redirect('login')

        # Autenticación usando el método authenticate de Django
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirige a la página de inicio si el login es exitoso
        else:
            messages.error(request, "Contraseña incorrecta.")
            return redirect('login')

    return render(request, 'app/login.html')
def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    # Puedes agregar lógica aquí si es necesario, como obtener datos del usuario o mostrar diferentes paneles según el tipo de usuario.
    nombre_usuario = request.user.nombre  # Asegúrate de que el modelo de usuario tenga este campo.
    tipo_usuario = request.user.tipo_usuario  # Asegúrate de que el modelo de usuario tenga este campo.

    return render(request, 'app/home.html', {'nombre_usuario': nombre_usuario, 'tipo_usuario': tipo_usuario})

@login_required
def home_view(request):
    # Obtén el usuario autenticado
    usuario = request.user
    # Verifica si `tipo_usuario` está presente y tiene valor
    tipo_usuario = usuario.tipo_usuario if usuario.tipo_usuario else "NO DEFINIDO"
    # Pasa el tipo de usuario al contexto
    contexto = {
        'nombre_usuario': usuario.nombre,
        'tipo_usuario': usuario.tipo_usuario,
        'permisos': usuario.permisos,
    }
    return render(request, 'app/home.html', contexto)

@login_required
def panel_usuario_regional(request):
    # Aquí puedes agregar lógica específica para el usuario regional si es necesario
    return render(request, 'app/panel_usuario_regional.html')

@login_required
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UsuarioForm()
    return render(request, 'app/crear_usuario.html', {'form': form})

@login_required
def reporte_vacantes(request):
    # Lógica para generar el reporte
    # Por ejemplo, generar un archivo PDF o CSV
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_vacantes.pdf"'
    # Agrega el contenido del PDF aquí
    return response


@login_required
def generar_backup(request):
    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        # Lógica para generar el backup basado en::contentReference[oaicite:0]{index=0}
@login_required
def home(request):
    # Asegúrate de pasar nombre_usuario y tipo_usuario en el contexto
    nombre_usuario = request.user.nombre
    tipo_usuario = request.user.tipo_usuario
    return render(request, 'app/home.html', {'nombre_usuario': nombre_usuario, 'tipo_usuario': tipo_usuario})

@login_required
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UsuarioForm()
    return render(request, 'app/crear_usuario.html', {'form': form})


@login_required
def reporte_vacantes(request):
    # Lógica para generar el reporte
    return render(request, 'app/reporte_vacantes.html')

@login_required
def control_usuarios_ugel(request):
    usuarios_ugel = Usuario.objects.filter(tipo_usuario='UGEL')
    return render(request, 'app/control_usuarios_ugel.html', {'usuarios': usuarios_ugel})

@login_required
def generar_backup(request):
    return render(request, 'app/generar_backup.html')

@login_required
def registrar_colegios(request):
    return render(request, 'app/registrar_colegios.html')

@login_required
def registrar_directores(request):
    return render(request, 'app/registrar_directores.html')

@login_required
def registro_vacantes(request):
    return render(request, 'app/registro_vacantes.html')

@login_required
def registro_vacantes_nee(request):
    return render(request, 'app/registro_vacantes_nee.html')

@login_required
def control_usuarios(request):
    # Excluir al usuario actual
    usuarios = Usuario.objects.exclude(id=request.user.id)
    
    # Filtrar según el tipo de usuario
    if request.user.tipo_usuario == "REGIONAL":
        # Solo mostrar usuarios de tipo "REGIONAL" o "UGEL"
        usuarios = usuarios.filter(tipo_usuario__in=["REGIONAL", "UGEL"])
    
    elif request.user.tipo_usuario == "UGEL":
        # Solo mostrar usuarios "DIRECTOR" de la misma UGEL
        usuarios = usuarios.filter(tipo_usuario="DIRECTOR", ugel=request.user.ugel)
    
    else:
        # Si no es un usuario regional ni UGEL, no devolver usuarios
        usuarios = []

    # Filtrar por la búsqueda de nombre o DNI
    query = request.GET.get('query', '')  # Búsqueda por nombre o DNI
    tipo_usuario = request.GET.get('tipo_usuario', '')  # Filtrar por tipo de usuario
    
    if query:
        usuarios = usuarios.filter(nombre__icontains=query) | usuarios.filter(dni__icontains=query)  # Buscar por nombre o DNI
    
    if tipo_usuario:
        usuarios = usuarios.filter(tipo_usuario=tipo_usuario)  # Filtrar por tipo de usuario
    
    return render(request, 'app/control_usuarios.html', {
        'usuarios': usuarios,
        'user': request.user,
    })
@login_required
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)  # Fetch the user by ID
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)  # Use a form to handle the post data
        if form.is_valid():
            form.save()
            return redirect('control_usuarios')  # Redirect after saving changes
    else:
        form = UsuarioForm(instance=usuario)  # Display the current user data in the form

    return render(request, 'app/editar_usuario.html', {'form': form, 'usuario': usuario})
@login_required
def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado con éxito.')
        return redirect('control_usuarios')  # Cambia a tu nombre de vista para listar usuarios

    return render(request, 'control_usuarios.html')
@login_required
def generar_backup(request):
    # Crear la respuesta para descargar el archivo
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="backup_usuarios.csv"'
    
    # Crear el objeto writer de csv
    writer = csv.writer(response)
    
    # Escribir las cabeceras del CSV
    writer.writerow(['DNI', 'Nombre', 'Apellido Paterno', 'Apellido Materno', 'Email', 'Teléfono', 'Tipo Usuario', 'Estado', 'UGEL', 'Código Modular'])
    
    # Escribir los datos de los usuarios
    usuarios = Usuario.objects.all()  # O filtrados según lo necesites
    for usuario in usuarios:
        writer.writerow([usuario.dni, usuario.nombre, usuario.apellido_paterno, usuario.apellido_materno, usuario.email, usuario.telefono, usuario.tipo_usuario, usuario.estado, usuario.ugel, usuario.codigo_modular])
    
    return response