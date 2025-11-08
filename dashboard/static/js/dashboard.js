// Jule Bot Dashboard - Main JavaScript

// Update current time
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('currentTime').textContent = timeString;
}

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format relative time
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
}

// Fetch and display overview stats
async function loadOverviewStats() {
    try {
        const response = await fetch('/api/stats/overview');
        const data = await response.json();

        document.getElementById('totalUsers').textContent = formatNumber(data.total_users);
        document.getElementById('totalPoints').textContent = formatNumber(data.total_points);
        document.getElementById('totalMessages').textContent = formatNumber(data.total_messages);
        document.getElementById('activeReminders').textContent = formatNumber(data.active_reminders);
        document.getElementById('totalBirthdays').textContent = formatNumber(data.total_birthdays);
        document.getElementById('spamToday').textContent = formatNumber(data.spam_today);
        document.getElementById('messages24h').textContent = formatNumber(data.messages_24h);

        // Calculate uptime (mock for now)
        document.getElementById('uptime').textContent = '24h';
    } catch (error) {
        console.error('Error loading overview stats:', error);
    }
}

// Load leaderboard
async function loadLeaderboard() {
    try {
        const response = await fetch('/api/users/leaderboard?limit=10');
        const data = await response.json();

        const leaderboardDiv = document.getElementById('leaderboard');
        
        if (data.leaderboard.length === 0) {
            leaderboardDiv.innerHTML = '<div class="loading">No users yet</div>';
            return;
        }

        let html = '';
        data.leaderboard.forEach((user, index) => {
            const rank = index + 1;
            let rankClass = '';
            if (rank === 1) rankClass = 'gold';
            else if (rank === 2) rankClass = 'silver';
            else if (rank === 3) rankClass = 'bronze';

            const displayName = user.display_name || user.username;

            html += `
                <div class="leaderboard-item">
                    <div class="rank ${rankClass}">${rank}</div>
                    <div class="user-info">
                        <div class="user-name">${displayName}</div>
                        <div class="user-points">${formatNumber(user.points)} points</div>
                    </div>
                    <div class="points-badge">${formatNumber(user.points)}</div>
                </div>
            `;
        });

        leaderboardDiv.innerHTML = html;
    } catch (error) {
        console.error('Error loading leaderboard:', error);
        document.getElementById('leaderboard').innerHTML = '<div class="loading">Error loading data</div>';
    }
}

// Load upcoming birthdays
async function loadBirthdays() {
    try {
        const response = await fetch('/api/birthdays/upcoming');
        const data = await response.json();

        const birthdaysDiv = document.getElementById('birthdaysList');
        
        if (data.birthdays.length === 0) {
            birthdaysDiv.innerHTML = '<div class="loading">No upcoming birthdays</div>';
            return;
        }

        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

        let html = '';
        data.birthdays.forEach(birthday => {
            const monthName = monthNames[birthday.month - 1];
            const daysText = birthday.days_until === 0 ? 'Today!' : 
                           birthday.days_until === 1 ? 'Tomorrow' : 
                           `${birthday.days_until} days`;

            const displayName = birthday.display_name || birthday.username;

            html += `
                <div class="birthday-item">
                    <div class="birthday-user">
                        <div class="birthday-icon">🎂</div>
                        <div>
                            <div class="birthday-details">${displayName}</div>
                            <div class="birthday-date">${monthName} ${birthday.day}</div>
                        </div>
                    </div>
                    <div class="days-until">${daysText}</div>
                </div>
            `;
        });

        birthdaysDiv.innerHTML = html;
    } catch (error) {
        console.error('Error loading birthdays:', error);
        document.getElementById('birthdaysList').innerHTML = '<div class="loading">Error loading data</div>';
    }
}

// Load spam logs
async function loadSpamLogs() {
    try {
        const response = await fetch('/api/logs/spam?limit=20&hours=24');
        const data = await response.json();

        const tbody = document.querySelector('#spamLogs tbody');
        
        if (data.logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No spam logs in the last 24 hours</td></tr>';
            return;
        }

        let html = '';
        data.logs.forEach(log => {
            const actionClass = log.action.toLowerCase().includes('delete') ? 'danger' : 'warning';
            html += `
                <tr>
                    <td>${formatRelativeTime(log.detected_at)}</td>
                    <td>${log.username}</td>
                    <td>${log.guild_id}</td>
                    <td>${log.message_count}</td>
                    <td>${log.timeframe.toFixed(1)}s</td>
                    <td><span class="action-badge ${actionClass}">${log.action}</span></td>
                </tr>
            `;
        });

        tbody.innerHTML = html;
    } catch (error) {
        console.error('Error loading spam logs:', error);
        document.querySelector('#spamLogs tbody').innerHTML = 
            '<tr><td colspan="6" class="loading">Error loading logs</td></tr>';
    }
}

// Load reminders
async function loadReminders() {
    try {
        const response = await fetch('/api/reminders');
        const data = await response.json();

        const remindersDiv = document.getElementById('remindersList');
        
        if (data.reminders.length === 0) {
            remindersDiv.innerHTML = '<div class="loading">No active reminders</div>';
            return;
        }

        let html = '';
        data.reminders.forEach(reminder => {
            const remindTime = new Date(reminder.remind_time);
            const timeString = remindTime.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            html += `
                <div class="reminder-item">
                    <div class="reminder-content">
                        <div class="reminder-message">${reminder.message}</div>
                        <div class="reminder-meta">
                            User: ${reminder.username} | Channel: ${reminder.channel_id}
                        </div>
                    </div>
                    <div class="reminder-time">${timeString}</div>
                </div>
            `;
        });

        remindersDiv.innerHTML = html;
    } catch (error) {
        console.error('Error loading reminders:', error);
        document.getElementById('remindersList').innerHTML = '<div class="loading">Error loading data</div>';
    }
}

// Load birthday calendar
async function loadBirthdayCalendar() {
    try {
        const response = await fetch('/api/birthdays/calendar');
        const data = await response.json();

        const calendarDiv = document.getElementById('birthdayCalendar');

        if (data.birthdays.length === 0) {
            calendarDiv.innerHTML = '<div class="loading">No birthdays registered</div>';
            return;
        }

        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December'];

        // Group birthdays by month
        const birthdaysByMonth = {};
        for (let i = 1; i <= 12; i++) {
            birthdaysByMonth[i] = [];
        }

        data.birthdays.forEach(birthday => {
            birthdaysByMonth[birthday.month].push(birthday);
        });

        // Create calendar grid
        let html = '<div class="calendar-grid">';

        for (let month = 1; month <= 12; month++) {
            const birthdays = birthdaysByMonth[month];
            const hasAny = birthdays.length > 0;

            html += `
                <div class="calendar-month ${hasAny ? 'has-birthdays' : ''}">
                    <div class="month-header">
                        <i class="fas fa-calendar"></i>
                        <span>${monthNames[month - 1]}</span>
                        ${hasAny ? `<span class="birthday-count">${birthdays.length}</span>` : ''}
                    </div>
                    <div class="month-birthdays">
            `;

            if (birthdays.length === 0) {
                html += '<div class="no-birthdays">No birthdays</div>';
            } else {
                birthdays.forEach(birthday => {
                    const displayName = birthday.display_name || birthday.username;
                    html += `
                        <div class="calendar-birthday-item">
                            <div class="birthday-day">${birthday.day}</div>
                            <div class="birthday-username">${displayName}</div>
                        </div>
                    `;
                });
            }

            html += `
                    </div>
                </div>
            `;
        }

        html += '</div>';
        calendarDiv.innerHTML = html;
    } catch (error) {
        console.error('Error loading birthday calendar:', error);
        document.getElementById('birthdayCalendar').innerHTML = '<div class="loading">Error loading calendar</div>';
    }
}

// Create activity chart
let activityChart = null;

async function loadActivityChart() {
    try {
        const response = await fetch('/api/activity/chart?days=7');
        const data = await response.json();

        const ctx = document.getElementById('activityChart').getContext('2d');

        // Destroy existing chart if it exists
        if (activityChart) {
            activityChart.destroy();
        }

        const labels = data.activity.map(d => {
            const date = new Date(d.date);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });
        const values = data.activity.map(d => d.count);

        activityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Messages',
                    data: values,
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#a855f7',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: '#1e2139',
                        titleColor: '#e4e4e7',
                        bodyColor: '#a1a1aa',
                        borderColor: '#27272a',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#27272a',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#a1a1aa'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#a1a1aa'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading activity chart:', error);
    }
}

// Update last updated time
function updateLastUpdated() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('lastUpdated').textContent = timeString;
}

// Initialize dashboard
async function initDashboard() {
    updateTime();
    updateLastUpdated();

    await Promise.all([
        loadOverviewStats(),
        loadLeaderboard(),
        loadBirthdays(),
        loadBirthdayCalendar(),
        loadSpamLogs(),
        loadReminders(),
        loadActivityChart()
    ]);
}

// Auto-refresh
function startAutoRefresh() {
    // Update time every second
    setInterval(updateTime, 1000);

    // Refresh data every 30 seconds
    setInterval(() => {
        initDashboard();
    }, 30000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    startAutoRefresh();
});

