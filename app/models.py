from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
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
    cod_ied_N = models.CharField(max_length=50, unique=True)  # Código de la institución educativa
    nombre = models.CharField(max_length=255)  # Nombre de la institución educativa
    ugel = models.ForeignKey(Ugel, on_delete=models.CASCADE, related_name="instituciones")  # Relación con la UGEL
    cod_mod = models.CharField(max_length=50, null=False, default="-------")  # Código modular, con valor por defecto
    niveles = models.ManyToManyField(Nivel, related_name="instituciones")  # Relación muchos a muchos con niveles

    def __str__(self):
        return f"{self.nombre} ({self.cod_ied_N}) - {self.cod_mod}"




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
    telefono = models.CharField(max_length=20, blank=True, null=True)
    tipo_usuario = models.CharField(max_length=15, choices=[
        ('REGIONAL', 'Usuario Regional'),
        ('UGEL', 'Usuario UGEL'),
        ('DIRECTOR', 'Director'),
    ])
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
class Vacante(models.Model):
    institucion_educativa = models.ForeignKey(InstitucionEducativa, on_delete=models.CASCADE, related_name="vacantes")
    nivel = models.CharField(max_length=50)
    grado = models.CharField(max_length=50)
    vacantes_regulares = models.IntegerField(default=0)
    vacantes_nee = models.IntegerField(default=0)  # Vacantes para Necesidades Educativas Especiales (NEE)

    def __str__(self):
        return f"{self.institucion_educativa.nombre} - {self.nivel} {self.grado}"

    def actualizar_vacantes(self, nuevas_vacantes, nuevas_vacantes_nee):
        """Actualiza el número de vacantes regulares y NEE."""
        self.vacantes_regulares = nuevas_vacantes
        self.vacantes_nee = nuevas_vacantes_nee
        self.save()
