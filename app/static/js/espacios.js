// espacios.js - Gestión de espacios de estacionamiento

document.addEventListener('DOMContentLoaded', () => {
    cargarEspacios();
    cargarEstadisticas();
    
    // Event listeners
    document.getElementById('btn-nuevo-espacio')?.addEventListener('click', mostrarFormularioNuevoEspacio);
    document.getElementById('btn-filtros')?.addEventListener('click', toggleFiltros);
    document.getElementById('btn-aplicar-filtros')?.addEventListener('click', aplicarFiltros);
});

// ========== CARGAR ESPACIOS ==========
async function cargarEspacios(filtros = {}) {
    try {
        // Construir URL con filtros
        const params = new URLSearchParams();
        if (filtros.estado) params.append('estado', filtros.estado);
        if (filtros.tipo) params.append('tipo', filtros.tipo);
        if (filtros.seccion) params.append('seccion', filtros.seccion);
        
        const url = `/api/espacios${params.toString() ? '?' + params.toString() : ''}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('Error al cargar espacios');
        }
        
        const espacios = await response.json();
        mostrarEspacios(espacios);
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudieron cargar los espacios'
        });
    }
}

// ========== MOSTRAR ESPACIOS EN EL GRID ==========
function mostrarEspacios(espacios) {
    const grid = document.getElementById('espacios-grid');
    const mensajeVacio = document.getElementById('mensaje-vacio');
    
    if (espacios.length === 0) {
        mensajeVacio.textContent = 'No hay espacios configurados';
        mensajeVacio.style.display = 'block';
        grid.innerHTML = '<p class="no-data" id="mensaje-vacio">No hay espacios configurados</p>';
        return;
    }
    
    grid.innerHTML = '';
    
    espacios.forEach(espacio => {
        const card = crearTarjetaEspacio(espacio);
        grid.appendChild(card);
    });
}

// ========== CREAR TARJETA DE ESPACIO ==========
function crearTarjetaEspacio(espacio) {
    const card = document.createElement('div');
    card.className = `espacio-card ${espacio.estado}`;
    card.dataset.id = espacio.id;
    
    // Icono según tipo
    let icono = 'fa-parking';
    if (espacio.tipo === 'discapacitado') icono = 'fa-wheelchair';
    if (espacio.tipo === 'moto') icono = 'fa-motorcycle';
    
    // Estado traducido
    const estadosTraducidos = {
        'disponible': 'Disponible',
        'ocupado': 'Ocupado',
        'mantenimiento': 'Mantenimiento'
    };
    
    card.innerHTML = `
        <i class="fas ${icono} espacio-icono"></i>
        <div class="espacio-numero">${espacio.numero}</div>
        <div class="espacio-tipo">${capitalizarPrimeraLetra(espacio.tipo)}</div>
        <span class="espacio-estado">${estadosTraducidos[espacio.estado]}</span>
    `;
    
    // Click en la tarjeta
    card.addEventListener('click', () => mostrarDetallesEspacio(espacio));
    
    return card;
}

// ========== MOSTRAR DETALLES DEL ESPACIO ==========
function mostrarDetallesEspacio(espacio) {
    const estadosTraducidos = {
        'disponible': 'Disponible',
        'ocupado': 'Ocupado',
        'mantenimiento': 'Mantenimiento'
    };
    
    Swal.fire({
        title: `Espacio ${espacio.numero}`,
        html: `
            <div style="text-align: left; padding: 1rem;">
                <p><strong>Tipo:</strong> ${capitalizarPrimeraLetra(espacio.tipo)}</p>
                <p><strong>Estado:</strong> ${estadosTraducidos[espacio.estado]}</p>
                <p><strong>Piso:</strong> ${espacio.piso}</p>
                <p><strong>Sección:</strong> ${espacio.seccion}</p>
            </div>
        `,
        showCancelButton: true,
        showDenyButton: true,
        showCloseButton: true,  // ⭐ Agregar X para cerrar
        confirmButtonText: '<i class="fas fa-exchange-alt"></i> Cambiar Estado',
        denyButtonText: '<i class="fas fa-edit"></i> Editar',
        cancelButtonText: '<i class="fas fa-trash"></i> Eliminar',  // ⭐ Cambiar cancelButton por Eliminar
        confirmButtonColor: '#2486DB',
        denyButtonColor: '#6c757d',
        cancelButtonColor: '#dc3545',  // ⭐ Color rojo para eliminar
        reverseButtons: true  // ⭐ Poner eliminar al final
    }).then((result) => {
        if (result.isConfirmed) {
            // Cambiar estado
            mostrarFormularioCambiarEstado(espacio);
        } else if (result.isDenied) {
            // Editar
            mostrarFormularioEditarEspacio(espacio);
        } else if (result.dismiss === Swal.DismissReason.cancel) {
            // Eliminar (botón cancelar ahora es eliminar)
            confirmarEliminarEspacio(espacio);
        }
    });
}


// ========== FORMULARIO NUEVO ESPACIO ==========
async function mostrarFormularioNuevoEspacio() {
    const { value: formValues } = await Swal.fire({
        title: 'Nuevo Espacio',
        html: `
            <div style="text-align: left;">
                <div class="form-group">
                    <label>Número de espacio *</label>
                    <input id="swal-numero" class="swal2-input" placeholder="Ej: A-01" required>
                </div>
                <div class="form-group">
                    <label>Tipo *</label>
                    <select id="swal-tipo" class="swal2-input">
                        <option value="regular">Regular</option>
                        <option value="discapacitado">Discapacitado</option>
                        <option value="moto">Moto</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Estado *</label>
                    <select id="swal-estado" class="swal2-input">
                        <option value="disponible">Disponible</option>
                        <option value="ocupado">Ocupado</option>
                        <option value="mantenimiento">Mantenimiento</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Piso</label>
                    <input id="swal-piso" class="swal2-input" type="number" value="1" min="1">
                </div>
                <div class="form-group">
                    <label>Sección</label>
                    <input id="swal-seccion" class="swal2-input" placeholder="Ej: A" maxlength="1">
                </div>
            </div>
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'Crear',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#2486DB',
        preConfirm: () => {
            const numero = document.getElementById('swal-numero').value;
            const tipo = document.getElementById('swal-tipo').value;
            const estado = document.getElementById('swal-estado').value;
            const piso = document.getElementById('swal-piso').value;
            const seccion = document.getElementById('swal-seccion').value;
            
            if (!numero) {
                Swal.showValidationMessage('El número de espacio es requerido');
                return false;
            }
            
            return { numero, tipo, estado, piso: parseInt(piso), seccion };
        }
    });
    
    if (formValues) {
        await crearEspacio(formValues);
    }
}

// ========== CREAR ESPACIO (API) ==========
async function crearEspacio(datos) {
    try {
        const response = await fetch('/api/espacios', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Error al crear espacio');
        }
        
        Swal.fire({
            icon: 'success',
            title: '¡Éxito!',
            text: 'Espacio creado correctamente',
            timer: 2000
        });
        
        // Recargar espacios y estadísticas
        cargarEspacios();
        cargarEstadisticas();
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}

// ========== CARGAR ESTADÍSTICAS ==========
async function cargarEstadisticas() {
    try {
        const response = await fetch('/api/espacios/estadisticas');
        
        if (!response.ok) {
            throw new Error('Error al cargar estadísticas');
        }
        
        const stats = await response.json();
        
        document.getElementById('stat-total').textContent = stats.total;
        document.getElementById('stat-disponibles').textContent = stats.disponibles;
        document.getElementById('stat-ocupados').textContent = stats.ocupados;
        document.getElementById('stat-mantenimiento').textContent = stats.mantenimiento;
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// ========== CAMBIAR ESTADO ==========
async function mostrarFormularioCambiarEstado(espacio) {
    const { value: nuevoEstado } = await Swal.fire({
        title: `Cambiar estado de ${espacio.numero}`,
        input: 'select',
        inputOptions: {
            'disponible': 'Disponible',
            'ocupado': 'Ocupado',
            'mantenimiento': 'Mantenimiento'
        },
        inputValue: espacio.estado,
        showCancelButton: true,
        confirmButtonText: 'Cambiar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#2486DB'
    });
    
    if (nuevoEstado && nuevoEstado !== espacio.estado) {
        await cambiarEstadoEspacio(espacio.id, nuevoEstado);
    }
}

async function cambiarEstadoEspacio(id, estado) {
    try {
        const response = await fetch(`/api/espacios/${id}/cambiar-estado`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ estado })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Error al cambiar estado');
        }
        
        Swal.fire({
            icon: 'success',
            title: '¡Éxito!',
            text: 'Estado cambiado correctamente',
            timer: 2000
        });
        
        cargarEspacios();
        cargarEstadisticas();
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}

// ========== FILTROS ==========
function toggleFiltros() {
    const filtros = document.getElementById('filtros-container');
    filtros.style.display = filtros.style.display === 'none' ? 'block' : 'none';
}

function aplicarFiltros() {
    const filtros = {
        estado: document.getElementById('filtro-estado').value,
        tipo: document.getElementById('filtro-tipo').value,
        seccion: document.getElementById('filtro-seccion').value
    };
    
    cargarEspacios(filtros);
}

// ========== CONFIRMAR ELIMINACIÓN DE ESPACIO ==========
async function confirmarEliminarEspacio(espacio) {
    const result = await Swal.fire({
        title: '⚠️ ¿Estás seguro?',
        html: `
            <p>Estás a punto de eliminar el espacio:</p>
            <h3 style="color: #dc3545; margin: 1rem 0;">${espacio.numero}</h3>
            <p><strong>Tipo:</strong> ${capitalizarPrimeraLetra(espacio.tipo)}</p>
            <p style="color: #dc3545; margin-top: 1rem;">
                <i class="fas fa-exclamation-triangle"></i> 
                Esta acción no se puede deshacer
            </p>
        `,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        focusCancel: true  // Foco en cancelar por seguridad
    });
    
    if (result.isConfirmed) {
        // Solicitar confirmación del admin (contraseña o segundo paso)
        await solicitarConfirmacionAdmin(espacio);
    }
}

// ========== SOLICITAR CONFIRMACIÓN DEL ADMIN ==========
async function solicitarConfirmacionAdmin(espacio) {
    const { value: confirmacion } = await Swal.fire({
        title: 'Confirmación de Admin',
        html: `
            <p>Para eliminar el espacio <strong>${espacio.numero}</strong>,<br>
            escribe la palabra <strong style="color: #dc3545;">ELIMINAR</strong> en mayúsculas:</p>
        `,
        input: 'text',
        inputPlaceholder: 'Escribe ELIMINAR',
        showCancelButton: true,
        confirmButtonText: 'Confirmar Eliminación',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#dc3545',
        inputValidator: (value) => {
            if (!value) {
                return 'Debes escribir algo';
            }
            if (value !== 'ELIMINAR') {
                return 'Debes escribir exactamente "ELIMINAR" en mayúsculas';
            }
        }
    });
    
    if (confirmacion === 'ELIMINAR') {
        await eliminarEspacio(espacio.id);
    }
}

// ========== ELIMINAR ESPACIO (API) ==========
async function eliminarEspacio(id) {
    try {
        // Mostrar loading
        Swal.fire({
            title: 'Eliminando...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            allowEscapeKey: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch(`/api/espacios/${id}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Error al eliminar espacio');
        }
        
        // Éxito
        Swal.fire({
            icon: 'success',
            title: '¡Eliminado!',
            text: result.mensaje,
            timer: 2000,
            showConfirmButton: false
        });
        
        // Recargar espacios y estadísticas
        cargarEspacios();
        cargarEstadisticas();
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error al eliminar',
            text: error.message
        });
    }
}


// ========== UTILIDADES ==========
function capitalizarPrimeraLetra(texto) {
    return texto.charAt(0).toUpperCase() + texto.slice(1);
}

// ========== FORMULARIO EDITAR ESPACIO ==========
async function mostrarFormularioEditarEspacio(espacio) {
    const { value: formValues } = await Swal.fire({
        title: `Editar Espacio ${espacio.numero}`,
        html: `
            <div style="text-align: left;">
                <div class="form-group">
                    <label>Número de espacio *</label>
                    <input id="swal-numero" class="swal2-input" value="${espacio.numero}" disabled>
                    <small style="color: #999;">El número no se puede cambiar</small>
                </div>
                <div class="form-group">
                    <label>Tipo *</label>
                    <select id="swal-tipo" class="swal2-input">
                        <option value="regular" ${espacio.tipo === 'regular' ? 'selected' : ''}>Regular</option>
                        <option value="discapacitado" ${espacio.tipo === 'discapacitado' ? 'selected' : ''}>Discapacitado</option>
                        <option value="moto" ${espacio.tipo === 'moto' ? 'selected' : ''}>Moto</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Estado *</label>
                    <select id="swal-estado" class="swal2-input">
                        <option value="disponible" ${espacio.estado === 'disponible' ? 'selected' : ''}>Disponible</option>
                        <option value="ocupado" ${espacio.estado === 'ocupado' ? 'selected' : ''}>Ocupado</option>
                        <option value="mantenimiento" ${espacio.estado === 'mantenimiento' ? 'selected' : ''}>Mantenimiento</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Piso</label>
                    <input id="swal-piso" class="swal2-input" type="number" value="${espacio.piso}" min="1">
                </div>
                <div class="form-group">
                    <label>Sección</label>
                    <input id="swal-seccion" class="swal2-input" value="${espacio.seccion}" maxlength="1">
                </div>
            </div>
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'Guardar Cambios',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#2486DB',
        preConfirm: () => {
            const tipo = document.getElementById('swal-tipo').value;
            const estado = document.getElementById('swal-estado').value;
            const piso = document.getElementById('swal-piso').value;
            const seccion = document.getElementById('swal-seccion').value;
            
            return { tipo, estado, piso: parseInt(piso), seccion };
        }
    });
    
    if (formValues) {
        await actualizarEspacio(espacio.id, formValues);
    }
}

// ========== ACTUALIZAR ESPACIO (API) ==========
async function actualizarEspacio(id, datos) {
    try {
        const response = await fetch(`/api/espacios/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Error al actualizar espacio');
        }
        
        Swal.fire({
            icon: 'success',
            title: '¡Éxito!',
            text: 'Espacio actualizado correctamente',
            timer: 2000,
            showConfirmButton: false
        });
        
        // Recargar espacios y estadísticas
        cargarEspacios();
        cargarEstadisticas();
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}
