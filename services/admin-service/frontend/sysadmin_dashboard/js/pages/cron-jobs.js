const CronJobsPage = (() => {
    function render(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h2>${window.t('Cron Job Administration')}</h2>
                    <p class="text-secondary">${window.t('Create, edit, and disable scheduled tasks.')}</p>
                </div>
                <div class="header-actions">
                    <button class="btn btn-primary" onclick="Toast.show('Add cron functionality not implemented yet.', 'info')">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        ${window.t('Add New')}
                    </button>
                </div>
            </div>

            <div class="card">
                <div class="table-actions">
                    <div class="form-search" style="width: 320px; max-width: 100%;">
                        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                            <circle cx="11" cy="11" r="8"></circle>
                            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                        </svg>
                        <input type="text" class="form-input" placeholder="${window.t('Search...')}" oninput="CronJobsPage.loadData()">
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table" id="cron-table">
                        <thead>
                            <tr>
                                <th>${window.t('Name')}</th>
                                <th>${window.t('Server')}</th>
                                <th>${window.t('Schedule')}</th>
                                <th>${window.t('Command')}</th>
                                <th>${window.t('User')}</th>
                                <th>${window.t('Status')}</th>
                                <th>${window.t('Actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="7" class="text-center py-4"><div style="display:flex;flex-direction:column;align-items:center;padding:32px 0;"><div class="spinner" style="margin-bottom:16px;"></div><p style="color:var(--clr-text-muted)">Loading cron jobs...</p></div></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        loadData();
    }

    async function loadData() {
        try {
            const data = await API.get('/api/system-admin/cron-jobs/');
            const tbody = document.querySelector('#cron-table tbody');
            if (!data || data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-border);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('No Data Available')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">${window.t('No cron jobs found.')}</p>
    </div>
</td></tr>`;
                return;
            }

            tbody.innerHTML = data.map(job => `
                <tr>
                    <td class="font-medium">${job.name}</td>
                    <td>${job.server ? `Server #${job.server}` : 'Local'}</td>
                    <td><code>${job.schedule}</code></td>
                    <td class="text-secondary" style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${job.command}">${job.command}</td>
                    <td>${job.user}</td>
                    <td>
                        <span class="badge badge-${job.status === 'active' ? 'success' : 'warning'}">${job.status}</span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline" onclick="Toast.show('Edit functionality coming soon', 'info')">${window.t('Edit')}</button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            console.error('Error loading cron jobs:', error);
            document.querySelector('#cron-table tbody').innerHTML = 
                `<tr><td colspan="7" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-danger);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('Error')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">${window.t('Failed to load cron jobs')}</p>
    </div>
</td></tr>`;
        }
    }

    return { render, loadData };
})();

window.CronJobsPage = CronJobsPage;
