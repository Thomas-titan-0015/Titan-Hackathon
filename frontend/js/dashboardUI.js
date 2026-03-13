// Tanishq — Dashboard (Admin Only)
(async function () {
    if (!AUTH.requireAdmin()) return;

    const tabs = document.querySelectorAll('.dash-tab');
    const panels = document.querySelectorAll('.dash-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById('panel-' + tab.dataset.tab).classList.add('active');
        });
    });

    // Overview
    try {
        const o = await API.dashOverview();
        const grid = document.getElementById('kpiGrid');
        grid.innerHTML = `
            <div class="kpi-card"><div class="kpi-value">${o.total_sessions}</div><div class="kpi-label">Total Sessions</div></div>
            <div class="kpi-card"><div class="kpi-value">${o.new_users}</div><div class="kpi-label">New Users</div></div>
            <div class="kpi-card"><div class="kpi-value">${o.returning_users}</div><div class="kpi-label">Returning Users</div></div>
            <div class="kpi-card"><div class="kpi-value">${o.avg_messages_per_session}</div><div class="kpi-label">Avg Messages/Session</div></div>
            <div class="kpi-card"><div class="kpi-value">${o.total_orders}</div><div class="kpi-label">Orders</div></div>
            <div class="kpi-card"><div class="kpi-value">₹${o.total_revenue.toLocaleString('en-IN', {minimumFractionDigits: 2})}</div><div class="kpi-label">Revenue</div></div>
        `;
    } catch (e) { console.error('Overview:', e); }

    // Sessions
    try {
        const sessions = await API.dashSessions();
        const tbody = document.getElementById('sessionsBody');
        if (sessions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-secondary);padding:40px;">No sessions yet</td></tr>';
        } else {
            tbody.innerHTML = sessions.map(s => `
                <tr>
                    <td title="${s.id}">${s.id.slice(0, 12)}…</td>
                    <td>${s.user_id || '—'}</td>
                    <td><span class="path-badge">${s.path || '—'}</span></td>
                    <td>${s.message_count}</td>
                    <td>${new Date(s.started_at).toLocaleString()}</td>
                    <td><button class="btn-sm btn-primary" onclick="viewConversation('${s.id}')">View</button></td>
                </tr>
            `).join('');
        }
    } catch (e) { console.error('Sessions:', e); }

    // View conversation handler
    window.viewConversation = async (sessionId) => {
        tabs.forEach(t => t.classList.remove('active'));
        panels.forEach(p => p.classList.remove('active'));
        document.querySelector('[data-tab="conversations"]').classList.add('active');
        document.getElementById('panel-conversations').classList.add('active');

        const title = document.getElementById('convTitle');
        const container = document.getElementById('convMessages');
        title.textContent = `Session: ${sessionId}`;
        container.innerHTML = '<p style="color:var(--text-secondary)">Loading…</p>';
        try {
            const messages = await API.dashConversation(sessionId);
            if (messages.length === 0) {
                container.innerHTML = '<p style="color:var(--text-secondary)">No messages in this session.</p>';
            } else {
                container.innerHTML = messages.map(m => `
                    <div class="conv-msg ${m.role}" style="margin-bottom:12px;padding:12px;background:var(--bg-hover);border-radius:var(--radius-sm);border-left:3px solid ${m.role === 'user' ? 'var(--accent)' : 'var(--success)'};">
                        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                            <strong style="color:${m.role === 'user' ? 'var(--accent)' : 'var(--success)'};text-transform:capitalize;">${m.role}</strong>
                            <span style="color:var(--text-secondary);font-size:.75rem;">${new Date(m.timestamp).toLocaleString()}</span>
                        </div>
                        <div style="font-size:.88rem;line-height:1.6;">${m.content}</div>
                        ${m.item_ids_shown ? `<div style="color:var(--text-secondary);font-size:.75rem;margin-top:6px;">Products shown: ${m.item_ids_shown.join(', ')}</div>` : ''}
                    </div>
                `).join('');
            }
        } catch (e) {
            container.innerHTML = '<p style="color:var(--danger)">Failed to load conversation.</p>';
        }
    };

    // Users
    try {
        const users = await API.dashUsers();
        const tbody = document.getElementById('usersBody');
        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-secondary);padding:40px;">No users yet</td></tr>';
        } else {
            tbody.innerHTML = users.map(u => `
                <tr>
                    <td>${u.id}</td>
                    <td>${u.name}</td>
                    <td>${u.email}</td>
                    <td><span class="path-badge">${u.role}</span></td>
                    <td><span class="path-badge">${u.segment}</span></td>
                    <td>${new Date(u.last_seen).toLocaleString()}</td>
                </tr>
            `).join('');
        }
    } catch (e) { console.error('Users:', e); }

    // Recommendation stats
    try {
        const stats = await API.dashRecStats();
        const tbody = document.getElementById('recBody');
        if (stats.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-secondary);padding:40px;">No recommendation data yet. Stats appear after users interact with product recommendations.</td></tr>';
        } else {
            tbody.innerHTML = stats.map(s => `
                <tr><td title="${s.session_id}">${s.session_id.slice(0, 12)}…</td><td>${s.shown}</td><td>${s.clicked}</td><td>${s.dismissed}</td><td>${s.ctr}%</td></tr>
            `).join('');
        }
    } catch (e) { console.error('RecStats:', e); }
})();
