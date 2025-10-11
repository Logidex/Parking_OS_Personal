// usuarios.js - Gestión de usuarios

document.addEventListener('DOMContentLoaded', () => {
    cargarUsuarios();
});

// ========== CARGAR USUARIOS ==========
async function cargarUsuarios() {
    try {
        const response = await fetch('/api/usuarios');
        
        if (!response.ok) {
            if (response.status === 403) {
                throw new Error('No tienes permisos para ver esta página');
            }
            throw new Error('Error al cargar usuarios');
        }
        
        const usuarios = await response.json();
        mostrarUsuarios(usuarios);
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}

// ========== MOSTRAR USUARIOS ==========
function mostrarUsuarios(usuarios) {
    const tbody = document.getElementById('tbody-usuarios');
    
    if (!tbody) return;
    
    if (usuarios.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="no-data">No hay usuarios registrados</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    
    usuarios.forEach(usuario => {
        const row = crearFilaUsuario(usuario);
        tbody.appendChild(row);
    });
}

// ========== CREAR FILA DE USUARIO ==========
function crearFilaUsuario(usuario) {
    const tr = document.createElement('tr');
    
    const rolBadge = usuario.rol === 'admin' 
        ? '<span class="badge badge-admin">👑 Admin</span>'
        : '<span class="badge badge-user">👤 Usuario</span>';
    
    tr.innerHTML = `
        <td><strong>#${usuario.id}</strong></td>
        <td><strong>${usuario.nombre_usuario}</strong></td>
        <td>${rolBadge}</td>
        <td>
            <button class="btn-icon btn-warning" onclick="cambiarPassword(${usuario.id}, '${usuario.nombre_usuario}')" title="Cambiar contraseña">
                <i class="fas fa-key"></i>
            </button>
            <button class="btn-icon btn-info" onclick="cambiarRol(${usuario.id}, '${usuario.nombre_usuario}', '${usuario.rol}')" title="Cambiar rol">
                <i class="fas fa-user-shield"></i>
            </button>
            <button class="btn-icon btn-danger" onclick="eliminarUsuario(${usuario.id}, '${usuario.nombre_usuario}')" title="Eliminar">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;
    
    return tr;
}

// ========== CREAR USUARIO ==========
async function mostrarModalCrearUsuario() {
    const { value: formValues } = await Swal.fire({
        title: 'Crear Nuevo Usuario',
        html: `
            <div style="text-align: left;">
                <label for="swal-username" style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Nombre de usuario: *</label>
                <input id="swal-username" 
                       class="swal2-input" 
                       placeholder="Ej: usuario123" 
                       style="width: 100%; margin: 0 0 1rem 0;">
                
                <label for="swal-password" style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Contraseña: *</label>
                <input id="swal-password" 
                       type="password"
                       class="swal2-input" 
                       placeholder="Mínimo 4 caracteres" 
                       style="width: 100%; margin: 0 0 1rem 0;">
                
                <label for="swal-rol" style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Rol: *</label>
                <select id="swal-rol" class="swal2-input" style="width: 100%; margin: 0;">
                    <option value="usuario">👤 Usuario</option>
                    <option value="admin">👑 Administrador</option>
                </select>
            </div>
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'Crear',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#2486DB',
        width: '500px',
        preConfirm: () => {
            const username = document.getElementById('swal-username').value.trim();
            const password = document.getElementById('swal-password').value;
            const rol = document.getElementById('swal-rol').value;
            
            if (!username) {
                Swal.showValidationMessage('El nombre de usuario es requerido');
                return false;
            }
            
            if (!password || password.length < 4) {
                Swal.showValidationMessage('La contraseña debe tener al menos 4 caracteres');
                return false;
            }
            
            return { username, password, rol };
        }
    });
    
    if (formValues) {
        await crearUsuario(formValues);
    }
}

async function crearUsuario(datos) {
    try {
        Swal.fire({
            title: 'Creando usuario...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch('/api/usuarios', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nombre_usuario: datos.username,
                password: datos.password,
                rol: datos.rol
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Error al crear usuario');
        }
        
        Swal.fire({
            icon: 'success',
            title: '¡Usuario creado!',
            text: `Usuario: ${result.usuario.nombre_usuario}`,
            confirmButtonColor: '#2486DB'
        });
        
        cargarUsuarios();
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}

// ========== ELIMINAR USUARIO ==========
async function eliminarUsuario(id, nombre) {
    const result = await Swal.fire({
        title: '¿Eliminar usuario?',
        html: `¿Estás seguro de eliminar al usuario <strong>${nombre}</strong>?<br><br>Esta acción no se puede deshacer.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d'
    });
    
    if (!result.isConfirmed) return;
    
    try {
        Swal.fire({
            title: 'Eliminando...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch(`/api/usuarios/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Error al eliminar usuario');
        }
        
        Swal.fire({
            icon: 'success',
            title: '¡Usuario eliminado!',
            text: data.mensaje,
            confirmButtonColor: '#2486DB'
        });
        
        cargarUsuarios();
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}

// ========== CAMBIAR CONTRASEÑA ==========
async function cambiarPassword(id, nombre) {
    const { value: nuevaPassword } = await Swal.fire({
        title: `Cambiar contraseña de ${nombre}`,
        input: 'password',
        inputLabel: 'Nueva contraseña',
        inputPlaceholder: 'Mínimo 4 caracteres',
        showCancelButton: true,
        confirmButtonText: 'Cambiar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#2486DB',
        inputValidator: (value) => {
            if (!value) {
                return 'Debes ingresar una contraseña';
            }
            if (value.length < 4) {
                return 'La contraseña debe tener al menos 4 caracteres';
            }
        }
    });
    
    if (!nuevaPassword) return;
    
    try {
        Swal.fire({
            title: 'Cambiando contraseña...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch(`/api/usuarios/${id}/cambiar-password`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nueva_password: nuevaPassword
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Error al cambiar contraseña');
        }
        
        Swal.fire({
            icon: 'success',
            title: '¡Contraseña cambiada!',
            text: result.mensaje,
            confirmButtonColor: '#2486DB'
        });
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}

// ========== CAMBIAR ROL ==========
async function cambiarRol(id, nombre, rolActual) {
    const nuevoRol = rolActual === 'admin' ? 'usuario' : 'admin';
    const nuevoRolTexto = nuevoRol === 'admin' ? '👑 Administrador' : '👤 Usuario';
    
    const result = await Swal.fire({
        title: `¿Cambiar rol de ${nombre}?`,
        html: `El nuevo rol será: <strong>${nuevoRolTexto}</strong>`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sí, cambiar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#2486DB'
    });
    
    if (!result.isConfirmed) return;
    
    try {
        Swal.fire({
            title: 'Cambiando rol...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch(`/api/usuarios/${id}/cambiar-rol`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                rol: nuevoRol
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Error al cambiar rol');
        }
        
        Swal.fire({
            icon: 'success',
            title: '¡Rol cambiado!',
            text: data.mensaje,
            confirmButtonColor: '#2486DB'
        });
        
        cargarUsuarios();
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}
