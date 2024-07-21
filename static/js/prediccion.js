
document.addEventListener('DOMContentLoaded', function () {
    const rungeKuttaForm = document.getElementById('rungeKuttaForm');
    const downloadReportBtn = document.getElementById('downloadReportBtn');

    rungeKuttaForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const formData = {
            estudiantes_inicial: parseInt(document.getElementById('estudiantes_inicial').value),
            año_inicio: parseInt(document.getElementById('año_inicio').value),
            año_fin: parseInt(document.getElementById('año_fin').value),
            opcion: document.getElementById('opcion').value,
            factor: document.getElementById('factor').value
        };

        fetch('/calculate_rungeKutta', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            generateChart(data);
            downloadReportBtn.style.display = 'block';
            downloadReportBtn.addEventListener('click', function () {
                generateAndDownloadReport(data);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});

function generateChart(data) {
    const ctx = document.getElementById('myChart').getContext('2d');

    const ciclos = generateCycleLabels(data.años);

    // Calculamos todos los puntos para cada etapa del ciclo
    const allPoints = [];
    for (let i = 0; i < data.estudiantes.length; i += 2) {
        const inicioPeríodo = data.estudiantes[i];
        const despuésIngresos = inicioPeríodo + data.nuevos_ingresos[i/2];
        const despuésDeserciones = despuésIngresos - data.desertores[i/2];
        const finPeríodo = despuésDeserciones; // Este es el valor correcto para fin del período

        allPoints.push(inicioPeríodo);
        allPoints.push(despuésIngresos);
        allPoints.push(despuésDeserciones);
        allPoints.push(finPeríodo);
    }

    const chartData = {
        labels: ciclos.flatMap(ciclo => [
            ciclo + ' Inicio',
            ciclo + ' Ingresos',
            ciclo + ' Desertores',
            ciclo + ' Fin'
        ]),
        datasets: [{
            label: 'Número de Estudiantes',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            data: allPoints,
            pointRadius: 5,
            pointHoverRadius: 7
        }]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Ciclo'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Número de Estudiantes'
                },
                beginAtZero: false
            }
        },
        plugins: {
            legend: {
                display: true
            },
            title: {
                display: true,
                text: `Simulación de Estudiantes (${data.años[0]}-${data.años[data.años.length - 1]})`,
                font: {
                    size: 16
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += new Intl.NumberFormat('es-PE').format(context.parsed.y);
                        }
                        return label;
                    }
                }
            }
        }
    };

    const myChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: chartOptions
    });

    // Añadir etiquetas de datos
    myChart.options.plugins.annotation = {
        annotations: allPoints.map((value, index) => ({
            type: 'label',
            xValue: index,
            yValue: value,
            content: value.toString(),
            position: 'top'
        }))
    };

    myChart.update();
}
function generateCycleLabels(años) {
    return años.flatMap(año => [`${año}-1`, `${año}-2`]);
}

function generateAndDownloadReport(data) {
    const ciclos = generateCycleLabels(data.años);
    const estudiantesPorCiclo = data.estudiantes.filter((_, index) => index % 2 !== 0);

    const reportContent =`
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Informe de Simulación Runge-Kutta</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .container { max-width: 800px; margin: 20px auto; padding: 20px; border: 1px solid #ccc; }
                h2 { color: #007bff; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Inform de predicción de la deserción</h2>
                <h3>Datos de Resultado</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Ciclo</th>
                            <th>Número de Estudiantes</th>
                            <th>Nuevos Ingresos</th>
                            <th>Desertores</th>
                        </tr>
                    </thead>
                     <tbody>
                        ${ciclos.map((ciclo, index) => `
                         <tr>
                             <td>${ciclo}</td>
                            <td>${formatNumber(estudiantesPorCiclo[index])}</td>
                             <td>${formatNumber(data.nuevos_ingresos[index])}</td>
                            <td>${formatNumber(data.desertores[index])}</td>
                         </tr>
                        `).join('')}
                    </tbody>
                </table>
                <h3>Gráfico de Resultados</h3>
                <canvas id="reportChart"></canvas>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
             <script>
            document.addEventListener('DOMContentLoaded', function () {
                const ctx = document.getElementById('reportChart').getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: ${JSON.stringify(ciclos)},
                        datasets: [{
                            label: 'Número de Estudiantes',
                            data: ${JSON.stringify(estudiantesPorCiclo)},
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1,
                            fill: false
                        }, {
                            label: 'Desertores',
                            data: ${JSON.stringify(data.desertores)},
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1,
                            fill: false
                        }, {
                            label: 'Nuevos Ingresos',
                            data: ${JSON.stringify(data.nuevos_ingresos)},
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1,
                            fill: false
                        }]
                    },
        </body>
        </html>
    `;

    const blob = new Blob([reportContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'runge_kutta_report.html';
    a.click();

    URL.revokeObjectURL(url);
}

function formatNumber(num) {
    return new Intl.NumberFormat('es-PE').format(num);
}