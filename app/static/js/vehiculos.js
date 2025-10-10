// vehiculos.js - Gestión de vehículos

document.addEventListener('DOMContentLoaded', () => {
    cargarVehiculos();
    cargarEstadisticas();
    
    // Event listeners
    document.getElementById('btn-nuevo-vehiculo')?.addEventListener('click', mostrarFormularioNuevoVehiculo);
    
    // Búsqueda en tiempo real
    document.getElementById('buscar-vehiculo')?.addEventListener('input', (e) => {
        const termino = e.target.value;
        cargarVehiculos({ buscar: termino });
    });
});

// ========== CARGAR VEHÍCULOS ==========
async function cargarVehiculos(filtros = {}) {
    try {
        const params = new URLSearchParams();
        if (filtros.tipo) params.append('tipo', filtros.tipo);
        if (filtros.buscar) params.append('buscar', filtros.buscar);
        
        const url = `/api/vehiculos${params.toString() ? '?' + params.toString() : ''}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('Error al cargar vehículos');
        }
        
        const vehiculos = await response.json();
        mostrarVehiculos(vehiculos);
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudieron cargar los vehículos'
        });
    }
}

// ========== MOSTRAR VEHÍCULOS EN LA TABLA ==========
function mostrarVehiculos(vehiculos) {
    const tbody = document.getElementById('tbody-vehiculos');
    
    if (vehiculos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="no-data">No hay vehículos registrados</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    
    vehiculos.forEach(vehiculo => {
        const row = crearFilaVehiculo(vehiculo);
        tbody.appendChild(row);
    });
}

// ========== CREAR FILA DE VEHÍCULO ==========
function crearFilaVehiculo(vehiculo) {
    const tr = document.createElement('tr');
    tr.dataset.id = vehiculo.id;
    
    // Iconos según tipo
    const iconosTipo = {
        'sedan': 'fa-car',
        'suv': 'fa-truck',
        'pickup': 'fa-truck-pickup',
        'moto': 'fa-motorcycle',
        'van': 'fa-van-shuttle',
        'otro': 'fa-car-side'
    };
    
    const icono = iconosTipo[vehiculo.tipo] || 'fa-car';
    
    tr.innerHTML = `
        <td><strong>${vehiculo.placa}</strong></td>
        <td>${vehiculo.marca}</td>
        <td>${vehiculo.modelo}</td>
        <td>
            <span class="badge-color" style="background-color: ${obtenerColorHex(vehiculo.color)};">
                ${vehiculo.color}
            </span>
        </td>
        <td>
            <i class="fas ${icono}"></i>
            ${capitalizarPrimeraLetra(vehiculo.tipo)}
        </td>
        <td>${vehiculo.propietario || '-'}</td>
        <td>
            <div class="action-buttons">
                <button class="btn-icon btn-view" title="Ver detalles" onclick="verDetallesVehiculo(${vehiculo.id})">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn-icon btn-edit" title="Editar" onclick="editarVehiculo(${vehiculo.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon btn-delete" title="Eliminar" onclick="confirmarEliminarVehiculo(${vehiculo.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </td>
    `;
    
    return tr;
}

// ========== VER DETALLES DEL VEHÍCULO ==========
async function verDetallesVehiculo(id) {
    try {
        const response = await fetch(`/api/vehiculos/${id}`);
        const vehiculo = await response.json();
        
        Swal.fire({
            title: `Vehículo ${vehiculo.placa}`,
            html: `
                <div style="text-align: left; padding: 1rem;">
                    <p><strong>Placa:</strong> ${vehiculo.placa}</p>
                    <p><strong>Marca:</strong> ${vehiculo.marca}</p>
                    <p><strong>Modelo:</strong> ${vehiculo.modelo}</p>
                    <p><strong>Color:</strong> ${vehiculo.color}</p>
                    <p><strong>Tipo:</strong> ${capitalizarPrimeraLetra(vehiculo.tipo)}</p>
                    ${vehiculo.propietario ? `<p><strong>Propietario:</strong> ${vehiculo.propietario}</p>` : ''}
                    ${vehiculo.telefono ? `<p><strong>Teléfono:</strong> ${vehiculo.telefono}</p>` : ''}
                </div>
            `,
            confirmButtonText: 'Cerrar',
            confirmButtonColor: '#2486DB'
        });
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudo cargar el vehículo'
        });
    }
}

// ========== FORMULARIO NUEVO VEHÍCULO ==========
async function mostrarFormularioNuevoVehiculo() {
    const { value: formValues } = await Swal.fire({
        title: 'Nuevo Vehículo',
        html: `
            <div style="text-align: left;">
                <div class="form-group">
                    <label>Placa *</label>
                    <input id="swal-placa" class="swal2-input" placeholder="Ej: ABC123" style="text-transform: uppercase;" required>
                </div>
                <div class="form-group">
                    <label>Marca *</label>
                    <input id="swal-marca" class="swal2-input" placeholder="Ej: Toyota" required>
                </div>
                <div class="form-group">
                    <label>Modelo *</label>
                    <input id="swal-modelo" class="swal2-input" placeholder="Ej: Corolla" required>
                </div>
                <div class="form-group">
                    <label>Color *</label>
                    <input id="swal-color" class="swal2-input" placeholder="Ej: Rojo" required>
                </div>
                <div class="form-group">
                    <label>Tipo *</label>
                    <select id="swal-tipo" class="swal2-input">
                        <option value="sedan">Sedán</option>
                        <option value="suv">SUV</option>
                        <option value="pickup">Pickup</option>
                        <option value="moto">Moto</option>
                        <option value="van">Van</option>
                        <option value="otro">Otro</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Propietario (opcional)</label>
                    <input id="swal-propietario" class="swal2-input" placeholder="Nombre del propietario">
                </div>
                <div class="form-group">
                    <label>Teléfono (opcional)</label>
                    <input id="swal-telefono" class="swal2-input" type="tel" placeholder="Ej: 1234567890">
                </div>
            </div>
        `,
        width: '600px',
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'Crear',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#2486DB',
        preConfirm: () => {
            const placa = document.getElementById('swal-placa').value.trim().toUpperCase();
            const marca = document.getElementById('swal-marca').value.trim();
            const modelo = document.getElementById('swal-modelo').value.trim();
            const color = document.getElementById('swal-color').value.trim();
            const tipo = document.getElementById('swal-tipo').value;
            const propietario = document.getElementById('swal-propietario').value.trim();
            const telefono = document.getElementById('swal-telefono').value.trim();
            
            if (!placa || !marca || !modelo || !color) {
                Swal.showValidationMessage('Todos los campos marcados con * son requeridos');
                return false;
            }
            
            return { placa, marca, modelo, color, tipo, propietario, telefono };
        }
    });
    
    if (formValues) {
        await crearVehiculo(formValues);
    }
}

// ========== CREAR VEHÍCULO (API) ==========
async function crearVehiculo(datos) {
    try {
        const response = await fetch('/api/vehiculos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Error al crear vehículo');
        }
        
        Swal.fire({
            icon: 'success',
            title: '¡Éxito!',
            text: 'Vehículo creado correctamente',
            timer: 2000,
            showConfirmButton: false
        });
        
        cargarVehiculos();
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

// ========== EDITAR VEHÍCULO ==========
async function editarVehiculo(id) {
    try {
        // Cargar datos actuales
        const response = await fetch(`/api/vehiculos/${id}`);
        const vehiculo = await response.json();
        
        const { value: formValues } = await Swal.fire({
            title: `Editar Vehículo ${vehiculo.placa}`,
            html: `
                <div style="text-align: left;">
                    <div class="form-group">
                        <label>Placa *</label>
                        <input id="swal-placa" class="swal2-input" value="${vehiculo.placa}" disabled>
                        <small style="color: #999;">La placa no se puede cambiar</small>
                    </div>
                    <div class="form-group">
                        <label>Marca *</label>
                        <input id="swal-marca" class="swal2-input" value="${vehiculo.marca}">
                    </div>
                    <div class="form-group">
                        <label>Modelo *</label>
                        <input id="swal-modelo" class="swal2-input" value="${vehiculo.modelo}">
                    </div>
                    <div class="form-group">
                        <label>Color *</label>
                        <input id="swal-color" class="swal2-input" value="${vehiculo.color}">
                    </div>
                    <div class="form-group">
                        <label>Tipo *</label>
                        <select id="swal-tipo" class="swal2-input">
                            <option value="sedan" ${vehiculo.tipo === 'sedan' ? 'selected' : ''}>Sedán</option>
                            <option value="suv" ${vehiculo.tipo === 'suv' ? 'selected' : ''}>SUV</option>
                            <option value="pickup" ${vehiculo.tipo === 'pickup' ? 'selected' : ''}>Pickup</option>
                            <option value="moto" ${vehiculo.tipo === 'moto' ? 'selected' : ''}>Moto</option>
                            <option value="van" ${vehiculo.tipo === 'van' ? 'selected' : ''}>Van</option>
                            <option value="otro" ${vehiculo.tipo === 'otro' ? 'selected' : ''}>Otro</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Propietario (opcional)</label>
                        <input id="swal-propietario" class="swal2-input" value="${vehiculo.propietario || ''}">
                    </div>
                    <div class="form-group">
                        <label>Teléfono (opcional)</label>
                        <input id="swal-telefono" class="swal2-input" value="${vehiculo.telefono || ''}">
                    </div>
                </div>
            `,
            width: '600px',
            focusConfirm: false,
            showCancelButton: true,
            confirmButtonText: 'Guardar Cambios',
            cancelButtonText: 'Cancelar',
            confirmButtonColor: '#2486DB',
            preConfirm: () => {
                return {
                    marca: document.getElementById('swal-marca').value.trim(),
                    modelo: document.getElementById('swal-modelo').value.trim(),
                    color: document.getElementById('swal-color').value.trim(),
                    tipo: document.getElementById('swal-tipo').value,
                    propietario: document.getElementById('swal-propietario').value.trim(),
                    telefono: document.getElementById('swal-telefono').value.trim()
                };
            }
        });
        
        if (formValues) {
            await actualizarVehiculo(id, formValues);
        }
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// ========== ACTUALIZAR VEHÍCULO (API) ==========
async function actualizarVehiculo(id, datos) {
    try {
        const response = await fetch(`/api/vehiculos/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Error al actualizar vehículo');
        }
        
        Swal.fire({
            icon: 'success',
            title: '¡Éxito!',
            text: 'Vehículo actualizado correctamente',
            timer: 2000,
            showConfirmButton: false
        });
        
        cargarVehiculos();
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}

// ========== CONFIRMAR ELIMINAR VEHÍCULO ==========
async function confirmarEliminarVehiculo(id) {
    try {
        // Cargar datos del vehículo
        const response = await fetch(`/api/vehiculos/${id}`);
        const vehiculo = await response.json();
        
        const result = await Swal.fire({
            title: '⚠️ ¿Estás seguro?',
            html: `
                <p>Estás a punto de eliminar el vehículo:</p>
                <h3 style="color: #dc3545; margin: 1rem 0;">${vehiculo.placa}</h3>
                <p>${vehiculo.marca} ${vehiculo.modelo}</p>
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
            cancelButtonColor: '#6c757d'
        });
        
        if (result.isConfirmed) {
            await eliminarVehiculo(id);
        }
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// ========== ELIMINAR VEHÍCULO (API) ==========
async function eliminarVehiculo(id) {
    try {
        Swal.fire({
            title: 'Eliminando...',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch(`/api/vehiculos/${id}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Error al eliminar vehículo');
        }
        
        Swal.fire({
            icon: 'success',
            title: '¡Eliminado!',
            text: result.mensaje,
            timer: 2000,
            showConfirmButton: false
        });
        
        cargarVehiculos();
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
        const response = await fetch('/api/vehiculos/estadisticas');
        const stats = await response.json();
        
        document.getElementById('stat-total').textContent = stats.total;
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// ========== UTILIDADES ==========
function capitalizarPrimeraLetra(texto) {
    return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function obtenerColorHex(nombreColor) {
    const colores = {
        'rojo': '#dc3545',
        'azul': '#007bff',
        'verde': '#28a745',
        'amarillo': '#ffc107',
        'negro': '#343a40',
        'blanco': '#f8f9fa',
        'gris': '#6c757d',
        'plata': '#adb5bd',
        'naranja': '#fd7e14',
        'morado': '#6f42c1'
    };
    
    return colores[nombreColor.toLowerCase()] || '#6c757d';
}
