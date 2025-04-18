from django import forms
from .models import Usuario, InstitucionEducativa, Ugel
from django.core.exceptions import ValidationError
import re


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'dni', 'nombre', 'apellido_paterno', 'apellido_materno',
            'email', 'telefono', 'password', 'tipo_usuario', 'estado', 'ugel', 'codigo_modular'
        ]
        widgets = {
            'dni': forms.TextInput(attrs={
                'pattern': '[0-9]{8}',
                'maxlength': '8',
                'inputmode': 'numeric',
                'title': 'Ingrese exactamente 8 dígitos numéricos'
            }),
            'telefono': forms.TextInput(attrs={
                'pattern': '[0-9]{9}',
                'maxlength': '9',
                'inputmode': 'numeric',
                'title': 'Ingrese exactamente 9 dígitos numéricos'
            }),
            'password': forms.PasswordInput(),
        }

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if dni:
            # Elimina todo lo que no sea dígito
            dni = re.sub(r'\D', '', str(dni))
            if len(dni) != 8:
                raise ValidationError('El DNI debe tener exactamente 8 dígitos numéricos.')
        return dni

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Elimina todo lo que no sea dígito
            telefono = re.sub(r'\D', '', str(telefono))
            if len(telefono) != 9:
                raise ValidationError('El teléfono debe tener exactamente 9 dígitos numéricos.')
        return telefono

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        ugel = cleaned_data.get('ugel')
        codigo_modular = cleaned_data.get('codigo_modular')

        if tipo_usuario in ['UGEL', 'DIRECTOR'] and not ugel:
            raise forms.ValidationError(f"El usuario de tipo {tipo_usuario} debe pertenecer a una UGEL.")
        if tipo_usuario == 'DIRECTOR' and not codigo_modular:
            raise forms.ValidationError("El usuario de tipo DIRECTOR debe tener un código modular.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class DirectorForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'dni', 'nombre', 'apellido_paterno', 'apellido_materno',
            'email', 'telefono', 'password', 'estado', 'codigo_modular'
        ]  # No incluimos tipo_usuario ni ugel porque estarán predefinidos
        widgets = {
            'password': forms.PasswordInput(),  # Mostrar el campo de contraseña como oculto
        }

    def __init__(self, *args, **kwargs):
        # Recibimos la UGEL del usuario que crea el director
        self.ugel = kwargs.pop('ugel', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        codigo_modular = cleaned_data.get('codigo_modular')

        # Validar que el código modular esté presente
        if not codigo_modular:
            raise forms.ValidationError("El director debe tener un código modular asociado.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hashea la contraseña
        user.tipo_usuario = 'DIRECTOR'  # Establecer tipo de usuario como DIRECTOR
        user.ugel = self.ugel  # Asignar la UGEL pasada en el constructor
        if commit:
            user.save()
        return user
    


class InstitucionEducativaForm(forms.ModelForm):
    class Meta:
        model = InstitucionEducativa
        fields = [
            'cod_mod', 
            'cen_edu', 
            'niv_mod', 
            'd_niv_mod', 
            'd_forma', 
            'd_cod_car', 
            'd_tipss', 
            'd_gestion', 
            'd_ges_dep', 
            'ugel',  # Relación con UGEL
        ]
        widgets = {
            'cod_mod': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Modular'}),
            'cen_edu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Centro Educativo'}),
            'niv_mod': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nivel Modalidad (Código)'}),
            'd_niv_mod': forms.Select(attrs={'class': 'form-control'}, choices=InstitucionEducativa.NIVEL_MODALIDAD_CHOICES),
            'd_forma': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Forma de Atención'}),
            'd_cod_car': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código de Carrera'}),
            'd_tipss': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo de Servicio'}),
            'd_gestion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Gestión'}),
            'd_ges_dep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dependencia de Gestión'}),
            'ugel': forms.Select(attrs={'class': 'form-control'}),  # Selector para UGELs
        }
