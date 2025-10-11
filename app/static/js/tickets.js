// tickets.js - Gestión de tickets activos

let todosLosTickets = [];
let ticketsOriginales = [];
let filtroActual = 'todos';

document.addEventListener('DOMContentLoaded', () => {
    cargarTickets();
    
    // Auto-refresh cada 30 segundos
    setInterval(() => {
        cargarTickets();
    }, 30000);
});

// ========== CARGAR TICKETS ==========
async function cargarTickets() {
    try {
        const response = await fetch('/api/tickets/activos');
        
        if (!response.ok) {
            throw new Error('Error al cargar tickets');
        }
        
        const tickets = await response.json();
        ticketsOriginales = tickets;
        todosLosTickets = tickets;
        
        // Actualizar estadísticas
        actualizarEstadisticas(tickets);
        
        // Aplicar filtros actuales
        aplicarFiltros();
        
    } catch (error) {
        console.error('Error:', error);
        const tbody = document.getElementById('tbody-tickets');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="8" class="no-data">Error al cargar tickets</td></tr>';
        }
    }
}

// ========== ACTUALIZAR ESTADÍSTICAS ==========
function actualizarEstadisticas(tickets) {
    // Total de tickets
    const totalElement = document.getElementById('stat-total-tickets');
    if (totalElement) {
        totalElement.textContent = tickets.length;
    }
    
    // Calcular tiempo promedio
    let totalMinutos = 0;
    let ticketsConTiempo = 0;
    
    tickets.forEach(ticket => {
        if (ticket.tiempo_transcurrido) {
            // Convertir a string si es necesario
            const tiempoStr = typeof ticket.tiempo_transcurrido === 'string' 
                ? ticket.tiempo_transcurrido 
                : (ticket.tiempo_transcurrido.texto || '0h 0m');
            
            const partes = tiempoStr.match(/(\d+)h (\d+)m/);
            if (partes) {
                const horas = parseInt(partes[1]);
                const minutos = parseInt(partes[2]);
                totalMinutos += (horas * 60) + minutos;
                ticketsConTiempo++;
            }
        }
    });
    
    const promedioMinutos = ticketsConTiempo > 0 ? Math.floor(totalMinutos / ticketsConTiempo) : 0;
    const promedioHoras = Math.floor(promedioMinutos / 60);
    const promedioMins = promedioMinutos % 60;
    
    const tiempoPromedioElement = document.getElementById('stat-tiempo-promedio');
    if (tiempoPromedioElement) {
        tiempoPromedioElement.textContent = `${promedioHoras}h ${promedioMins}m`;
    }
    
    // Calcular porcentaje de espacios usados
    const espaciosUsadosElement = document.getElementById('stat-espacios-usados');
    if (espaciosUsadosElement) {
        fetch('/api/espacios/estadisticas')
            .then(res => res.json())
            .then(stats => {
                const porcentaje = stats.total > 0 
                    ? Math.round((tickets.length / stats.total) * 100)
                    : 0;
                espaciosUsadosElement.textContent = `${porcentaje}%`;
            })
            .catch(() => {
                espaciosUsadosElement.textContent = '0%';
            });
    }
}

// ========== FILTRAR TICKETS ==========
function filtrarTickets(tipo, btn) {
    // Actualizar botón activo
    document.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    filtroActual = tipo;
    aplicarFiltros();
}

// ========== BUSCAR POR PLACA ==========
function buscarPorPlaca(texto) {
    aplicarFiltros(texto);
}

// ========== APLICAR FILTROS ==========
function aplicarFiltros(textoBusqueda = '') {
    let ticketsFiltrados = ticketsOriginales;
    
    // Filtro por tipo
    if (filtroActual !== 'todos') {
        if (filtroActual === 'alerta') {
            // Filtrar tickets con más de 3 horas
            ticketsFiltrados = ticketsFiltrados.filter(ticket => {
                if (ticket.tiempo_transcurrido) {
                    const tiempoStr = typeof ticket.tiempo_transcurrido === 'string' 
                        ? ticket.tiempo_transcurrido 
                        : (ticket.tiempo_transcurrido.texto || '0h 0m');
                    
                    const partes = tiempoStr.match(/(\d+)h/);
                    if (partes) {
                        const horas = parseInt(partes[1]);
                        return horas >= 3;
                    }
                }
                return false;
            });
        } else {
            ticketsFiltrados = ticketsFiltrados.filter(t => t.tipo_vehiculo === filtroActual);
        }
    }
    
    // Filtro por búsqueda
    if (textoBusqueda.trim()) {
        const busqueda = textoBusqueda.trim().toLowerCase();
        ticketsFiltrados = ticketsFiltrados.filter(t => 
            t.placa.toLowerCase().includes(busqueda)
        );
    }
    
    // Mostrar tickets filtrados
    mostrarTickets(ticketsFiltrados);
}

// ========== MOSTRAR TICKETS ==========
function mostrarTickets(tickets) {
    const tbody = document.getElementById('tbody-tickets');
    
    if (!tbody) return;
    
    if (tickets.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="no-data">No se encontraron tickets</td></tr>';
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
    
    // Formatear fecha de entrada
    const fechaEntrada = new Date(ticket.fecha_entrada);
    const horaEntrada = fechaEntrada.toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
    });
    const diaEntrada = fechaEntrada.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit'
    });
    
    // Iconos según tipo
    const iconosTipo = {
        'regular': '<i class="fas fa-car" style="color: #2486DB;"></i>',
        'moto': '<i class="fas fa-motorcycle" style="color: #28a745;"></i>',
        'discapacitado': '<i class="fas fa-wheelchair" style="color: #ffc107;"></i>'
    };
    
    // Obtener tiempo como string
    const tiempoStr = ticket.tiempo_transcurrido 
        ? (typeof ticket.tiempo_transcurrido === 'string' 
            ? ticket.tiempo_transcurrido 
            : (ticket.tiempo_transcurrido.texto || 'Calculando...'))
        : 'Calculando...';
    
    // Determinar clase de tiempo según duración
    let claseEstado = 'tiempo-ok';
    let iconoEstado = '<i class="fas fa-check-circle" style="color: #28a745;"></i>';
    
    const partes = tiempoStr.match(/(\d+)h/);
    if (partes) {
        const horas = parseInt(partes[1]);
        if (horas >= 3) {
            claseEstado = 'tiempo-alerta';
            iconoEstado = '<i class="fas fa-exclamation-triangle" style="color: #dc3545;"></i>';
        } else if (horas >= 2) {
            claseEstado = 'tiempo-warning';
            iconoEstado = '<i class="fas fa-exclamation-circle" style="color: #ffc107;"></i>';
        }
    }
    
    // Información del espacio
    const espacioInfo = ticket.espacio 
        ? `<strong>${ticket.espacio.numero}</strong><br><small>${ticket.espacio.seccion}</small>`
        : 'N/A';
    
    tr.innerHTML = `
        <td><strong>#${ticket.id}</strong></td>
        <td><strong style="font-size: 1.1rem;">${ticket.placa}</strong></td>
        <td>${espacioInfo}</td>
        <td>${iconosTipo[ticket.tipo_vehiculo] || ''} ${capitalizarPrimeraLetra(ticket.tipo_vehiculo)}</td>
        <td>
            ${horaEntrada}<br>
            <small style="color: #666;">${diaEntrada}</small>
        </td>
        <td class="${claseEstado}" style="font-weight: bold; font-size: 1.1rem;">
            ${tiempoStr}
        </td>
        <td>${iconoEstado}</td>
        <td>
            <button class="btn-icon btn-danger" onclick="procesarSalida(${ticket.id}, '${ticket.placa}')" title="Registrar Salida">
                <i class="fas fa-sign-out-alt"></i>
            </button>
        </td>
    `;
    
    return tr;
}

// ========== PROCESAR SALIDA ==========
async function procesarSalida(ticketId, placa) {
    try {
        // Mostrar modal con método de pago
        const { value: metodoPago } = await Swal.fire({
            title: `Salida del vehículo ${placa}`,
            html: `
                <div style="text-align: left; padding: 1rem;">
                    <p style="margin-bottom: 1rem; color: #666;">Selecciona el método de pago:</p>
                    
                    <div style="display: grid; gap: 1rem;">
                        <label style="display: flex; align-items: center; padding: 1rem; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; transition: all 0.3s ease;">
                            <input type="radio" name="metodo_pago" value="efectivo" checked style="margin-right: 1rem; width: 20px; height: 20px;">
                            <div style="flex: 1;">
                                <div style="font-weight: 600; font-size: 1.1rem;">
                                    <i class="fas fa-money-bill-wave" style="color: #28a745; margin-right: 0.5rem;"></i>
                                    Efectivo
                                </div>
                                <small style="color: #666;">Pago en efectivo</small>
                            </div>
                        </label>
                        
                        <label style="display: flex; align-items: center; padding: 1rem; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; transition: all 0.3s ease;">
                            <input type="radio" name="metodo_pago" value="tarjeta" style="margin-right: 1rem; width: 20px; height: 20px;">
                            <div style="flex: 1;">
                                <div style="font-weight: 600; font-size: 1.1rem;">
                                    <i class="fas fa-credit-card" style="color: #007bff; margin-right: 0.5rem;"></i>
                                    Tarjeta
                                </div>
                                <small style="color: #666;">Pago con tarjeta de crédito/débito</small>
                            </div>
                        </label>
                    </div>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: 'Procesar Salida',
            cancelButtonText: 'Cancelar',
            confirmButtonColor: '#2486DB',
            width: '500px',
            preConfirm: () => {
                const selected = document.querySelector('input[name="metodo_pago"]:checked');
                if (!selected) {
                    Swal.showValidationMessage('Debes seleccionar un método de pago');
                    return false;
                }
                return selected.value;
            }
        });
        
        if (!metodoPago) return;
        
        // Mostrar loading
        Swal.fire({
            title: 'Procesando salida...',
            text: 'Calculando monto y liberando espacio',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        // Procesar salida
        const response = await fetch(`/api/tickets/${ticketId}/salida`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                metodo_pago: metodoPago
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Error al procesar salida');
        }
        
        // Mostrar resultado exitoso
        Swal.fire({
            icon: 'success',
            title: '¡Salida Registrada!',
            html: `
                <div style="text-align: left; padding: 1rem;">
                    <p><strong>Placa:</strong> ${result.placa}</p>
                    <p><strong>Tiempo total:</strong> ${result.tiempo_estancia}</p>
                    <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); 
                                padding: 1.5rem; 
                                border-radius: 12px; 
                                margin: 1rem 0; 
                                text-align: center;
                                border-left: 4px solid #28a745;">
                        <p style="margin: 0; color: #666; font-size: 0.9rem;">Total a Pagar</p>
                        <h2 style="color: #2e7d32; margin: 0.5rem 0; font-size: 2.5rem;">
                            RD$${result.monto.toFixed(2)}
                        </h2>
                        <p style="margin: 0; color: #666; font-size: 0.9rem;">
                            <i class="fas ${metodoPago === 'efectivo' ? 'fa-money-bill-wave' : 'fa-credit-card'}"></i>
                            ${metodoPago === 'efectivo' ? 'Efectivo' : 'Tarjeta'}
                        </p>
                    </div>
                    <p style="text-align: center; color: #28a745; font-weight: 600;">
                        <i class="fas fa-check-circle"></i> Espacio ${result.espacio_numero} liberado
                    </p>
                </div>
            `,
            confirmButtonText: 'Aceptar',
            confirmButtonColor: '#28a745',
            width: '500px'
        });
        
        // Recargar tickets
        cargarTickets();
        
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




