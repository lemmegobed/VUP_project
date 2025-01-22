document.addEventListener("DOMContentLoaded", function () {
    console.log("dash_admin.js is loaded!");

    // รับค่าจาก input hidden
    const maleMembers = parseInt(document.getElementById('maleMembers').value);
    const femaleMembers = parseInt(document.getElementById('femaleMembers').value);

    console.log("Male Members:", maleMembers);
    console.log("Female Members:", femaleMembers);

    // ข้อมูลที่ใช้ร่วมกัน
    const labels = ['Male', 'Female'];
    const data = [maleMembers, femaleMembers];
    const backgroundColors = ['#36A2EB', '#FF6384'];

    // สร้าง Pie Chart
    const pieCtx = document.getElementById('genderPieChart').getContext('2d');
    const genderPieChart = new Chart(pieCtx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                datalabels: {
                    formatter: (value, context) => {
                        const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                        return ((value / total) * 100).toFixed(1) + '%';
                    }
                }
            }
        }
    });

    // สร้าง Bar Chart
    const barCtx = document.getElementById('genderBarChart').getContext('2d');
    const genderBarChart = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Members',
                data: data,
                backgroundColor: backgroundColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true // ให้แกน y เริ่มจาก 0
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                datalabels: {
                    anchor: 'end',
                    align: 'top',
                    formatter: (value) => value
                }
            }
        }
    });
});
