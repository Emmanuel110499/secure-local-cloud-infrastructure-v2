const MAX_POINTS = 20;

const chartLabels = [];
const cpuValues = [];
const memoryValues = [];

const cpuChart = new Chart(
    document.getElementById("cpuChart"),
    {
        type: "line",
        data: {
            labels: chartLabels,
            datasets: [
                {
                    label: "CPU (%)",
                    data: cpuValues,
                    tension: 0.35,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            animation: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    }
);

const memoryChart = new Chart(
    document.getElementById("memoryChart"),
    {
        type: "line",
        data: {
            labels: chartLabels,
            datasets: [
                {
                    label: "RAM (%)",
                    data: memoryValues,
                    tension: 0.35,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            animation: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    }
);

function addChartPoint(cpu, memory) {
    const now = new Date().toLocaleTimeString("fr-FR");

    chartLabels.push(now);
    cpuValues.push(cpu ?? 0);
    memoryValues.push(memory ?? 0);

    if (chartLabels.length > MAX_POINTS) {
        chartLabels.shift();
        cpuValues.shift();
        memoryValues.shift();
    }

    cpuChart.update();
    memoryChart.update();
}

async function refreshCharts() {
    try {
        const response = await fetch("/api/metrics", {
            cache: "no-store"
        });

        if (!response.ok) {
            throw new Error("API indisponible");
        }

        const data = await response.json();

        addChartPoint(
            data.metrics.cpu,
            data.metrics.memory
        );
    } catch (error) {
        console.error(
            "Impossible de récupérer les métriques :",
            error
        );
    }
}

refreshCharts();
window.setInterval(refreshCharts, 5000);

async function loadContainers() {

    try {

        const response = await fetch("/api/containers");

        const data = await response.json();

        const tbody = document.getElementById("containers-table");

        tbody.innerHTML = "";

        data.containers.forEach(container => {

            tbody.innerHTML += `
                <tr>

                    <td>${container.name}</td>

                    <td>${container.image}</td>

                    <td>

                        <span class="badge bg-success">
                            Running
                        </span>

                    </td>

                </tr>
            `;

        });

    }

    catch(error){

        console.error(error);

    }

}
loadContainers();

setInterval(loadContainers,5000);