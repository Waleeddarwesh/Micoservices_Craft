const SystemLogsPage = (() => {
    function render(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h2>${window.t('System Logs')}</h2>
                    <p class="text-secondary">${window.t('Centralized search and live view of application and system logs.')}</p>
                </div>
                <div class="page-header-actions">
                    <button class="btn btn-outline" onclick="SystemLogsPage.loadData()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                            <path d="M21 2v6h-6"></path>
                            <path d="M3 12a9 9 0 0 1 15-6.7L21 8"></path>
                            <path d="M3 22v-6h6"></path>
                            <path d="M21 12a9 9 0 0 1-15 6.7L3 16"></path>
                        </svg>
                        ${window.t('Refresh')}
                    </button>
                    <button class="btn btn-primary" onclick="Toast.show('Export functionality not implemented yet.', 'info')">
                        ${window.t('Export Logs')}
                    </button>
                </div>
            </div>

            <div class="card data-table-wrapper">
                <div class="table-actions">
                    <div class="form-search" style="width: 320px; max-width: 100%;">
                        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                            <circle cx="11" cy="11" r="8"></circle>
                            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                        </svg>
                        <input type="text" placeholder="${window.t('Search logs...')}" class="form-input" oninput="SystemLogsPage.loadData()">
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table" id="syslogs-table">
                        <thead>
                            <tr>
                                <th>${window.t('Timestamp')}</th>
                                <th>${window.t('Source')}</th>
                                <th>${window.t('Level')}</th>
                                <th>${window.t('Message')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="4" class="text-center py-4"><div style="display:flex;flex-direction:column;align-items:center;padding:32px 0;"><div class="spinner" style="margin-bottom:16px;"></div><p style="color:var(--clr-text-muted)">Loading logs...</p></div></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        loadData();
    }

    async function loadData() {
        try {
            const data = await API.get('/api/system-admin/system-logs/');
            const tbody = document.querySelector('#syslogs-table tbody');
            if (!data || data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-border);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('No Data Available')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">${window.t('No logs found.')}</p>
    </div>
</td></tr>`;
                return;
            }

            tbody.innerHTML = data.map(log => {
                let badgeClass = 'secondary';
                if (log.level === 'WARN') badgeClass = 'warning';
                if (log.level === 'ERROR' || log.level === 'CRITICAL') badgeClass = 'danger';
                if (log.level === 'INFO') badgeClass = 'info';

                return `
                <tr>
                    <td class="font-mono text-xs text-secondary">${new Date(log.timestamp).toLocaleString()}</td>
                    <td class="font-medium">${log.source}</td>
                    <td>
                        <span class="badge badge-${badgeClass}">${log.level}</span>
                    </td>
                    <td class="font-mono text-sm">${log.message}</td>
                </tr>
            `}).join('');
        } catch (error) {
            console.error('Error loading system logs:', error);
            document.querySelector('#syslogs-table tbody').innerHTML = 
                `<tr><td colspan="4" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-danger);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('Error')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">${window.t('Failed to load system logs')}</p>
    </div>
</td></tr>`;
        }
    }

    return { render, loadData };
})();

window.SystemLogsPage = SystemLogsPage;
