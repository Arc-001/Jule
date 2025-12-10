document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadAllData();
    setInterval(loadAllData, 60000); // Auto-refresh every minute
});

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.view-section');
    const title = document.getElementById('page-title');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Update Nav
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Update View
            const targetId = item.dataset.tab;
            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === targetId) section.classList.add('active');
            });

            // Update Title
            const titleMap = {
                'overview': 'Dashboard Overview',
                'leaderboard': 'Global Rankings',
                'games': 'Games Arena',
                'music': 'Music Hall',
                'logs': 'Security Logs'
            };
            title.textContent = titleMap[targetId] || 'Dashboard';
        });
    });
}

async function loadAllData() {
    const btn = document.querySelector('#refresh-icon');
    if (btn) btn.classList.add('fa-spin');

    try {
        await Promise.all([
            loadOverview(),
            loadLeaderboard(),
            loadGames(),
            loadMusic(),
            loadLogs(),
            loadBirthdays()
        ]);
    } catch (error) {
        console.error('Error loading data:', error);
    } finally {
        if (btn) btn.classList.remove('fa-spin');
    }
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

// ================= DATA LOADING FUNCTIONS =================

async function loadOverview() {
    const response = await fetch('/api/stats/overview');
    const data = await response.json();

    document.getElementById('stat-users').textContent = formatNumber(data.total_users);
    document.getElementById('stat-points').textContent = formatNumber(data.total_points);
    document.getElementById('stat-messages-24h').textContent = formatNumber(data.messages_24h);
    document.getElementById('stat-spam').textContent = formatNumber(data.spam_today);

    // Trigger chart update if available
    if (window.updateActivityChart) window.updateActivityChart();
}

async function loadLeaderboard() {
    const response = await fetch('/api/users/leaderboard?limit=50');
    const data = await response.json();
    const tbody = document.getElementById('leaderboard-body');
    if (!tbody) return;

    tbody.innerHTML = data.leaderboard.map((user, index) => {
        let rankClass = 'rank-other';
        if (index === 0) rankClass = 'rank-1';
        if (index === 1) rankClass = 'rank-2';
        if (index === 2) rankClass = 'rank-3';

        return `
            <tr>
                <td><span class="rank-badge ${rankClass}">${index + 1}</span></td>
                <td>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-weight: 600;">${user.username || 'Unknown'}</span>
                    </div>
                </td>
                <td style="font-family: 'Outfit'; color: var(--primary); font-weight: 700;">
                    ${formatNumber(user.points)}
                </td>
                 <td><span style="font-size: 0.8rem; color: var(--text-muted);">Active</span></td>
            </tr>
        `;
    }).join('');
}

async function loadGames() {
    const response = await fetch('/api/games/stats');
    const data = await response.json();

    document.getElementById('game-total').textContent = formatNumber(data.total_games);

    // Calculate global winrate
    let totalWins = 0;
    let totalPlayed = 0;
    data.games.forEach(g => {
        totalWins += g.total_wins;
        totalPlayed += g.total_played;
    });
    const globalRate = totalPlayed > 0 ? (totalWins / totalPlayed * 100).toFixed(1) : 0;

    document.getElementById('game-winrate').textContent = `${globalRate}%`;

    // Update Trivia Circle if element exists
    // Using a mock fetch for trivia specific stats as example
    const triviaRes = await fetch('/api/trivia/stats');
    const triviaData = await triviaRes.json();

    const circle = document.getElementById('trivia-accuracy-circle');
    if (circle) {
        circle.style.background = `conic-gradient(var(--primary) ${triviaData.accuracy * 3.6}deg, rgba(255,255,255,0.1) 0deg)`;
        circle.querySelector('.progress-value').textContent = `${Math.round(triviaData.accuracy)}%`;
    }

    if (window.updateGamesChart) window.updateGamesChart(data.games);
}

async function loadMusic() {
    const response = await fetch('/api/music/top?limit=10');
    const data = await response.json();
    const container = document.getElementById('music-list');
    if (!container) return;

    container.innerHTML = data.top_songs.map((song, i) => `
        <div style="display: flex; justify-content: space-between; padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <div style="display: flex; gap: 12px; align-items: center;">
                <span style="color: var(--text-muted); width: 20px;">#${i + 1}</span>
                <div>
                    <div style="font-weight: 600;">${song.title}</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">${song.artist}</div>
                </div>
            </div>
            <div style="font-weight: 700; color: var(--secondary);">${song.plays} plays</div>
        </div>
    `).join('');
}

async function loadLogs() {
    const response = await fetch('/api/logs/spam?limit=20');
    const data = await response.json();
    const tbody = document.getElementById('logs-body');
    if (!tbody) return;

    tbody.innerHTML = data.logs.map(log => {
        const date = new Date(log.detected_at).toLocaleString();
        return `
            <tr>
                <td style="color: var(--text-muted); font-size: 0.85rem;">${date}</td>
                <td>${log.username}</td>
                <td style="color: #fca5a5;">${log.action}</td>
                <td>${log.message_count} msgs / ${log.timeframe}s</td>
            </tr>
        `;
    }).join('');
}

async function loadBirthdays() {
    const response = await fetch('/api/birthdays/upcoming');
    const data = await response.json();
    const list = document.getElementById('birthdays-list');
    if (!list) return;

    if (data.birthdays.length === 0) {
        list.innerHTML = '<div style="padding: 1rem; color: var(--text-muted); text-align: center;">No upcoming birthdays</div>';
        return;
    }

    const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];

    list.innerHTML = data.birthdays.map(b => `
        <div class="birthday-item">
            <div class="bday-date-box">
                <span class="bday-month">${months[b.month - 1]}</span>
                <span class="bday-day">${b.day}</span>
            </div>
            <div class="bday-info">
                <h4>${b.username}</h4>
                <span>In ${b.days_until} days</span>
            </div>
        </div>
    `).join('');
}

// Global Refresh
function refreshData() {
    loadAllData();
}
