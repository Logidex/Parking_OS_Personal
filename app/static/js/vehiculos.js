// vehiculos.js - Ingreso rápido de vehículos

// Variable global para almacenar espacios por tipo
let espaciosPorTipo = {};

document.addEventListener('DOMContentLoaded', () => {
    cargarVehiculos();
    cargarDisponibilidad();
    
    // Auto-convertir placa a mayúsculas mientras escribes
    const inputPlaca = document.getElementById('input-placa');
    if (inputPlaca) {
        inputPlaca.addEventListener('input', (e) => {
            e.target.value = e.target.value.toUpperCase();
        });
    }
    
    // Event listener para formulario
    document.getElementById('form-ingreso-rapido')?.addEventListener('submit', ingresarVehiculoRapido);
});

// ========== INGRESAR VEHÍCULO RÁPIDO ==========
async function ingresarVehiculoRapido(e) {
    e.preventDefault();
    
    const placa = document.getElementById('input-placa').value.trim().toUpperCase();
    const tipoVehiculo = document.getElementById('select-tipo-vehiculo').value;
    
    if (!placa) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Debes ingresar una placa'
        });
        return;
    }
    
    try {
        // Mostrar loading
        Swal.fire({
            title: 'Asignando espacio...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch('/api/tickets/ingresar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                placa: placa,
                tipo_vehiculo: tipoVehiculo
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Error al ingresar vehículo');
        }
        
        // Éxito
        Swal.fire({
            icon: 'success',
            title: '¡Vehículo Ingresado!',
            html: `
                <div style="text-align: center;">
                    <h2 style="color: #2486DB; margin: 1rem 0; font-size: 3rem;">${result.espacio.numero}</h2>
                    <p><strong>Placa:</strong> ${placa}</p>
                    <p><strong>Tipo:</strong> ${capitalizarPrimeraLetra(tipoVehiculo)}</p>
                    <p><strong>Sección:</strong> ${result.espacio.seccion}</p>
                    <p style="margin-top: 1rem; color: #666;">
                        <i class="fas fa-ticket-alt"></i> Ticket #${result.ticket.id}
                    </p>
                </div>
            `,
            confirmButtonText: 'Aceptar',
            confirmButtonColor: '#2486DB'
        });
        
        // Limpiar formulario
        document.getElementById('input-placa').value = '';
        document.getElementById('select-tipo-vehiculo').value = 'regular';
        
        // Focus en input
        document.getElementById('input-placa').focus();
        
        // Actualizar disponibilidad
        cargarDisponibilidad();
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}

// ========== CARGAR DISPONIBILIDAD ==========
async function cargarDisponibilidad() {
    try {
        const response = await fetch('/api/espacios/disponibles-por-tipo');
        
        if (response.ok) {
            espaciosPorTipo = await response.json();
            actualizarDisponibilidad();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// ========== ACTUALIZAR DISPONIBILIDAD ==========
function actualizarDisponibilidad() {
    // Actualizar cada tipo de espacio
    const regularElement = document.getElementById('disponibles-regular');
    const motoElement = document.getElementById('disponibles-moto');
    const discapacitadoElement = document.getElementById('disponibles-discapacitado');
    
    if (regularElement) {
        regularElement.textContent = espaciosPorTipo.regular || 0;
    }
    if (motoElement) {
        motoElement.textContent = espaciosPorTipo.moto || 0;
    }
    if (discapacitadoElement) {
        discapacitadoElement.textContent = espaciosPorTipo.discapacitado || 0;
    }
}

// ========== CARGAR VEHÍCULOS ==========
async function cargarVehiculos() {
    try {
        const response = await fetch('/api/vehiculos');
        
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
    
    if (!tbody) return;
    
    if (vehiculos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="no-data">No hay vehículos registrados</td></tr>';
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
    
    tr.innerHTML = `
        <td><strong>${vehiculo.placa}</strong></td>
        <td>${vehiculo.marca || 'N/A'}</td>
        <td>${vehiculo.modelo || 'N/A'}</td>
        <td>
            <button class="btn-icon btn-success" onclick="ingresarVehiculo('${vehiculo.placa}')" title="Ingresar al estacionamiento">
                <i class="fas fa-sign-in-alt"></i>
            </button>
        </td>
    `;
    
    return tr;
}

// ========== INGRESAR VEHÍCULO DESDE LA TABLA ==========
async function ingresarVehiculo(placa) {
    try {
        // Mostrar modal para seleccionar tipo de vehículo
        const { value: formValues } = await Swal.fire({
            title: `Ingresar vehículo ${placa}`,
            html: `
                <div style="text-align: left;">
                    <label for="swal-tipo" style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Tipo de vehículo:</label>
                    <select id="swal-tipo" class="swal2-input" style="width: 100%; margin: 0;">
                        <option value="regular">🚗 Regular</option>
                        <option value="moto">🏍️ Moto</option>
                        <option value="discapacitado">♿ Discapacitado</option>
                    </select>
                    
                    <div id="swal-espacios-info" style="margin-top: 1rem; padding: 0.75rem; background: #e3f2fd; border-radius: 8px; text-align: center; transition: all 0.3s ease;">
                        <strong>Espacios disponibles: <span id="swal-espacios-count">0</span></strong>
                    </div>
                </div>
            `,
            focusConfirm: false,
            showCancelButton: true,
            confirmButtonText: 'Ingresar',
            cancelButtonText: 'Cancelar',
            confirmButtonColor: '#2486DB',
            width: '500px',
            didOpen: () => {
                const tipoSelect = document.getElementById('swal-tipo');
                const espaciosCount = document.getElementById('swal-espacios-count');
                const infoDiv = document.getElementById('swal-espacios-info');
                
                // Actualizar espacios al cambiar tipo
                const actualizarEspaciosSwal = () => {
                    const tipo = tipoSelect.value;
                    const disponibles = espaciosPorTipo[tipo] || 0;
                    espaciosCount.textContent = disponibles;
                    
                    // Cambiar color según disponibilidad
                    if (disponibles === 0) {
                        infoDiv.style.background = '#ffebee';
                        infoDiv.style.color = '#c62828';
                    } else if (disponibles <= 5) {
                        infoDiv.style.background = '#fff3e0';
                        infoDiv.style.color = '#e65100';
                    } else {
                        infoDiv.style.background = '#e3f2fd';
                        infoDiv.style.color = '#1565c0';
                    }
                };
                
                tipoSelect.addEventListener('change', actualizarEspaciosSwal);
                actualizarEspaciosSwal(); // Inicializar
            },
            preConfirm: () => {
                const tipo = document.getElementById('swal-tipo').value;
                const disponibles = espaciosPorTipo[tipo] || 0;
                
                if (disponibles === 0) {
                    Swal.showValidationMessage(`No hay espacios disponibles para vehículos tipo ${tipo}`);
                    return false;
                }
                
                return { tipo_vehiculo: tipo };
            }
        });
        
        if (!formValues) return;
        
        // Mostrar loading
        Swal.fire({
            title: 'Ingresando vehículo...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        // Ingresar vehículo
        const response = await fetch('/api/tickets/ingresar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                placa: placa,
                tipo_vehiculo: formValues.tipo_vehiculo
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Error al ingresar vehículo');
        }
        
        // Mostrar éxito
        Swal.fire({
            icon: 'success',
            title: '¡Vehículo Ingresado!',
            html: `
                <div style="text-align: left; padding: 1rem;">
                    <p><strong>Placa:</strong> ${result.ticket.placa}</p>
                    <p><strong>Tipo:</strong> ${capitalizarPrimeraLetra(result.espacio.tipo)}</p>
                    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                                padding: 1.5rem; 
                                border-radius: 12px; 
                                margin: 1rem 0; 
                                text-align: center;
                                border-left: 4px solid #2486DB;">
                        <h2 style="color: #1565c0; margin: 0; font-size: 2.5rem;">
                            ${result.espacio.numero}
                        </h2>
                        <p style="margin: 0.5rem 0 0 0; color: #666;">Espacio asignado</p>
                    </div>
                    <p style="text-align: center; color: #2486DB; font-weight: 600;">
                        <i class="fas fa-check-circle"></i> Ingreso registrado exitosamente
                    </p>
                </div>
            `,
            confirmButtonText: 'Aceptar',
            confirmButtonColor: '#2486DB',
            width: '500px'
        });
        
        // Recargar espacios disponibles
        cargarDisponibilidad();
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}

// ========== MODAL PARA AGREGAR VEHÍCULO ==========
async function mostrarModalAgregarVehiculo() {
    const { value: formValues } = await Swal.fire({
        title: 'Agregar Vehículo',
        html: `
            <div style="text-align: left;">
                <label for="swal-placa" style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Placa: *</label>
                <input id="swal-placa" 
                       class="swal2-input" 
                       placeholder="Ej: ABC1234" 
                       style="text-transform: uppercase; width: 100%; margin: 0 0 1rem 0;">
                
                <label for="swal-marca" style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Marca: (opcional)</label>
                <input id="swal-marca" 
                       class="swal2-input" 
                       placeholder="Ej: Toyota" 
                       style="width: 100%; margin: 0 0 1rem 0;">
                
                <label for="swal-modelo" style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Modelo: (opcional)</label>
                <input id="swal-modelo" 
                       class="swal2-input" 
                       placeholder="Ej: Corolla 2020" 
                       style="width: 100%; margin: 0;">
            </div>
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'Guardar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#2486DB',
        width: '500px',
        preConfirm: () => {
            const placa = document.getElementById('swal-placa').value.trim().toUpperCase();
            
            if (!placa) {
                Swal.showValidationMessage('La placa es requerida');
                return false;
            }
            
            // Validación básica de formato de placa
            if (placa.length < 3) {
                Swal.showValidationMessage('La placa debe tener al menos 3 caracteres');
                return false;
            }
            
            return {
                placa: placa,
                marca: document.getElementById('swal-marca').value.trim() || null,
                modelo: document.getElementById('swal-modelo').value.trim() || null
            };
        }
    });
    
    if (formValues) {
        await agregarVehiculo(formValues);
    }
}

// ========== AGREGAR VEHÍCULO ==========
async function agregarVehiculo(datos) {
    try {
        Swal.fire({
            title: 'Guardando...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
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
            title: '¡Vehículo agregado!',
            html: `
                <p><strong>Placa:</strong> ${result.vehiculo.placa}</p>
                ${result.vehiculo.marca ? `<p><strong>Marca:</strong> ${result.vehiculo.marca}</p>` : ''}
                ${result.vehiculo.modelo ? `<p><strong>Modelo:</strong> ${result.vehiculo.modelo}</p>` : ''}
            `,
            confirmButtonColor: '#2486DB'
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

// ========== UTILIDADES ==========
function capitalizarPrimeraLetra(texto) {
    if (!texto) return '';
    return texto.charAt(0).toUpperCase() + texto.slice(1);
}



