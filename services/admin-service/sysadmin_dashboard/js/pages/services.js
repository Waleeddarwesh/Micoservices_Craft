const ServicesPage = (() => {
    function render(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h2>${window.t('Services Registry')}</h2>
                    <p class="text-secondary">${window.t('Manage all system services from one place.')}</p>
                </div>
                <div class="header-actions">
                    <button class="btn btn-primary" onclick="Toast.show('Add service functionality not implemented yet.', 'info')">
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
                        <input type="text" class="form-input" placeholder="${window.t('Search...')}" oninput="ServicesPage.loadData()">
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table" id="services-table">
                        <thead>
                            <tr>
                                <th>${window.t('Name')}</th>
                                <th>${window.t('Server')}</th>
                                <th>${window.t('Type')}</th>
                                <th>${window.t('Status')}</th>
                                <th>${window.t('Last Restart')}</th>
                                <th>${window.t('Actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="6" class="text-center py-4"><div style="display:flex;flex-direction:column;align-items:center;padding:32px 0;"><div class="spinner" style="margin-bottom:16px;"></div><p style="color:var(--clr-text-muted)">Loading services...</p></div></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        loadData();
    }

    async function loadData() {
        try {
            const data = await API.get('/api/system-admin/services/');
            const tbody = document.querySelector('#services-table tbody');
            if (!data || data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-border);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('No Data Available')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">${window.t('No services found.')}</p>
    </div>
</td></tr>`;
                return;
            }

            tbody.innerHTML = data.map(service => `
                <tr>
                    <td class="font-medium">${service.service_name}</td>
                    <td>${service.server ? `Server #${service.server}` : 'Local'}</td>
                    <td>${service.service_type}</td>
                    <td>
                        <span class="badge badge-${service.status === 'running' || service.status === 'active' ? 'success' : (service.status === 'stopped' ? 'danger' : 'warning')}">${service.status}</span>
                    </td>
                    <td>${service.last_restart ? new Date(service.last_restart).toLocaleString() : 'Never'}</td>
                    <td>
                        <button class="btn btn-sm btn-outline" onclick="ServicesPage.executeCommand(${service.id}, 'start')">${window.t('Start')}</button>
                        <button class="btn btn-sm btn-outline text-danger" onclick="ServicesPage.executeCommand(${service.id}, 'stop')">${window.t('Stop')}</button>
                        <button class="btn btn-sm btn-outline" onclick="ServicesPage.executeCommand(${service.id}, 'restart')">${window.t('Restart')}</button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            console.error('Error loading services:', error);
            document.querySelector('#services-table tbody').innerHTML = 
                `<tr><td colspan="6" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-danger);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('Error')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">${window.t('Failed to load services')}</p>
    </div>
</td></tr>`;
        }
    }

    async function executeCommand(id, action) {
        try {
            Toast.show(`Executing ${action} command...`, 'info');
            const result = await API.post(`/api/system-admin/services/${id}/execute_command/`, { action });
            if (result && result.success !== false) {
                Toast.show(`Service ${action} command executed successfully.`, 'success');
                loadData();
            } else {
                Toast.show(result.error || `Failed to ${action} service.`, 'error');
            }
        } catch (error) {
            Toast.show(`Error: ${error.message}`, 'error');
        }
    }

    return { render, loadData, executeCommand };
})();

window.ServicesPage = ServicesPage;
