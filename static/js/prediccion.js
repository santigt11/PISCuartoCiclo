 // Espera a que el DOM esté completamente cargado
    document.addEventListener('DOMContentLoaded', function () {
        // Selecciona el formulario
        const eulerForm = document.getElementById('eulerForm');
        const downloadReportBtn = document.getElementById('downloadReportBtn');

        // Agrega un event listener para la sumisión del formulario
        eulerForm.addEventListener('submit', function (event) {
            event.preventDefault(); // Evita la sumisión estándar del formulario

            // Recolecta los datos del formulario
            const formData = {
                t0: parseFloat(document.getElementById('t0').value),
                t_final: parseFloat(document.getElementById('t_final').value)
            };

            // Envía los datos al servidor usando fetch
            fetch('/calculate_euler', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                // Muestra el resultado en la gráfica
                generateChart(data);

                // Mostrar botón de descarga del informe
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

    // Función para generar la gráfica usando Chart.js
    function generateChart(data) {
        // Configuración de los datos para la gráfica
        const chartData = {
            labels: data.t.map(time => time.toFixed(2)),
            datasets: [{
                label: 'S(t) - Número Total de Estudiantes',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                data: data.S.map(result => result.toFixed(2))
            }, {
                label: 'D(t) - Estudiantes Desertados',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                data: data.D.map(result => result.toFixed(2))
            }]
        };

        // Configuración de las opciones de la gráfica
        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Tiempo'
                    }
                }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Número de Estudiantes'
                    },
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        };

        // Obtén el contexto del canvas donde se dibujará la gráfica
        const ctx = document.getElementById('myChart').getContext('2d');

        // Crea la instancia de la gráfica
        const myChart = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: chartOptions
        });
    }

    // Función para generar y descargar el informe en formato HTML
    function generateAndDownloadReport(data) {
        // Construye el contenido del informe en HTML
        const reportContent = `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Informe de Cálculo de Euler</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                    }
                    .container {
                        max-width: 800px;
                        margin: 20px auto;
                        padding: 20px;
                        border: 1px solid #ccc;
                    }
                    h2 {
                        color: #007bff;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 20px;
                    }
                    th, td {
                        border: 1px solid #ccc;
                        padding: 8px;
                        text-align: center;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Informe de Cálculo de Euler</h2>
                    <h3>Datos de Resultado</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Tiempo</th>
                                <th>S(t) - Número Total de Estudiantes</th>
                                <th>D(t) - Estudiantes Desertados</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.t.map((time, index) => `
                                <tr>
                                    <td>${time.toFixed(2)}</td>
                                    <td>${data.S[index].toFixed(2)}</td>
                                    <td>${data.D[index].toFixed(2)}</td>
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
                        // Obtén el contexto del canvas donde se dibujará la gráfica
                        const ctx = document.getElementById('reportChart').getContext('2d');
                        
                        // Configuración de los datos para la gráfica
                        const chartData = {
                            labels: ${JSON.stringify(data.t.map(time => time.toFixed(2)))},
                            datasets: [{
                                label: 'S(t) - Número Total de Estudiantes',
                                data: ${JSON.stringify(data.S.map(result => result.toFixed(2)))},
                                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                                borderColor: 'rgba(54, 162, 235, 1)',
                                borderWidth: 1,
                                fill: false
                            }, {
                                label: 'D(t) - Estudiantes Desertados',
                                data: ${JSON.stringify(data.D.map(result => result.toFixed(2)))},
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                borderColor: 'rgba(255, 99, 132, 1)',
                                borderWidth: 1,
                                fill: false
                            }]
                        };

                        // Configuración de las opciones de la gráfica
                        const chartOptions = {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                xAxes: [{
                                    scaleLabel: {
                                        display: true,
                                        labelString: 'Tiempo'
                                    }
                                }],
                                yAxes: [{
                                    scaleLabel: {
                                        display: true,
                                        labelString: 'Número de Estudiantes'
                                    },
                                    ticks: {
                                        beginAtZero: true
                                    }
                                }]
                            }
                        };

                        // Crea la instancia de la gráfica
                        const myChart = new Chart(ctx, {
                            type: 'line',
                            data: chartData,
                            options: chartOptions
                        });
                    });
                </script>
            </body>
            </html>
        `;

        // Crear un blob con el contenido del informe
        const blob = new Blob([reportContent], { type: 'text/html' });
        const url = URL.createObjectURL(blob);

        // Crear un enlace para descargar el archivo
        const a = document.createElement('a');
        a.href = url;
        a.download = 'euler_report.html'; // Nombre del archivo a descargar
        a.click();

        // Liberar recursos
        URL.revokeObjectURL(url);
    }