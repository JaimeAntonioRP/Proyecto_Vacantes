from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import json
class Ugel(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    ruc = models.CharField(max_length=11, unique=True)
    str_images = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Nivel(models.Model):
    # Relación con InstitucionEducativa
    codigo_modular = models.CharField(max_length=50)
    nivel = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nivel} - {self.codigo_modular}"
class InstitucionEducativa(models.Model):
    NIVEL_MODALIDAD_CHOICES = [
        ('Inicial - Jardín', 'Inicial - Jardín'),
        ('Inicial - Cuna-jardín', 'Inicial - Cuna-jardín'),
        ('Primaria', 'Primaria'),
        ('Secundaria', 'Secundaria'),
        ('Básica Alternativa-Inicial e Intermedio', 'Básica Alternativa-Inicial e Intermedio'),
        ('Básica Alternativa-Avanzado', 'Básica Alternativa-Avanzado'),
        ('Técnico Productiva', 'Técnico Productiva'),
        ('Básica Especial-Primaria', 'Básica Especial-Primaria'),
        ('Escuela Formación Artística', 'Escuela Formación Artística'),
        ('Escuela Superior Pedagógica', 'Escuela Superior Pedagógica'),
        ('Instituto Superior Tecnológico', 'Instituto Superior Tecnológico'),
        ('Básica Especial', 'Básica Especial'),
        ('Instituto Superior Pedagógico', 'Instituto Superior Pedagógico'),
        ('Inicial - Programa no escolarizado', 'Inicial - Programa no escolarizado'),
        ('Básica Especial-Inicial', 'Básica Especial-Inicial'),
    ]
    TIPOS_SERVICIO = [
    ('Mixto', 'Mixto'),
    ('Mujeres', 'Mujeres'),
    ('Varones', 'Varones'),
    ('Desconocido', 'Desconocido'),
    ]
    TIPO_FORMA_ATENCION = [
        ('Escolarizada', 'Escolarizada'),
        ('No aplica', 'No aplica'),
        ('No escolarizada', 'No escolarizada'),
        ('Desconocido', 'Desconocido'),
    ]
    TIPO_GESTION = [
        ('PÚBLICA', 'PÚBLICA'),
        ('PRIVADA', 'PRIVADA'),
        ('Desconocido', 'Desconocido')
    ]
    foto_colegio = models.ImageField(upload_to='fotos_colegio/', blank=True, null=True)
    cod_mod = models.CharField(max_length=10, unique=True, verbose_name="Código Modular")
    cen_edu = models.CharField(max_length=255, verbose_name="Centro Educativo", default = "Desconocido")
    niv_mod = models.CharField(max_length=20, verbose_name="Nivel Modalidad (Código)", default= "Desconocido", null=True, blank=True)
    d_niv_mod = models.CharField(
        max_length=50, 
        choices=NIVEL_MODALIDAD_CHOICES, 
        verbose_name="Nivel Modalidad (Descripción)",
        default="Desconocido"
    )
    d_forma = models.CharField(max_length=50, verbose_name="Forma de Atención", default="Desconocido", choices=TIPO_FORMA_ATENCION)
    d_cod_car = models.CharField(max_length=50, verbose_name="Código de Carrera", default= "Desconocido", null = True, blank=True)
    d_tipss = models.CharField(max_length=50, verbose_name="Tipo de Servicio", default="Desconocido", choices=TIPOS_SERVICIO)
    d_gestion = models.CharField(max_length=50,
                                 choices=TIPO_GESTION,
                                 verbose_name='Gestión',
                                 default="Desconocido")
    d_ges_dep = models.CharField(max_length=50, verbose_name="Dependencia de Gestión", default="Sector Educativo")
    ugel = models.ForeignKey('Ugel', on_delete=models.SET_NULL, null=True, verbose_name="UGEL")
    def __str__(self):
        return f"{self.cen_edu} ({self.cod_mod})"





class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')

        # Validar UGEL si el tipo de usuario requiere una UGEL
        tipo_usuario = extra_fields.get('tipo_usuario')
        if tipo_usuario in ['UGEL', 'DIRECTOR'] and not extra_fields.get('ugel'):
            raise ValueError(f'El usuario de tipo {tipo_usuario} debe pertenecer a una UGEL.')

        # Validar código modular si el tipo de usuario es DIRECTOR
        if tipo_usuario == 'DIRECTOR' and not extra_fields.get('codigo_modular'):
            raise ValueError('El usuario de tipo DIRECTOR debe tener un código modular.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser):
    dni = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=255)
    apellido_paterno = models.CharField(max_length=255)
    apellido_materno = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    tipo_usuario = models.CharField(max_length=15, choices=[
        ('REGIONAL', 'Usuario Regional'),
        ('UGEL', 'Usuario UGEL'),
        ('DIRECTOR', 'Director'),
    ], default='REGIONAL'
    )
    estado = models.CharField(max_length=10, choices=[
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ], default='ACTIVO')
    permisos = models.JSONField(default=dict, blank=True, null=True)
    ugel = models.ForeignKey('Ugel', on_delete=models.SET_NULL, null=True, blank=True, related_name="usuarios")
    codigo_modular = models.CharField(max_length=15, blank=True, null=True, default="SIN_CODIGO")  # Nuevo atributo para DIRECTORES

    # Campos necesarios para superusuario
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['dni', 'nombre', 'apellido_paterno']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} - {self.tipo_usuario}"

class VacanteFinal(models.Model):
    # Código modular como clave primaria
    codigo_modular = models.CharField(
        max_length=10,
        primary_key=True,
        verbose_name="Código Modular",
        help_text="Código modular de la institución educativa."
    )

    # Nivel de educación
    nivel = models.CharField(max_length=50)

    # Guardamos las vacantes regulares y NEE como JSON en TextFields
    vacantes = models.TextField(default="{}", verbose_name="Vacantes Regulares")  
    vacantes_nee = models.TextField(default="{}", verbose_name="Vacantes NEE")  

    def __str__(self):
        return f"{self.codigo_modular} - {self.nivel}"

    def actualizar_vacantes(self, grado, regulares, nee):
        """Actualiza el número de vacantes en un grado específico y las guarda en la base de datos."""

        try:
            vacantes_dict = json.loads(self.vacantes)  # Convertir de JSON a diccionario
            vacantes_nee_dict = json.loads(self.vacantes_nee)

            # Asegurar que los valores sean enteros
            regulares = int(regulares)
            nee = int(nee)

            # Actualizar los valores
            vacantes_dict[grado] = regulares
            vacantes_nee_dict[grado] = nee

            # Guardar los cambios en el modelo
            self.vacantes = json.dumps(vacantes_dict)
            self.vacantes_nee = json.dumps(vacantes_nee_dict)
            self.save()

            # Refrescar el modelo desde la base de datos para verificar los cambios
            self.refresh_from_db()

            print(f"✅ DEBUG: Vacantes guardadas correctamente -> {vacantes_dict}")
            print(f"✅ DEBUG: Vacantes NEE guardadas correctamente -> {vacantes_nee_dict}")

        except Exception as e:
            print(f"⚠️ ERROR: No se pudo actualizar las vacantes -> {str(e)}")


    def obtener_vacantes(self):
        """Devuelve las vacantes regulares y NEE como un diccionario."""
        return {
            "regulares": json.loads(self.vacantes),
            "nee": json.loads(self.vacantes_nee),
        }

    @staticmethod
    def get_grados_por_nivel(nivel):
        """Obtiene los grados válidos según el nivel educativo."""
        grados_por_nivel = {
            'Inicial - Jardín': ['3 años', '4 años', '5 años'],
            'Primaria': ['1er grado', '2do grado', '3er grado', '4to grado', '5to grado', '6to grado'],
            'Secundaria': ['1er grado', '2do grado', '3er grado', '4to grado', '5to grado'],
            'Básica Alternativa-Inicial e Intermedio': ['Inicial', 'Intermedio', 'Avanzado'],
            'Básica Alternativa-Avanzado': ['Inicial', 'Intermedio', 'Avanzado'],
            'Técnico Productiva': ['Módulo Básico', 'Módulo Avanzado'],
            'Básica Especial-Primaria': ['Inicial', 'Primaria'],
            'Básica Especial-Inicial': ['Inicial', 'Primaria'],
            'Escuela Formación Artística': ['Año 1', 'Año 2', 'Año 3', 'Año 4'],
            'Escuela Superior Pedagógica': ['Ciclo 1', 'Ciclo 2', 'Ciclo 3', 'Ciclo 4'],
            'Instituto Superior Pedagógico': ['Ciclo 1', 'Ciclo 2', 'Ciclo 3', 'Ciclo 4'],
            'Instituto Superior Tecnológico': ['Semestre 1', 'Semestre 2', 'Semestre 3', 'Semestre 4', 'Semestre 5', 'Semestre 6'],
        }
        return grados_por_nivel.get(nivel, [])

    def get_institucion(self):
        """Obtiene la institución educativa asociada al código modular."""
        return InstitucionEducativa.objects.filter(cod_mod=self.codigo_modular).first()