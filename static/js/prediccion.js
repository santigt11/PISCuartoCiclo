let predicciones = [];
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

    let currentPage = 1;
    let processedPredictions = 0;

    function processPrediction(index) {
        if (index >= predicciones.length) {
            doc.save('multiple_runge_kutta_report.pdf');
            resetAfterDownload();
            return;
        }

        const data = predicciones[index];
        let y = 25;

        if (index > 0) {
            doc.addPage();
            currentPage++;
        }

        doc.setFontSize(14);
        doc.text(`Predicción ${index + 1}`, 10, y);
        y += 10;

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

        y = doc.lastAutoTable.finalY + 10;

        // Generar la gráfica para el PDF
        const canvas = document.createElement('canvas');
        canvas.width = 800;
        canvas.height = 400;
        const ctx = canvas.getContext('2d');

        const chartData = createChartData(data);

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

        // Usar setTimeout para asegurarse de que la gráfica se ha renderizado completamente
        setTimeout(() => {
            const imgData = canvas.toDataURL('image/png');

            // Verificar si hay espacio suficiente en la página actual
            if (y + 80 > doc.internal.pageSize.height - 20) {
                doc.addPage();
                currentPage++;
                y = 20;
            }

            doc.addImage(imgData, 'PNG', 10, y, 180, 80);

            // Procesar la siguiente predicción
            processPrediction(index + 1);
        }, 1000);
    }

    // Iniciar el proceso con la primera predicción
    processPrediction(0);
}

function resetAfterDownload() {
    predicciones = [];
    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }
    downloadReportBtn.style.display = 'none';
    newPredictionBtn.style.display = 'none';
    rungeKuttaForm.style.display = 'block';
    rungeKuttaForm.reset();

    const mainCanvas = document.getElementById('myChart');
    const mainCtx = mainCanvas.getContext('2d');
    mainCtx.clearRect(0, 0, mainCanvas.width, mainCanvas.height);
}

function generateChart(data) {
    const ctx = document.getElementById('myChart').getContext('2d');
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

    const chartData = createChartData(data);

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

function createChartData(data) {
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

    return {
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
}

function generateCycleLabels(años) {
    return años.flatMap(año => [`${año}-1`, `${año}-2`]);
}

function formatNumber(num) {
    return new Intl.NumberFormat('es-PE').format(num);
}