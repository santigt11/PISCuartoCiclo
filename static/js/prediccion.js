document.addEventListener('DOMContentLoaded', function () {
    const rungeKuttaForm = document.getElementById('rungeKuttaForm');
    const downloadReportBtn = document.getElementById('downloadReportBtn');

    rungeKuttaForm.addEventListener('submit', function (event) {
        event.preventDefault();

        // Primero, obtenemos el número de estudiantes de la base de datos
        fetch('/obtener_estudiantes')
            .then(response => response.json())
            .then(data => {
                const estudiantes_inicial = data.total;

                // Luego, enviamos todos los datos para el cálculo
                const formData = {
                    estudiantes_inicial: estudiantes_inicial,
                    año_inicio: parseInt(document.getElementById('año_inicio').value),
                    año_fin: parseInt(document.getElementById('año_fin').value),
                    opcion: document.getElementById('opcion').value
                };

                return fetch('/calculate_rungeKutta', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
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
    doc.setFont('Helvetica','bold');
    var text = 'Informe de Simulación Runge-Kutta';
    var pageWidth = doc.internal.pageSize.getWidth();
    var textWidth = doc.getStringUnitWidth(text) * doc.internal.getFontSize() / doc.internal.scaleFactor;
    var textX = (pageWidth - textWidth) / 2;

    doc.setFontSize(18);
    doc.text(text, textX, 15);
   
    doc.setFontSize(15);
    doc.text('Resultados', 10, 25);

    doc.setFont('helvetica', 'normal');

    let x = 35;
    for (let i = 1; i < data.estudiantes.length; i += 2) {
        const año = data.años[0] + Math.floor((i - 1) / 4);
        const ciclo = (i - 1) % 4 >= 2 ? 2 : 1;

        const inicio_ciclo = data.estudiantes[i - 1];
        const ingresados = data.nuevos_ingresos[Math.floor(i / 2)];
        const desertados = data.desertores[Math.floor(i / 2)];
        const fin_ciclo = data.estudiantes[i + 1];

        const tableData = [
            ['Inicio del Período', formatNumber(inicio_ciclo)],
            ['Nuevos Ingresos', formatNumber(ingresados)],
            ['Desertores', formatNumber(desertados)],
            ['Fin del Período', formatNumber(fin_ciclo)]
        ];

        doc.setFontSize(13);
        doc.text(`El ciclo ${ciclo} del año ${año} tiene los siguientes resultados: `, 10, x);
        x += 10;
        
        doc.autoTable({
            startY: x,
            head: [['Concepto', 'Valor']],
            body: tableData,
            theme: 'grid',
            styles: { cellPadding: 2, fontSize: 12 },
        });

        x = doc.lastAutoTable.finalY + 10; // Actualiza la posición y para la próxima tabla
    }
    
    doc.autoTable({
        startY: x,
        head: [['Ciclo', 'Número de Estudiantes', 'Nuevos Ingresos', 'Desertores']],
        body: ciclos.map((ciclo, index) => [
            ciclo,
            formatNumber(estudiantesPorCiclo[index]),
            formatNumber(data.nuevos_ingresos[index]),
            formatNumber(data.desertores[index])
        ]),
    });

    x = doc.lastAutoTable.finalY + 10;
    doc.text('Gráfico de Resultados', 10, x);
    x += 10;

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
        doc.addImage(imgData, 'PNG', 10, x, 180, 80);

        doc.save('runge_kutta_report.pdf');
    }, 1000);
}

function formatNumber(num) {
    return new Intl.NumberFormat('es-PE').format(num);
}