let predicciones = [];
let graficas = [];
let currentChart = null;

document.addEventListener('DOMContentLoaded', function () {
    const rungeKuttaForm = document.getElementById('rungeKuttaForm');
    const downloadReportBtn = document.getElementById('downloadReportBtn');
    const newPredictionBtn = document.getElementById('newPredictionBtn');
    const graphContainer = document.getElementById('graph-container');

    rungeKuttaForm.addEventListener('submit', handleFormSubmit);
    downloadReportBtn.addEventListener('click', generateAndDownloadReport);
    newPredictionBtn.addEventListener('click', handleNewPrediction);

    function handleFormSubmit(event) {
        event.preventDefault();

        if (predicciones.length >= 3) {
            alert('Ya se han realizado 3 predicciones. Descargue el informe o reinicie para hacer nuevas predicciones.');
            return;
        }

        const formData = {
            año_inicio: parseInt(document.getElementById('año_inicio').value),
            año_fin: parseInt(document.getElementById('año_fin').value),
            opcion: document.getElementById('opcion').value
        };

        fetch('/obtener_estudiantes')
            .then(response => response.json())
            .then(data => {
                formData.estudiantes_inicial = data.total;
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
                predicciones.push(data);
                if (currentChart) {
                    currentChart.destroy();
                }
                currentChart = generateChart(data);

                // Guardar la imagen de la gráfica
                const canvas = document.getElementById('myChart');
                const imageData = canvas.toDataURL('image/png');
                graficas.push(imageData);

                downloadReportBtn.style.display = 'block';
                newPredictionBtn.style.display = 'block';

                if (predicciones.length === 3) {
                    rungeKuttaForm.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Hubo un error al procesar la solicitud. Por favor, inténtelo de nuevo.');
            });
    }

    function handleNewPrediction() {
        if (predicciones.length < 3) {
            rungeKuttaForm.reset();
            if (currentChart) {
                currentChart.destroy();
                currentChart = null;
            }
            const canvas = document.getElementById('myChart');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        } else {
            alert('Ya se han realizado 3 predicciones. Descargue el informe o reinicie para hacer nuevas predicciones.');
        }
    }
});

function generateAndDownloadReport() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    doc.setFont('Helvetica', 'bold');
    doc.setFontSize(18);
    doc.text('Informe de Simulaciones Runge-Kutta', 105, 15, null, null, 'center');

    predicciones.forEach((data, index) => {
        let y = 25;

        if (index > 0) {
            doc.addPage();
        }

        doc.setFontSize(14);
        doc.text(`Predicción ${index + 1}`, 10, y);
        y += 10;

        const ciclos = generateCycleLabels(data.años);
        const estudiantesPorCiclo = data.estudiantes.filter((_, i) => i % 2 !== 0);

        doc.setFontSize(12);
        doc.setFont('helvetica', 'normal');

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

            doc.setFontSize(11);
            doc.text(`El ciclo ${ciclo} del año ${año} tiene los siguientes resultados: `, 10, y);
            y += 7;

            doc.autoTable({
                startY: y,
                head: [['Concepto', 'Valor']],
                body: tableData,
                theme: 'grid',
                styles: { cellPadding: 2, fontSize: 10 },
            });

            y = doc.lastAutoTable.finalY + 10;
        }

        doc.autoTable({
            startY: y,
            head: [['Ciclo', 'Número de Estudiantes', 'Nuevos Ingresos', 'Desertores']],
            body: ciclos.map((ciclo, i) => [
                ciclo,
                formatNumber(estudiantesPorCiclo[i]),
                formatNumber(data.nuevos_ingresos[i]),
                formatNumber(data.desertores[i])
            ]),
        });

        y = doc.lastAutoTable.finalY + 10;

        // Añadir la gráfica guardada correspondiente a esta predicción
        doc.addImage(graficas[index], 'PNG', 10, y, 190, 100);
    });

    doc.save('multiple_runge_kutta_report.pdf');

    // Reiniciar todo después de descargar el informe
    predicciones = [];
    graficas = [];
    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }
    downloadReportBtn.style.display = 'none';
    newPredictionBtn.style.display = 'none';
    rungeKuttaForm.style.display = 'block';
    rungeKuttaForm.reset();

    const canvas = document.getElementById('myChart');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function generateChart(data, canvas = null) {
    const ctx = canvas ? canvas.getContext('2d') : document.getElementById('myChart').getContext('2d');

    // Limpiar el canvas antes de dibujar una nueva gráfica
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

    const ciclos = generateCycleLabels(data.años);

    const allPoints = data.estudiantes.flatMap((estudiante, i) => {
        if (i % 2 === 0) {
            const inicioPeríodo = estudiante;
            const despuésIngresos = inicioPeríodo + data.nuevos_ingresos[i / 2];
            const despuésDeserciones = despuésIngresos - data.desertores[i / 2];
            const finPeríodo = data.estudiantes[i + 1];
            return [inicioPeríodo, despuésIngresos, despuésDeserciones, finPeríodo];
        }
        return [];
    });

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
                    label: function (context) {
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

    return new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: chartOptions
    });
}

function generateCycleLabels(años) {
    return años.flatMap(año => [`${año}-1`, `${año}-2`]);
}

function formatNumber(num) {
    return new Intl.NumberFormat('es-PE').format(num);
}