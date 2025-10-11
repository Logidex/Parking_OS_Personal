// tickets.js - Gestión de tickets activos

document.addEventListener('DOMContentLoaded', () => {
    cargarTicketsActivos();
    
    // Auto-refrescar cada 30 segundos
    setInterval(cargarTicketsActivos, 30000);
});

// ========== CARGAR TICKETS ACTIVOS ==========
async function cargarTicketsActivos() {
    try {
        const response = await fetch('/api/tickets/activos');
        
        if (!response.ok) {
            throw new Error('Error al cargar tickets');
        }
        
        const tickets = await response.json();
        mostrarTickets(tickets);
        actualizarEstadisticas(tickets);
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudieron cargar los tickets'
        });
    }
}

// ========== MOSTRAR TICKETS EN LA TABLA ==========
function mostrarTickets(tickets) {
    const tbody = document.getElementById('tbody-tickets');
    
    if (tickets.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="no-data">No hay vehículos en el estacionamiento</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    
    tickets.forEach(ticket => {
        const row = crearFilaTicket(ticket);
        tbody.appendChild(row);
    });
}

// ========== CREAR FILA DE TICKET ==========
function crearFilaTicket(ticket) {
    const tr = document.createElement('tr');
    
    // Usar tiempo transcurrido calculado por el backend
    const tiempoTranscurrido = ticket.tiempo_transcurrido 
        ? ticket.tiempo_transcurrido.texto 
        : 'Calculando...';
    
    // Formatear hora de entrada
    const entrada = new Date(ticket.fecha_entrada);
    const horaEntrada = entrada.toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
    
    // Icono según tipo
    const iconosTipo = {
        'regular': 'fa-car',
        'moto': 'fa-motorcycle',
        'discapacitado': 'fa-wheelchair'
    };
    const icono = iconosTipo[ticket.tipo_vehiculo] || 'fa-car';
    
    tr.innerHTML = `
        <td><strong>#${ticket.id}</strong></td>
        <td><strong>${ticket.placa}</strong></td>
        <td>
            <span class="badge-espacio">${ticket.espacio ? ticket.espacio.numero : 'N/A'}</span>
        </td>
        <td>
            <i class="fas ${icono}"></i>
            ${capitalizarPrimeraLetra(ticket.tipo_vehiculo)}
        </td>
        <td>${horaEntrada}</td>
        <td><strong>${tiempoTranscurrido}</strong></td>
        <td>
            <button class="btn-icon btn-salida" onclick="registrarSalida(${ticket.id})" title="Registrar Salida">
                <i class="fas fa-sign-out-alt"></i> Salida
            </button>
        </td>
    `;
    
    return tr;
}

// ========== REGISTRAR SALIDA ==========
async function registrarSalida(ticketId) {
    try {
        // Paso 1: Confirmar que quiere registrar salida
        const confirmResult = await Swal.fire({
            title: '¿Registrar salida?',
            text: 'Se calculará el tiempo y el monto a cobrar',
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Sí, continuar',
            cancelButtonText: 'Cancelar',
            confirmButtonColor: '#2486DB'
        });
        
        if (!confirmResult.isConfirmed) {
            return;
        }
        
        // Paso 2: Pedir método de pago directamente
        const { value: metodoPago } = await Swal.fire({
            title: 'Método de Pago',
            html: `
                <div style="text-align: left; padding: 1rem;">
                    <p style="text-align: center; margin-bottom: 1.5rem; color: #666;">
                        Selecciona cómo realizará el pago el cliente
                    </p>
                    
                    <div style="display: flex; flex-direction: column; gap: 1rem;">
                        <label class="payment-option" style="display: flex; align-items: center; padding: 1rem; border: 2px solid #28a745; border-radius: 8px; cursor: pointer; background: #f8fff9;">
                            <input type="radio" name="metodo_pago" value="efectivo" checked style="margin-right: 1rem; width: 20px; height: 20px; cursor: pointer;">
                            <i class="fas fa-money-bill-wave" style="font-size: 1.8rem; margin-right: 1rem; color: #28a745;"></i>
                            <div>
                                <strong style="font-size: 1.1rem;">Efectivo</strong>
                                <br>
                                <small style="color: #666;">Pago en efectivo</small>
                            </div>
                        </label>
                        
                        <label class="payment-option" style="display: flex; align-items: center; padding: 1rem; border: 2px solid #ddd; border-radius: 8px; cursor: pointer; transition: all 0.3s;">
                            <input type="radio" name="metodo_pago" value="tarjeta" style="margin-right: 1rem; width: 20px; height: 20px; cursor: pointer;">
                            <i class="fas fa-credit-card" style="font-size: 1.8rem; margin-right: 1rem; color: #007bff;"></i>
                            <div>
                                <strong style="font-size: 1.1rem;">Tarjeta</strong>
                                <br>
                                <small style="color: #666;">Débito o crédito</small>
                            </div>
                        </label>
                    </div>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: 'Procesar Pago',
            cancelButtonText: 'Cancelar',
            confirmButtonColor: '#28a745',
            width: '500px',
            preConfirm: () => {
                const selected = document.querySelector('input[name="metodo_pago"]:checked');
                if (!selected) {
                    Swal.showValidationMessage('Debes seleccionar un método de pago');
                    return false;
                }
                return selected.value;
            },
            didOpen: () => {
                // Agregar efectos visuales a las opciones
                const labels = document.querySelectorAll('.payment-option');
                const radios = document.querySelectorAll('input[name="metodo_pago"]');
                
                radios.forEach((radio, index) => {
                    radio.addEventListener('change', () => {
                        labels.forEach(label => {
                            label.style.border = '2px solid #ddd';
                            label.style.background = 'white';
                        });
                        
                        if (radio.checked) {
                            labels[index].style.border = '2px solid #28a745';
                            labels[index].style.background = '#f8fff9';
                        }
                    });
                });
            }
        });
        
        if (!metodoPago) {
            return; // Usuario canceló
        }
        
        // Paso 3: Procesar la salida con el método de pago
        Swal.fire({
            title: 'Procesando pago...',
            text: 'Registrando salida y calculando monto',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const salidaResponse = await fetch(`/api/tickets/${ticketId}/salida`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                metodo_pago: metodoPago
            })
        });
        
        const result = await salidaResponse.json();
        
        if (!salidaResponse.ok) {
            throw new Error(result.error || 'Error al registrar salida');
        }
        
        // Paso 4: Mostrar resumen final
        const montoFormateado = result.monto_formateado || `RD$${result.monto.toFixed(2)}`;
        
        const metodosTexto = {
            'efectivo': '💵 Efectivo',
            'tarjeta': '💳 Tarjeta'
        };
        
        Swal.fire({
            icon: 'success',
            title: '¡Pago Confirmado!',
            html: `
                <div style="text-align: left; padding: 1rem;">
                    <div style="text-align: center; margin-bottom: 1.5rem;">
                        <i class="fas fa-check-circle" style="font-size: 3.5rem; color: #28a745;"></i>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <p style="margin: 0.5rem 0;"><strong>Placa:</strong> ${result.ticket.placa}</p>
                        <p style="margin: 0.5rem 0;"><strong>Tiempo:</strong> ${result.tiempo_estancia_horas} horas</p>
                        <p style="margin: 0.5rem 0;"><strong>Pago:</strong> ${metodosTexto[metodoPago]}</p>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); 
                                padding: 1.5rem; 
                                border-radius: 12px; 
                                margin: 1rem 0; 
                                border-left: 4px solid #28a745;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <h2 style="color: #155724; 
                                   margin: 0 0 0.5rem 0; 
                                   text-align: center; 
                                   font-size: 3rem;
                                   font-weight: bold;">
                            ${montoFormateado}
                        </h2>
                        <p style="text-align: center; 
                                  color: #155724; 
                                  margin: 0; 
                                  font-size: 1rem;
                                  font-weight: 600;">
                            ✓ Pago completado
                        </p>
                    </div>
                </div>
            `,
            confirmButtonText: 'Aceptar',
            confirmButtonColor: '#28a745',
            width: '500px'
        });
        
        // Recargar tickets
        cargarTicketsActivos();
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}

// ========== ACTUALIZAR ESTADÍSTICAS ==========
function actualizarEstadisticas(tickets) {
    document.getElementById('stat-total-tickets').textContent = tickets.length;
}

// ========== UTILIDADES ==========
function capitalizarPrimeraLetra(texto) {
    return texto.charAt(0).toUpperCase() + texto.slice(1);
}


