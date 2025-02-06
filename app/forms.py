from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'dni', 'nombre', 'apellido_paterno', 'apellido_materno',
            'email', 'telefono', 'password', 'tipo_usuario', 'estado', 'ugel', 'codigo_modular'
        ]
        widgets = {
            'password': forms.PasswordInput(),  # Mostrar el campo de contraseña como oculto
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        ugel = cleaned_data.get('ugel')
        codigo_modular = cleaned_data.get('codigo_modular')

        # Validar que UGEL esté proporcionado si el tipo de usuario lo requiere
        if tipo_usuario in ['UGEL', 'DIRECTOR'] and not ugel:
            raise forms.ValidationError(f"El usuario de tipo {tipo_usuario} debe pertenecer a una UGEL.")

        # Validar que código modular esté proporcionado si el tipo de usuario es DIRECTOR
        if tipo_usuario == 'DIRECTOR' and not codigo_modular:
            raise forms.ValidationError("El usuario de tipo DIRECTOR debe tener un código modular.")

        return cleaned_data

    def save(self, commit=True):
        # Sobrescribe el método save para guardar la contraseña de forma segura
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hashea la contraseña
        if commit:
            user.save()
        return user
