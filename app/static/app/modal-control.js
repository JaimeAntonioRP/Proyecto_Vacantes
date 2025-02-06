function openEditModal(id, dni, nombre, apellido_paterno, apellido_materno, email, telefono, password, tipo_usuario, estado, ugel, codigo_modular) {
    document.getElementById("editForm").action = `/editar_usuario/${id}/`;
    document.getElementById("editUserId").value = id;
    document.getElementById("editDni").value = dni;
    document.getElementById("editNombre").value = nombre;
    document.getElementById("editApellidoPaterno").value = apellido_paterno;
    document.getElementById("editApellidoMaterno").value = apellido_materno;
    document.getElementById("editEmail").value = email;
    document.getElementById("editTelefono").value = telefono;
    document.getElementById("editPassword").value = password; // Opcional
    document.getElementById("editTipoUsuario").value = tipo_usuario;
    document.getElementById("editEstado").value = estado;
    document.getElementById("editUgel").value = ugel;
    document.getElementById("editCodigoModular").value = codigo_modular;

    document.getElementById("editModal").style.display = "block";
}

function closeEditModal() {
    document.getElementById("editModal").style.display = "none";
}
