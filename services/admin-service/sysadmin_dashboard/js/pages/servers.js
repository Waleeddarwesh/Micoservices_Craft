const ServersPage = (() => {
    function render(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h2>${window.t('Servers Inventory')}</h2>
                    <p class="text-secondary">${window.t('Manage system infrastructure, operating systems, and services.')}</p>
                </div>
                <div class="header-actions">
                    <button class="btn btn-primary" onclick="ServersPage.openAddServerModal()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        ${window.t('Add Server')}
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
                        <input type="text" class="form-input" id="server-search" placeholder="${window.t('Search servers...')}" oninput="ServersPage.loadData()">
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table" id="servers-table">
                        <thead>
                            <tr>
                                <th>${window.t('Hostname')}</th>
                                <th>${window.t('IP Address')}</th>
                                <th>${window.t('OS Type')}</th>
                                <th>${window.t('Environment')}</th>
                                <th>${window.t('Status')}</th>
                                <th>${window.t('Actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="6" class="text-center py-4"><div style="display:flex;flex-direction:column;align-items:center;padding:32px 0;"><div class="spinner" style="margin-bottom:16px;"></div><p style="color:var(--clr-text-muted)">Loading servers...</p></div></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        loadData();
    }

    async function loadData() {
        try {
            const data = await API.get('/api/system-admin/servers/');
            
            const tbody = document.querySelector('#servers-table tbody');
            if (!data || data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-border);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('No Data Available')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">${window.t('No servers found.')}</p>
    </div>
</td></tr>`;
                return;
            }

            tbody.innerHTML = data.map(server => `
                <tr>
                    <td class="font-medium">${server.hostname}</td>
                    <td>${server.ip_address}</td>
                    <td>${server.os_type}</td>
                    <td><span class="badge badge-info">${server.environment}</span></td>
                    <td>
                        <span class="badge badge-${server.status === 'active' ? 'success' : 'warning'}">${server.status}</span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline" onclick="ServersPage.editServer(${server.id})">${window.t('Edit')}</button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            console.error('Error loading servers:', error);
            document.querySelector('#servers-table tbody').innerHTML = 
                `<tr><td colspan="6" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-danger);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('Error')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">${window.t('Failed to load servers')}</p>
    </div>
</td></tr>`;
        }
    }

    function openAddServerModal() {
        Toast.show('Add server functionality will be implemented in the next phase.', 'info');
    }

    function editServer(id) {
        Toast.show(`Edit functionality for server ${id} will be implemented in the next phase.`, 'info');
    }

    return { render, loadData, openAddServerModal, editServer };
})();

window.ServersPage = ServersPage;
