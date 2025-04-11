import csv
from app.models import Usuario, InstitucionEducativa

def cargar_usuarios_desde_csv(ruta_csv):
    try:
        with open(ruta_csv, encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=";")  # Asegúrate de que el delimitador coincida

            for row in reader:
                # Obtener el código modular desde la columna correcta
                codigo_modular = row["Cód. Mod."].strip()
                institucion = InstitucionEducativa.objects.filter(cod_mod=codigo_modular).first()

                if not institucion or not institucion.ugel:
                    print(f"Error: No se encontró institución o UGEL para el código modular '{codigo_modular}'. Saltando usuario.")
                    continue

                # Determinar valores para los campos del usuario
                dni = row.get("DNI")
                if not dni:  # Si no hay DNI, generar uno a partir del código modular
                    dni = f"{codigo_modular}000"

                # Separar nombre y apellidos del campo "Nombre Director"
                nombre_completo = row["Nombre Director"].strip()
                if "," in nombre_completo:
                    apellido_paterno, nombre = map(str.strip, nombre_completo.split(",", 1))
                    apellido_materno = "SIN_APELLIDO"
                else:
                    nombre = nombre_completo
                    apellido_paterno = "SIN_APELLIDO"
                    apellido_materno = "SIN_APELLIDO"

                # Crear o actualizar el usuario
                usuario, creado = Usuario.objects.get_or_create(
                    email=f"{codigo_modular}@geredu.com",  # Usar correo o generar uno
                    defaults={
                        "dni": dni,
                        "nombre": nombre,
                        "apellido_paterno": apellido_paterno,
                        "apellido_materno": apellido_materno,
                        "telefono": row["Telefono"].strip() if row["Telefono"].strip() else None,
                        "tipo_usuario": "DIRECTOR",
                        "ugel": institucion.ugel,  # Asociar la UGEL recuperada de la institución
                        "codigo_modular": codigo_modular,
                    }
                )

                # Si el usuario fue creado, establecer su contraseña
                if creado:
                    usuario.set_password(f"geredu{codigo_modular}")
                    usuario.save()
                    print(f"Usuario creado: {usuario}")
                else:
                    print(f"Usuario ya existente: {usuario}")

    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")
