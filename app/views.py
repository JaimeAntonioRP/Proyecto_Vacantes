from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Usuario, Ugel, InstitucionEducativa, VacanteFinal, Nivel
from .forms import UsuarioForm, DirectorForm, InstitucionEducativaForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
import string
import random

import io
import json
import csv
import datetime
import zipfile
from django.core.paginator import Paginator
from django.shortcuts import render
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
def index(request):
    ugeles = Ugel.objects.all()  # Recuperar todas las UGELs de la base de datos
    Colegios = InstitucionEducativa.objects.all()  # Recuperar todas las instituciones educativas
    return render(request, 'app/index.html', {'ugeles': ugeles, 'colegios': Colegios})

def colegios_por_ugel(request, ugel_id):
    ugel = get_object_or_404(Ugel, id=ugel_id)
    colegios = InstitucionEducativa.objects.filter(ugel=ugel)
    modalidades = InstitucionEducativa.NIVEL_MODALIDAD_CHOICES
    return render(request, 'app/colegios_por_ugel.html', {'ugel': ugel, 'colegios': colegios, 'modalidades': modalidades})





@login_required
def home_view(request):
    # Obtén el usuario autenticado
    colegio = None
    usuario = request.user
    # Verifica si `tipo_usuario` está presente y tiene valor
    tipo_usuario = usuario.tipo_usuario if usuario.tipo_usuario else "NO DEFINIDO"
    colegio = InstitucionEducativa.objects.filter(cod_mod=request.user.codigo_modular).first()
    # Pasa el tipo de usuario al contexto
    contexto = {
        'nombre_usuario': usuario.nombre,
        'tipo_usuario': usuario.tipo_usuario,
        'permisos': usuario.permisos,
        'colegio': colegio,
    }


    return render(request, 'app/home.html', contexto)

@login_required
def panel_usuario_regional(request):
    # Aquí puedes agregar lógica específica para el usuario regional si es necesario
    return render(request, 'app/panel_usuario_regional.html')

@login_required
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)
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
    ap_usuario = request.user.apellido_paterno
    usuario = request.user
    colegio = InstitucionEducativa.objects.filter(cod_mod=request.user.codigo_modular).first()
    return render(request, 'app/home.html', {'nombre_usuario': nombre_usuario, 'tipo_usuario': tipo_usuario,
    'ap_usuario': ap_usuario,
    'usuario': usuario,
    'colegio': colegio                                        
    })

@login_required
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            messages.error
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
    # Obtener el tipo de usuario desde la sesión o modelo
    tipo_usuario = request.user.tipo_usuario  # Ejemplo: "REGIONAL" o "UGEL"
    ugel_usuario = request.user.ugel  # Suponiendo que el usuario UGEL está vinculado a una UGEL

    # Obtener parámetros de búsqueda y filtrado desde la solicitud
    search_nombre = request.GET.get('search_nombre', '')
    search_codigo = request.GET.get('search_codigo', '')
    filter_modalidad = request.GET.get('filter_modalidad', '')
    filter_ugel = request.GET.get('filter_ugel', '')

    # Consulta inicial para obtener los colegios
    colegios = InstitucionEducativa.objects.all()

    # Filtrar colegios según el tipo de usuario
    if tipo_usuario == "UGEL" and ugel_usuario:
        colegios = colegios.filter(ugel=ugel_usuario)
    # Si el tipo de usuario es "REGIONAL", no aplicamos filtro adicional

    # Filtrar por nombre
    if search_nombre:
        colegios = colegios.filter(cen_edu__icontains=search_nombre)

    # Filtrar por código modular
    if search_codigo:
        colegios = colegios.filter(cod_mod__icontains=search_codigo)

    # Filtrar por modalidad
    if filter_modalidad:
        colegios = colegios.filter(d_niv_mod=filter_modalidad)

    # Filtrar por UGEL (solo para el usuario REGIONAL)
    if tipo_usuario == "REGIONAL" and filter_ugel:
        colegios = colegios.filter(ugel__id=filter_ugel)

    # Paginación: Mostrar 50 colegios por página
    paginator = Paginator(colegios, 50)  # 50 colegios por página
    page_number = request.GET.get('page')  # Número de página actual
    page_obj = paginator.get_page(page_number)

    # Obtener las modalidades y las UGELs para los filtros
    modalidades = InstitucionEducativa.NIVEL_MODALIDAD_CHOICES
    modalidades = [modalidad[0] for modalidad in modalidades]

    # Obtener UGELs registradas (solo para el filtro del usuario REGIONAL)
    ugeles = Ugel.objects.all() if tipo_usuario == "REGIONAL" else None

    return render(request, 'app/registrar_colegios.html', {
        'colegios': page_obj,  # Colegios de la página actual
        'modalidades': modalidades,
        'ugeles': ugeles,
        'paginator': paginator,  # Paginador
        'page_obj': page_obj,   # Información sobre la página actual
    })




@login_required
def agregar_colegio(request):
    if request.method == 'POST':
        form = InstitucionEducativaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Colegio agregado exitosamente.")
            return redirect('registrar_colegios')
        else:
            print(form.errors)
    else:
        form = InstitucionEducativaForm()
    return render(request, 'app/agregar_colegio.html', {'form': form})
    
@login_required
def editar_colegio(request, id):
    colegio = get_object_or_404(InstitucionEducativa, id=id)
    if request.method == 'POST':
        form = InstitucionEducativaForm(request.POST,request.FILES, instance=colegio)
        if form.is_valid():
            form.save()
            messages.success(request, "Colegio actualizado exitosamente.")
            if(request.user.tipo_usuario == "UGEL" or request.user.tipo_usuario == "REGIONAL"):
                return redirect('registrar_colegios')
            else:
                return redirect('home')
    else:
        form = InstitucionEducativaForm(instance=colegio)
    return render(request, 'app/editar_colegio.html', {'form': form})
@login_required
def eliminar_colegio(request, id):
    colegio = get_object_or_404(InstitucionEducativa, id=id)
    
    if request.method == "POST":
        colegio.delete()
        messages.success(request, "Colegio eliminado exitosamente.")
        return redirect('registrar_colegios')

    return render(request, 'app/confirmar_eliminar_colegio.html', {'colegio': colegio})

@login_required
def registrar_director(request):
    if not hasattr(request.user, 'ugel') or not request.user.ugel:
        messages.error(request, "No tienes una UGEL asignada.")
        return redirect('dashboard')  # Cambia 'dashboard' según corresponda

    if request.method == 'POST':
        form = DirectorForm(request.POST, ugel=request.user.ugel)
        if form.is_valid():
            form.save()
            messages.success(request, "Director registrado exitosamente.")
            return redirect('control_usuarios')
        else:
            messages.error(request, "Error al registrar el director. Verifique los datos.")
    else:
        form = DirectorForm(ugel=request.user.ugel)

    return render(request, 'app/registrar_director.html', {'form': form})
import json
from django.utils.text import slugify  
@login_required
def registrar_vacantes(request):
    colegio = InstitucionEducativa.objects.filter(cod_mod=request.user.codigo_modular).first()

    if not colegio:
        messages.error(request, "No se encontró la institución educativa asociada a este usuario.")
        return redirect('home')

    grados = VacanteFinal.get_grados_por_nivel(colegio.d_niv_mod)

    vacante, created = VacanteFinal.objects.get_or_create(
        codigo_modular=colegio.cod_mod,
        defaults={"nivel": colegio.d_niv_mod, "vacantes": json.dumps({}), "vacantes_nee": json.dumps({})}
    )

    vacantes_dict = json.loads(vacante.vacantes)
    vacantes_nee_dict = json.loads(vacante.vacantes_nee)

    if request.method == "POST":
        #print("🛠️ DEBUG: Datos recibidos del formulario ->", request.POST)

        for grado in grados:
            grado_key = slugify(grado)  # Asegura compatibilidad con slugify

            vacantes_regulares = request.POST.get(f"vacantes_{grado_key}_regulares", "0").strip()
            vacantes_nee = request.POST.get(f"vacantes_{grado_key}_nee", "0").strip()

            #print(f"🛠️ DEBUG: Procesando {grado} -> Regulares: {vacantes_regulares}, NEE: {vacantes_nee}")

            # Asegurar que sean números válidos antes de convertir a int
            vacantes_dict[grado] = int(vacantes_regulares) if vacantes_regulares.isdigit() else 0
            vacantes_nee_dict[grado] = int(vacantes_nee) if vacantes_nee.isdigit() else 0

        vacante.vacantes = json.dumps(vacantes_dict)
        vacante.vacantes_nee = json.dumps(vacantes_nee_dict)
        vacante.save()

        #print("✅ DEBUG: Vacantes guardadas ->", vacantes_dict)
        #print("✅ DEBUG: Vacantes NEE guardadas ->", vacantes_nee_dict)

        messages.success(request, "Vacantes actualizadas correctamente.")
        return redirect('registrar_vacantes')

    data_grados = [
        {
            "grado": grado,
            "vacantes_regulares": vacantes_dict.get(grado, 0),
            "vacantes_nee": vacantes_nee_dict.get(grado, 0),
        }
        for grado in grados
    ]

    #print("📢 DEBUG: Datos enviados al HTML ->", data_grados)

    return render(request, 'app/registrar_vacantes.html', {
        "colegio": colegio,
        "data_grados": data_grados,
    })

@login_required
def registro_vacantes_nee(request):
    return render(request, 'app/registro_vacantes_nee.html')

@login_required
def perfil(request):
    usuario = request.user

    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()

            # Enviar correo al usuario confirmando la actualización
            send_mail(
                subject='Perfil actualizado correctamente',
                message=f'Hola {usuario.nombre}, tu perfil ha sido actualizado con éxito.',
                from_email='sirevaregional@drecusco.edu.pe',
                recipient_list=[usuario.email],
                fail_silently=False,
            )

            return redirect('home')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'app/editar_usuario.html', {'form': form, 'usuario': usuario})

def control_usuarios(request):
    # Obtener todos los usuarios, excluyendo el actual
    usuarios = Usuario.objects.exclude(id=request.user.id)

    # Filtrar por tipo de usuario
    if request.user.tipo_usuario == "REGIONAL":
        usuarios = usuarios.filter(tipo_usuario__in=["REGIONAL", "UGEL", "DIRECTOR"])
    elif request.user.tipo_usuario == "UGEL":
        usuarios = usuarios.filter(tipo_usuario="DIRECTOR", ugel=request.user.ugel)
    else:
        usuarios = Usuario.objects.none()

    # Filtrar por nombre, apellido, o DNI
    query = request.GET.get('query', '').strip()
    if query:
        usuarios = usuarios.filter(
            Q(nombre__icontains=query) |
            Q(apellido_paterno__icontains=query) |
            Q(apellido_materno__icontains=query) |
            Q(dni__icontains=query)
        )

    # Filtrar por tipo de usuario
    tipo_usuario = request.GET.get('tipo_usuario', '').strip()
    if tipo_usuario:
        usuarios = usuarios.filter(tipo_usuario=tipo_usuario)

    # Filtrar por UGEL
    filter_ugel = request.GET.get('ugel', '').strip()
    if filter_ugel:
        usuarios = usuarios.filter(ugel__id=filter_ugel)

    # Implementar paginación: 50 usuarios por página
    paginator = Paginator(usuarios, 50)
    page_number = request.GET.get('page')  # Obtener el número de la página actual
    page_obj = paginator.get_page(page_number)  # Obtener los usuarios de la página actual

    return render(request, 'app/control_usuarios.html', {
        'page_obj': page_obj,  # Pasar el objeto de la página al template
        'ugeles': Ugel.objects.all(),  # Pasar UGELs para el filtro
        'user': request.user,  # Usuario actual
    })

from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UsuarioForm
from .models import Usuario  # Asegúrate de importar tu modelo

@login_required
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()

            # Enviar correo al usuario editado
            send_mail(
                subject='Actualización de usuario',
                message=f'Hola {form.cleaned_data["nombre"]}, tu información ha sido actualizada correctamente.',
                from_email='sirevaregional@drecusco.edu.pe',
                recipient_list=[form.cleaned_data['email']],
                fail_silently=False,
            )

            return redirect('control_usuarios')
    else:
        form = UsuarioForm(instance=usuario)

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
import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import InstitucionEducativa, Ugel

def cargar_datos_colegios(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")
        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Por favor, suba un archivo CSV válido.")
            return redirect("registrar_colegios")

        try:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file, delimiter=";")
            for row in reader:
                ugel_nombre = row["D_DREUGEL"].strip()
                if ugel_nombre == "UGEL LA CONVENCIÓN":
                    ugel_nombre = "UGEL LA CONVENCION"

                try:
                    ugel = Ugel.objects.get(nombre=ugel_nombre)
                except Ugel.DoesNotExist:
                    messages.error(request, f"Error: La UGEL '{ugel_nombre}' no está registrada.")
                    continue

                # Normalización de campos según tus choices y validaciones
                d_niv_mod = row["D_NIV_MOD"].strip() or "Desconocido"
                if d_niv_mod not in dict(InstitucionEducativa.NIVEL_MODALIDAD_CHOICES):
                    d_niv_mod = "Desconocido"

                d_forma = row["D_FORMA"].strip() or "Desconocido"
                if d_forma not in dict(InstitucionEducativa.TIPO_FORMA_ATENCION):
                    d_forma = "Desconocido"

                d_tipss = row["D_TIPSSEXO"].strip() or "Desconocido"
                if d_tipss not in dict(InstitucionEducativa.TIPOS_SERVICIO):
                    d_tipss = "Desconocido"

                d_gestion = row["D_GESTION"].strip() or "Desconocido"
                if d_gestion not in dict(InstitucionEducativa.TIPO_GESTION):
                    d_gestion = "Desconocido"

                # Cargar o actualizar el colegio
                InstitucionEducativa.objects.update_or_create(
                    cod_mod=row["COD_MOD"].strip(),
                    defaults={
                        "cen_edu": row["CEN_EDU"].strip() or "Desconocido",
                        "niv_mod": row["NIV_MOD"].strip() or "Desconocido",
                        "d_niv_mod": d_niv_mod,
                        "d_forma": d_forma,
                        "d_cod_car": row["D_COD_CAR"].strip() or "Desconocido",
                        "d_tipss": d_tipss,
                        "d_gestion": d_gestion,
                        "d_ges_dep": row["D_GES_DEP"].strip() or "Sector Educativo",
                        "ugel": ugel,
                    }
                )
            messages.success(request, "Los datos de colegios se han cargado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo CSV: {e}")
        return redirect("home")

    return render(request, "app/carga_datos_colegios.html")

from django.http import JsonResponse
def obtener_instituciones_por_ugel(request, ugel_id):
    instituciones = InstitucionEducativa.objects.filter(ugel_id=ugel_id).values(
        'cod_mod', 'cen_edu', 'd_niv_mod', 'd_gestion'
    )
    return JsonResponse(list(instituciones), safe=False)

def generar_reporte(request):
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:

        # UGEL.csv
        ugel_io = io.StringIO()
        ugel_writer = csv.writer(ugel_io)
        ugel_writer.writerow(["ID", "Nombre", "RUC"])
        for u in Ugel.objects.all():
            ugel_writer.writerow([u.id, u.nombre, u.ruc])
        zip_file.writestr("UGEL.csv", ugel_io.getvalue())

        # Nivel.csv
        nivel_io = io.StringIO()
        nivel_writer = csv.writer(nivel_io)
        nivel_writer.writerow(["ID", "Código Modular", "Nivel"])
        for n in Nivel.objects.all():
            nivel_writer.writerow([n.id, n.codigo_modular, n.nivel])
        zip_file.writestr("Nivel.csv", nivel_io.getvalue())

        # Instituciones.csv
        ie_io = io.StringIO()
        ie_writer = csv.writer(ie_io)
        ie_writer.writerow([
            "Código Modular", "Centro Educativo", "Nivel Modalidad", "Forma Atención",
            "Tipo Servicio", "Gestión", "UGEL"
        ])
        for ie in InstitucionEducativa.objects.select_related('ugel').all():
            ie_writer.writerow([
                ie.cod_mod,
                ie.cen_edu,
                ie.d_niv_mod,
                ie.d_forma,
                ie.d_tipss,
                ie.d_gestion,
                ie.ugel.nombre if ie.ugel else "Sin UGEL"
            ])
        zip_file.writestr("Instituciones.csv", ie_io.getvalue())

        # Usuarios.csv
        user_io = io.StringIO()
        user_writer = csv.writer(user_io)
        user_writer.writerow([
            "DNI", "Nombre", "Apellido Paterno", "Apellido Materno", "Email",
            "Tipo", "Estado", "UGEL", "Código Modular"
        ])
        for u in Usuario.objects.select_related('ugel').all():
            user_writer.writerow([
                u.dni,
                u.nombre,
                u.apellido_paterno,
                u.apellido_materno,
                u.email,
                u.tipo_usuario,
                u.estado,
                u.ugel.nombre if u.ugel else "Sin UGEL",
                u.codigo_modular
            ])
        zip_file.writestr("Usuarios.csv", user_io.getvalue())

        # Vacantes.csv
        vac_io = io.StringIO()
        vac_writer = csv.writer(vac_io)
        vac_writer.writerow(["Código Modular", "Nivel", "Vacantes Regulares", "Vacantes NEE"])
        for v in VacanteFinal.objects.all():
            datos = v.obtener_vacantes()
            vac_writer.writerow([
                v.codigo_modular,
                v.nivel,
                json.dumps(datos.get("regulares", {}), ensure_ascii=False),
                json.dumps(datos.get("nee", {}), ensure_ascii=False)
            ])
        zip_file.writestr("Vacantes.csv", vac_io.getvalue())

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=reporte_respaldo.zip'
    return response
def vacantes_disponibles(request):
    # Obtener los parámetros GET
    search_nombre = request.GET.get('search_nombre', '')
    search_codigo = request.GET.get('search_codigo', '')
    filter_modalidad = request.GET.get('filter_modalidad', '')
    filter_ugel = request.GET.get('filter_ugel', '')

    tipo_usuario = "REGIONAL"  # <- Ajusta esto según tu lógica de autenticación

    # Consulta inicial
    colegios = InstitucionEducativa.objects.all()

    # Filtros aplicados
    if search_nombre:
        colegios = colegios.filter(cen_edu__icontains=search_nombre)

    if search_codigo:
        colegios = colegios.filter(cod_mod__icontains=search_codigo)

    if filter_modalidad:
        colegios = colegios.filter(d_niv_mod=filter_modalidad)

    if tipo_usuario == "REGIONAL" and filter_ugel:
        colegios = colegios.filter(ugel__id=filter_ugel)

    # Paginación
    paginator = Paginator(colegios, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Modalidades para el combo
    modalidades = [m[0] for m in InstitucionEducativa.NIVEL_MODALIDAD_CHOICES]
    
    # Lista de UGELs
    ugeles = Ugel.objects.all()

    return render(request, 'app/tabla_vacantes.html', {
        'colegios': page_obj,
        'modalidades': modalidades,
        'ugeles': ugeles,
                'paginator': paginator,  # Paginador
        'page_obj': page_obj,   # Información sobre la página actual
    })

def mostrar_vacantes_individual(request, cod_mod):
    try:
        vacante = VacanteFinal.objects.get(codigo_modular=cod_mod)

    except VacanteFinal.DoesNotExist:
        return HttpResponseBadRequest("Vacante no encontrada.")

    # Convertir las vacantes a un formato legible
    vacantes_regulares = json.loads(vacante.vacantes)
    vacantes_nee = json.loads(vacante.vacantes_nee)

    return JsonResponse({
        'vacantes_regulares': vacantes_regulares,
        'vacantes_nee': vacantes_nee,
    })


def enviar_encuesta(request):
    if request.method == 'POST':
        nombre = request.POST['name']
        correo = request.POST['email']
        mensaje = request.POST['message']

        asunto = f"Nuevo mensaje de {nombre}"
        cuerpo = f"""
        Has recibido un mensaje desde el formulario de contacto:

        Nombre: {nombre}
        Correo: {correo}
        Mensaje:
        {mensaje}
        """

        send_mail(
            subject=asunto,
            message=cuerpo,
            from_email='sirevaregional@drecusco.edu.pe',         # correo bot
            recipient_list=['jrodriguezphillco@gmail.com'],      # tu correo personal
            fail_silently=False,
        )

        return redirect('/')  # o una página de "gracias"

    return redirect('/')


from django.contrib.auth.hashers import make_password
from .models import Usuario, Ugel  # Asegúrate de importar tus modelos

def cargar_directores_csv(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")
        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Por favor, suba un archivo CSV válido.")
            return redirect("registrar_director")

        try:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                try:
                    ugel = Ugel.objects.get(nombre=row["ugel"].strip())
                except Ugel.DoesNotExist:
                    messages.error(request, f"UGEL no encontrada: {row['ugel']}")
                    continue

                usuario, creado = Usuario.objects.update_or_create(
                    dni=int(row["dni"]),
                    defaults={
                        "nombre": row["nombre"].strip().upper(),
                        "apellido_paterno": row["apellido_paterno"].strip().upper(),
                        "apellido_materno": row["apellido_materno"].strip().upper(),
                        "email": row["email"].strip().lower(),
                        "telefono": row.get("telefono", "").strip(),
                        "tipo_usuario": "DIRECTOR",
                        "codigo_modular": row["codigo_modular"].strip(),
                        "ugel": ugel,
                        "estado": "ACTIVO",
                        "is_staff": False,
                        "is_superuser": False,
                        "password": make_password("123456"),  # Contraseña por defecto
                    }
                )
            messages.success(request, "Carga de directores completada.")
        except Exception as e:
            messages.error(request, f"Error al cargar el archivo: {e}")
        return redirect("home")

    return render(request, "app/carga_directores.html")

def generar_contrasena(longitud=10):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for i in range(longitud))

def recuperar_contrasena(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            usuario = Usuario.objects.get(email=email)
            nueva_contra = generar_contrasena()
            usuario.set_password(nueva_contra)
            usuario.save()

            send_mail(
                'Recuperación de contraseña - SIREVA',
                f'Hola {usuario.nombre}, tu nueva contraseña es: {nueva_contra}\n\nPor favor cámbiala después de iniciar sesión.',
                'sirevaregional@drecusco.edu.pe',
                [email],
                fail_silently=False,
            )

            messages.success(request, 'Se ha enviado una nueva contraseña a tu correo.')
            return redirect('login')
        except Usuario.DoesNotExist:
            messages.error(request, 'El correo no está registrado.')
    
    return render(request, 'app/recuperar_contrasena.html')