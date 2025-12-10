// Chart Global Config
Chart.defaults.color = '#a1a1aa';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.05)';

let activityChartInstance = null;
let gameChartInstance = null;

async function updateActivityChart() {
    try {
        const response = await fetch('/api/activity/chart?days=7');
        const data = await response.json();

        const ctx = document.getElementById('activityChart');
        if (!ctx) return;

        const labels = data.activity.map(item => {
            const date = new Date(item.date);
            return date.toLocaleDateString('en-US', { weekday: 'short' });
        });
        const values = data.activity.map(item => item.count);

        if (activityChartInstance) {
            activityChartInstance.data.labels = labels;
            activityChartInstance.data.datasets[0].data = values;
            activityChartInstance.update();
        } else {
            activityChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Messages',
                        data: values,
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#6366f1',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { display: true, drawBorder: false }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        }
    } catch (e) {
        console.error("Chart error:", e);
    }
}

function updateGamesChart(gamesData) {
    const ctx = document.getElementById('gamesChart');
    if (!ctx) return;

    const labels = gamesData.map(g => g.game_type);
    const played = gamesData.map(g => g.total_played);

    if (gameChartInstance) {
        gameChartInstance.data.labels = labels;
        gameChartInstance.data.datasets[0].data = played;
        gameChartInstance.update();
    } else {
        gameChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: played,
                    backgroundColor: [
                        '#6366f1', // Indigo
                        '#ec4899', // Pink
                        '#10b981', // Emerald
                        '#f59e0b', // Amber
                        '#8b5cf6'  // Violet
                    ],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }
}
