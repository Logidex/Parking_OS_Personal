// reportes.js - Gestión de reportes

document.addEventListener('DOMContentLoaded', () => {
    // Event listeners para botones de reportes
    document.getElementById('btn-reporte-ingresos')?.addEventListener('click', generarReporteIngresos);
    document.getElementById('btn-reporte-ocupacion')?.addEventListener('click', generarReporteOcupacion);
    document.getElementById('btn-reporte-vehiculos')?.addEventListener('click', generarReporteVehiculos);
    document.getElementById('btn-reporte-metodos-pago')?.addEventListener('click', generarReporteMetodosPago);
});

// ========== REPORTE DE INGRESOS ==========
async function generarReporteIngresos() {
    try {
        Swal.fire({
            title: 'Generando reporte...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch('/api/reportes/ingresos-periodo');
        
        if (!response.ok) {
            throw new Error('Error al generar reporte');
        }
        
        const data = await response.json();
        
        Swal.fire({
            title: '📊 Reporte de Ingresos',
            html: `
                <div style="text-align: left;">
                    <h3 style="color: #2486DB; margin-bottom: 1rem;">💰 Ingresos por Período</h3>
                    
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <h4 style="margin: 0 0 0.5rem 0;">Hoy</h4>
                        <p style="margin: 0.25rem 0;"><strong>Ingresos:</strong> ${data.hoy.ingresos_formateado}</p>
                        <p style="margin: 0.25rem 0;"><strong>Transacciones:</strong> ${data.hoy.transacciones}</p>
                        <p style="margin: 0.25rem 0;"><strong>Promedio:</strong> ${data.hoy.promedio_formateado}</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <h4 style="margin: 0 0 0.5rem 0;">Esta Semana</h4>
                        <p style="margin: 0.25rem 0;"><strong>Ingresos:</strong> ${data.semana.ingresos_formateado}</p>
                        <p style="margin: 0.25rem 0;"><strong>Transacciones:</strong> ${data.semana.transacciones}</p>
                        <p style="margin: 0.25rem 0;"><strong>Promedio:</strong> ${data.semana.promedio_formateado}</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px;">
                        <h4 style="margin: 0 0 0.5rem 0;">Este Mes</h4>
                        <p style="margin: 0.25rem 0;"><strong>Ingresos:</strong> ${data.mes.ingresos_formateado}</p>
                        <p style="margin: 0.25rem 0;"><strong>Transacciones:</strong> ${data.mes.transacciones}</p>
                        <p style="margin: 0.25rem 0;"><strong>Promedio:</strong> ${data.mes.promedio_formateado}</p>
                    </div>
                </div>
            `,
            width: '600px',
            confirmButtonText: 'Cerrar',
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

// ========== REPORTE DE OCUPACIÓN ==========
async function generarReporteOcupacion() {
    try {
        Swal.fire({
            title: 'Generando reporte...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch('/api/reportes/ocupacion-espacios');
        
        if (!response.ok) {
            throw new Error('Error al generar reporte');
        }
        
        const data = await response.json();
        
        Swal.fire({
            title: '📈 Reporte de Ocupación',
            html: `
                <div style="text-align: left;">
                    <h3 style="color: #2486DB; margin-bottom: 1rem;">🅿️ Ocupación de Espacios</h3>
                    
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <h4 style="margin: 0 0 0.5rem 0;">Estado Actual</h4>
                        <p style="margin: 0.25rem 0;"><strong>Total espacios:</strong> ${data.ocupacion_actual.total}</p>
                        <p style="margin: 0.25rem 0;"><strong>Ocupados:</strong> ${data.ocupacion_actual.ocupados}</p>
                        <p style="margin: 0.25rem 0;"><strong>Disponibles:</strong> ${data.ocupacion_actual.disponibles}</p>
                        <p style="margin: 0.25rem 0;"><strong>Ocupación:</strong> ${data.ocupacion_actual.porcentaje_ocupacion}%</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <h4 style="margin: 0 0 0.5rem 0;">Uso Histórico por Tipo</h4>
                        <p style="margin: 0.25rem 0;">🚗 <strong>Regular:</strong> ${data.uso_por_tipo.regular.cantidad} (${data.uso_por_tipo.regular.porcentaje}%)</p>
                        <p style="margin: 0.25rem 0;">🏍️ <strong>Moto:</strong> ${data.uso_por_tipo.moto.cantidad} (${data.uso_por_tipo.moto.porcentaje}%)</p>
                        <p style="margin: 0.25rem 0;">♿ <strong>Discapacitado:</strong> ${data.uso_por_tipo.discapacitado.cantidad} (${data.uso_por_tipo.discapacitado.porcentaje}%)</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px;">
                        <h4 style="margin: 0 0 0.5rem 0;">Estadísticas Generales</h4>
                        <p style="margin: 0.25rem 0;"><strong>Tiempo promedio de estancia:</strong> ${data.tiempo_promedio_estancia} horas</p>
                        <p style="margin: 0.25rem 0;"><strong>Total de usos:</strong> ${data.total_usos_historico}</p>
                    </div>
                </div>
            `,
            width: '600px',
            confirmButtonText: 'Cerrar',
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

// ========== REPORTE DE VEHÍCULOS FRECUENTES ==========
async function generarReporteVehiculos() {
    try {
        Swal.fire({
            title: 'Generando reporte...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch('/api/reportes/vehiculos-frecuentes');
        
        if (!response.ok) {
            throw new Error('Error al generar reporte');
        }
        
        const vehiculos = await response.json();
        
        let tablaHTML = `
            <table style="width: 100%; border-collapse: collapse; margin-top: 1rem;">
                <thead>
                    <tr style="background: #f8f9fa;">
                        <th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid #dee2e6;">#</th>
                        <th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid #dee2e6;">Placa</th>
                        <th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid #dee2e6;">Visitas</th>
                        <th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid #dee2e6;">Total</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        vehiculos.forEach((vehiculo, index) => {
            tablaHTML += `
                <tr style="border-bottom: 1px solid #dee2e6;">
                    <td style="padding: 0.75rem;">${index + 1}</td>
                    <td style="padding: 0.75rem;"><strong>${vehiculo.placa}</strong><br></td>
                    <td style="padding: 0.75rem;">${vehiculo.visitas}</td>
                    <td style="padding: 0.75rem;"><strong>${vehiculo.total_gastado_formateado}</strong></td>
                </tr>
            `;
        });
        
        tablaHTML += '</tbody></table>';
        
        Swal.fire({
            title: '🚗 Vehículos Frecuentes',
            html: `
                <div style="text-align: left;">
                    <p style="color: #666; margin-bottom: 1rem;">Top 10 vehículos con mayor frecuencia de uso</p>
                    ${tablaHTML}
                </div>
            `,
            width: '700px',
            confirmButtonText: 'Cerrar',
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

// ========== REPORTE DE MÉTODOS DE PAGO ==========
async function generarReporteMetodosPago() {
    try {
        Swal.fire({
            title: 'Generando reporte...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch('/api/reportes/metodos-pago');
        
        if (!response.ok) {
            throw new Error('Error al generar reporte');
        }
        
        const data = await response.json();
        
        Swal.fire({
            title: '💳 Reporte de Métodos de Pago',
            html: `
                <div style="text-align: left;">
                    <h3 style="color: #2486DB; margin-bottom: 1rem;">💰 Métodos de Pago</h3>
                    
                    <div style="background: #d4edda; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #28a745;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #155724;">💵 Efectivo</h4>
                        <p style="margin: 0.25rem 0;"><strong>Monto total:</strong> ${data.efectivo.monto_formateado}</p>
                        <p style="margin: 0.25rem 0;"><strong>Transacciones:</strong> ${data.efectivo.transacciones} (${data.efectivo.porcentaje}%)</p>
                    </div>
                    
                    <div style="background: #cfe2ff; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #0d6efd;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #084298;">💳 Tarjeta</h4>
                        <p style="margin: 0.25rem 0;"><strong>Monto total:</strong> ${data.tarjeta.monto_formateado}</p>
                        <p style="margin: 0.25rem 0;"><strong>Transacciones:</strong> ${data.tarjeta.transacciones} (${data.tarjeta.porcentaje}%)</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border: 2px solid #2486DB;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #2486DB;">📊 Total General</h4>
                        <p style="margin: 0.25rem 0; font-size: 1.2rem;"><strong>Monto:</strong> ${data.total.monto_formateado}</p>
                        <p style="margin: 0.25rem 0;"><strong>Transacciones:</strong> ${data.total.transacciones}</p>
                    </div>
                </div>
            `,
            width: '600px',
            confirmButtonText: 'Cerrar',
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
