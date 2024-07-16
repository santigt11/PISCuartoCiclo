
document.addEventListener('DOMContentLoaded', function () {
    const rungeKuttaForm = document.getElementById('rungeKuttaForm');
    const downloadReportBtn = document.getElementById('downloadReportBtn');

    rungeKuttaForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const formData = {
            estudiantes_inicial: parseInt(document.getElementById('estudiantes_inicial').value),
            año_inicio: parseInt(document.getElementById('año_inicio').value),
            año_fin: parseInt(document.getElementById('año_fin').value),
            opcion: document.getElementById('opcion').value
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
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    const ciclos = generateCycleLabels(data.años);
    const estudiantesPorCiclo = data.estudiantes.filter((_, index) => index % 2 !== 0);

    doc.setFontSize(18);
    doc.text('Informe de Simulación Runge-Kutta', 10, 10);
    doc.setFontSize(12);
    doc.text('Datos de Resultado', 10, 20);

    let y = 30;
    doc.autoTable({
        startY: y,
        head: [['Ciclo', 'Número de Estudiantes', 'Nuevos Ingresos', 'Desertores']],
        body: ciclos.map((ciclo, index) => [
            ciclo,
            formatNumber(estudiantesPorCiclo[index]),
            formatNumber(data.nuevos_ingresos[index]),
            formatNumber(data.desertores[index])
        ]),
    });

    y = doc.lastAutoTable.finalY + 10;
    doc.text('Gráfico de Resultados', 10, y);
    y += 10;

    const chartData = {
        labels: ciclos,
        datasets: [{
            label: 'Número de Estudiantes',
            data: estudiantesPorCiclo,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
            fill: false
        }, {
            label: 'Desertores',
            data: data.desertores,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1,
            fill: false
        }, {
            label: 'Nuevos Ingresos',
            data: data.nuevos_ingresos,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            fill: false
        }]
    };

    const canvas = document.createElement('canvas');
    canvas.width = 800;
    canvas.height = 400;
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: false,
            maintainAspectRatio: false,
            scales: {
                x: { display: true },
                y: { display: true }
            }
        }
    });

    setTimeout(() => {
        const imgData = canvas.toDataURL('image/png');
        doc.addImage(imgData, 'PNG', 10, y, 180, 80);

        doc.save('runge_kutta_report.pdf');
    }, 1000);
}

function formatNumber(num) {
    return new Intl.NumberFormat('es-PE').format(num);
}