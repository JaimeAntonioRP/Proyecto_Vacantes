function cargarInstituciones(ugelId) {
    fetch(`/instituciones/${ugelId}/`)
        .then(response => response.json())
        .then(data => {
            let table = $('#institucionesTable').DataTable();
            table.clear(); // Limpiar tabla antes de actualizar

            data.forEach(institucion => {
                table.row.add([
                    institucion.cod_mod,
                    institucion.cen_edu,
                    institucion.d_niv_mod,
                    institucion.d_gestion,
                    `<button class="btn btn-info" onclick="mostrarVacantes('${institucion.cod_mod}')">
                        <img src="/static/app/img/icono_vacantes.png" alt="Vacantes">
                    </button>`
                ]).draw();
            });
        })
        .catch(error => console.error('Error cargando instituciones:', error));
}

$(document).ready(function() {
    $('#institucionesTable').DataTable();
});
