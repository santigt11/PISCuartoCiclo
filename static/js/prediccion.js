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

        const formData = {
            año_inicio: parseInt(document.getElementById('año_inicio').value),
            año_fin: parseInt(document.getElementById('año_fin').value),
            opcion: document.getElementById('opcion').value,
            factor: document.getElementById('factor').value
        };

        try {
            validateYearRange(formData.año_inicio, formData.año_fin);
            validateStartYear(formData.año_inicio);

            let fetchPromise;
            if (formData.año_inicio >= 2019 && formData.año_inicio <= 2023) {
                fetchPromise = fetch(`/get_total_students/${formData.año_inicio}`);
            } else {
                fetchPromise = fetch('/obtener_estudiantes');
            }

            fetchPromise
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
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    data.opcion = document.getElementById('opcion').value;
                    data.factor = document.getElementById('factor').value;
                    data.visualizacion = document.getElementById('visualizar').value;
                    data.año_inicio = formData.año_inicio;
                    data.año_fin = formData.año_fin;

                    // Guardar temporalmente la predicción actual
                    currentPrediction = data;

                    // Destruir el gráfico anterior si existe
                    if (currentChart) {
                        currentChart.destroy();
                    }

                    // Crear el nuevo gráfico
                    currentChart = generateChart(data);

                    downloadReportBtn.style.display = 'block';
                    newPredictionBtn.style.display = 'block';
                })
                .catch(error => {
                    console.error('Error:', error);
                    showErrorMessage('Error al realizar la simulación o obtener datos de estudiantes.');
                });
        } catch (error) {
            showErrorMessage(error.message);
        }
    }

    function validateYearRange(startYear, endYear) {
        if (endYear < startYear) {
            throw new Error('El año final no puede ser menor al año de inicio.');
        }
    }

    function validateStartYear(startYear) {
        const foundationYear = 2003;
        if (startYear < foundationYear) {
            throw new Error(`El año de inicio no puede ser menor a ${foundationYear}.`);
        }
    }

    function showErrorMessage(message) {
        // Eliminar cualquier referencia a la dirección IP y puerto
        const cleanedMessage = message.replace(/^.*?:\d+\s*dice\s*/, '');

        // Asegurarse de que el mensaje comienza con "Error:"
        const finalMessage = cleanedMessage.startsWith('Error:') ? cleanedMessage : 'Error: ' + cleanedMessage;

        // Mostrar un mensaje de alerta más amigable
        alert(finalMessage);

        // Registrar el error completo en la consola para depuración
        console.error('Error detallado:', message);
    }

    function handleNewPrediction() {
        if (predicciones.length < 3) {
            if (currentPrediction) {
                predicciones.push(currentPrediction);
                currentPrediction = null;
                rungeKuttaForm.reset();
                alert('La predicción actual ha sido guardada. Puede realizar una nueva predicción.');
            } else {
                alert('No hay ninguna predicción actual para guardar.');
            }
            downloadReportBtn.style.display = 'block';
            newPredictionBtn.style.display = 'block';
        } else {
            alert('Ya se han realizado 3 predicciones. Descargue el informe o reinicie para hacer nuevas predicciones.');
        }
    }
});

function generateChart(data) {
    const ctx = document.getElementById('myChart').getContext('2d');
    const visualizacion = document.getElementById('visualizar').value;
    const chartData = createChartData(data, visualizacion);

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Período'
                }
            },
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

    if (visualizacion === 'separada') {
        chartOptions.scales['y-axis-1'] = {
            type: 'linear',
            position: 'left',
            title: {
                display: true,
                text: 'Número de Estudiantes',
                color: 'rgba(54, 162, 235, 1)'
            },
            ticks: {
                color: 'rgba(54, 162, 235, 1)'
            },
            grid: {
                drawOnChartArea: false
            }
        };
        chartOptions.scales['y-axis-2'] = {
            type: 'linear',
            position: 'right',
            title: {
                display: true,
                text: 'Nuevos Ingresos / Desertores',
                color: 'rgb(140,225,125)'
            },
            ticks: {
                color: 'rgb(140,225,125)'
            },
            grid: {
                drawOnChartArea: false
            }
        };
    }

    return new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: chartOptions
    });
}

function createChartData(data, visualizacion) {
    const ciclos = generateCycleLabels(data.años);

    if (visualizacion === 'unificada') {
        const allPoints = [];
        const ingresosDeserciones = [];
        for (let i = 0; i < data.estudiantes.length; i += 2) {
            const inicioPeríodo = data.estudiantes[i];
            const despuésIngresos = inicioPeríodo + data.nuevos_ingresos[i / 2];
            const despuésDeserciones = despuésIngresos - data.desertores[i / 2];
            //const finPeríodo = despuésDeserciones;

            allPoints.push(inicioPeríodo, despuésIngresos, despuésDeserciones);
            ingresosDeserciones.push(null, {ingresos: data.nuevos_ingresos[i / 2]}, {deserciones: data.desertores[i / 2]}, null);
        }

        return {
            labels: ciclos.flatMap(ciclo => [
                ciclo + ' Inicio',
                ciclo + ' Ingresos',
                ciclo + ' Desertores'
            ]),
            datasets: [
                {
                    label: 'Número de Estudiantes',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    data: allPoints,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    tension: 0.4
                }

            ]
        };
    } else {
        const estudiantes = data.estudiantes.filter((_, index) => index % 2 !== 0);
        const nuevosIngresos = data.nuevos_ingresos;
        const desertores = data.desertores;

        return {
            labels: ciclos,
            datasets: [
                {
                    label: 'Estudiantes',
                    data: estudiantes,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    yAxisID: 'y-axis-1',
                    pointRadius: 5,
                    pointHoverRadius: 7
                },
                {
                    label: 'Nuevos Ingresos',
                    data: nuevosIngresos,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgb(140,225,125)',
                    borderWidth: 2,
                    yAxisID: 'y-axis-2',
                    pointStyle: 'rect',
                    pointRadius: 5,
                    pointHoverRadius: 7
                },
                {
                    label: 'Desertores',
                    data: desertores,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    yAxisID: 'y-axis-2',
                    pointStyle: 'triangle',
                    pointRadius: 5,
                    pointHoverRadius: 7
                }
            ]
        };
    }
}

function getCurrentDate() {
    const now = new Date();
    const day = String(now.getDate()).padStart(2, '0');
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const year = now.getFullYear();
    return `${day}-${month}-${year}`;
}

function generateCycleLabels(años) {
    return años.flatMap(año => [`${año}-1`, `${año}-2`]);
}

function generateAndDownloadReport() {
    try {
        const {jsPDF} = window.jspdf;
        const doc = new jsPDF();

        doc.addImage('static/img/PortadaUnl.png', 'PNG', 20, 20, 170, 250, 'center');
        doc.addPage();
        doc.setFont('Helvetica', 'bold');
        doc.setFontSize(18);
        doc.text('Informe De Predicción De Deserción Estudiantil', 105, 15, null, null, 'center');

        let currentPage = 1;

        function processPrediction(index) {
            if (index >= predicciones.length) {
                const currentDate = getCurrentDate();
                doc.save(`Informe_Deserción_${currentDate}.pdf`);
                //resetAfterDownload();
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

            // Agregar información sobre las opciones seleccionadas
            doc.text(`Género: ${data.opcion}`, 10, y);
            y += 7;
            doc.text(`Factor de deserción: ${data.factor}`, 10, y);
            y += 7;
            doc.text(`Visualización: ${data.visualizacion}`, 10, y);
            y += 7;
            doc.text(`Año inicio: ${data.años[0]}`, 10, y);
            y += 7;
            doc.text(`Año fin: ${data.años[data.años.length - 1]}`, 10, y);
            y += 10;

            for (let i = 1; i < data.estudiantes.length; i += 2) {
                const año = data.años[Math.floor((i - 1) / 4)];
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
                    styles: {cellPadding: 2, fontSize: 10},
                });

                y = doc.lastAutoTable.finalY + 10;

                if (y > doc.internal.pageSize.height - 20) {
                    doc.addPage();
                    currentPage++;
                    y = 20;
                }
            }

            // Generar la gráfica para el PDF
            const canvas = document.createElement('canvas');
            canvas.width = 800;
            canvas.height = 400;
            const ctx = canvas.getContext('2d');

            const chartData = createChartData(data, data.visualizacion);

            new Chart(ctx, {
                type: 'line',
                data: chartData,
                options: {
                    responsive: false,
                    maintainAspectRatio: false,
                    scales: {
                        x: {display: true},
                        y: {display: true}
                    }
                }
            });

            // Usar setTimeout para asegurarse de que la gráfica se ha renderizado completamente
            setTimeout(() => {
                const imgData = canvas.toDataURL('image/png');

                // Verificar si hay espacio suficiente en la página actual
                if (y + 80 > doc.internal.pageSize.height - 20) {
                    doc.addPage();
                    y = 40;
                }

                doc.addImage(imgData, 'PNG', 10, y, 180, 80);
                y += 90;
                // Procesar la siguiente predicción
                processPrediction(index + 1);
            }, 100);
        }

        // Iniciar el proceso con la primera predicción
        processPrediction(0);
    } catch (error) {
        showErrorMessage('Hubo un error al generar el informe: ' + error.message);
    }


}

function resetAfterDownload() {
    predicciones = [];
    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }
    document.getElementById('downloadReportBtn').style.display = 'none';
    document.getElementById('newPredictionBtn').style.display = 'none';
    document.getElementById('rungeKuttaForm').style.display = 'block';
    document.getElementById('rungeKuttaForm').reset();

    const mainCanvas = document.getElementById('myChart');
    const mainCtx = mainCanvas.getContext('2d');
    mainCtx.clearRect(0, 0, mainCanvas.width, mainCanvas.height);
}

function formatNumber(num) {
    return new Intl.NumberFormat('es-PE').format(num);
}