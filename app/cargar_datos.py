import csv
from app.models import InstitucionEducativa, Ugel

# Ruta del archivo CSV
CSV_FILE_PATH = "app/static/app/instituciones_directores.csv"

def cargar_instituciones():
    try:
        with open(CSV_FILE_PATH, encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                # Recuperar el nombre de la UGEL desde el CSV
                ugel_nombre = row["D_DREUGEL"].strip()
                if(ugel_nombre == "UGEL LA CONVENCIÓN"):
                    ugel_nombre = "UGEL LA CONVENCION"
                # Buscar la UGEL en la base de datos
                try:
                    ugel = Ugel.objects.get(nombre=ugel_nombre)
                except Ugel.DoesNotExist:
                    print(f"Error: La UGEL '{ugel_nombre}' no está registrada en la base de datos.")
                    continue  # Saltar al siguiente registro si la UGEL no existe

                # Crear o actualizar la Institución Educativa
                institucion, created_institucion = InstitucionEducativa.objects.get_or_create(
                    cod_mod=row["COD_MOD"].strip(),
                    defaults={
                        "cen_edu": row["CEN_EDU"].strip() or "Desconocido",
                        "niv_mod": row["NIV_MOD"].strip() or "Desconocido",
                        "d_niv_mod": row["D_NIV_MOD"].strip() or "Desconocido",
                        "d_forma": row["D_FORMA"].strip() or "Desconocido",
                        "d_cod_car": row["D_COD_CAR"].strip() or "No aplica",
                        "d_tipss": row["D_TIPSSEXO"].strip() or "Desconocido",
                        "d_gestion": row["D_GESTION"].strip() or "Desconocido",
                        "d_ges_dep": row["D_GES_DEP"].strip() or "Desconocido",
                        "ugel": ugel,  # Asignar la UGEL existente
                    }
                )
                if created_institucion:
                    print(f"Institución creada: {institucion}")
                else:
                    print(f"Institución ya existente: {institucion}")
    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")


from app.models import Ugel


