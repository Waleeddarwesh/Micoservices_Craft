const SecurityCenterPage = (() => {
    async function loadData() {
        try {
            const rules = await API.get('/api/system-admin/firewall-rules/');
            const alerts = await API.get('/api/system-admin/security-alerts/');
            const contexts = await API.get('/api/system-admin/selinux-contexts/');
            
            renderFirewallRules(rules);
            renderSecurityAlerts(alerts);
            renderSELinuxContexts(contexts);
        } catch (error) {
            console.error('Failed to load security data:', error);
            Toast.show('Failed to load security data', 'error');
        }
    }

    function renderFirewallRules(rules) {
        const tbody = document.getElementById('firewall-rules-tbody');
        if (!tbody) return;
        
        if (!rules || rules.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-border);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('No Data Available')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">No firewall rules found.</p>
    </div>
</td></tr>`;
            return;
        }

        tbody.innerHTML = rules.map(rule => `
            <tr>
                <td>${rule.port} / ${rule.protocol}</td>
                <td>
                    <span class="badge badge-${rule.action === 'allow' ? 'success' : 'danger'}">
                        ${rule.action.toUpperCase()}
                    </span>
                </td>
                <td>${rule.description || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="Toast.show('Action not implemented yet.', 'info')">Edit</button>
                </td>
            </tr>
        `).join('');
    }

    function renderSecurityAlerts(alerts) {
        const tbody = document.getElementById('security-alerts-tbody');
        if (!tbody) return;
        
        if (!alerts || alerts.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-border);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('No Data Available')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">No active security alerts.</p>
    </div>
</td></tr>`;
            return;
        }

        tbody.innerHTML = alerts.map(alert => `
            <tr>
                <td>${new Date(alert.timestamp).toLocaleString()}</td>
                <td><strong>${alert.title}</strong></td>
                <td>
                    <span class="badge badge-${getSeverityColor(alert.severity)}">
                        ${alert.severity.toUpperCase()}
                    </span>
                </td>
                <td>
                    <span class="badge badge-${alert.resolved ? 'success' : 'warning'}">
                        ${alert.resolved ? 'Resolved' : 'Active'}
                    </span>
                </td>
                <td>
                    ${!alert.resolved ? `<button class="btn btn-sm btn-outline" onclick="SecurityCenterPage.resolveAlert(${alert.id})">Resolve</button>` : '-'}
                </td>
            </tr>
        `).join('');
    }

    function renderSELinuxContexts(contexts) {
        const tbody = document.getElementById('selinux-contexts-tbody');
        if (!tbody) return;
        
        if (!contexts || contexts.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-border);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('No Data Available')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">No SELinux contexts configured.</p>
    </div>
</td></tr>`;
            return;
        }

        tbody.innerHTML = contexts.map(ctx => `
            <tr>
                <td><code>${ctx.file_path}</code></td>
                <td><code>${ctx.expected_context}</code></td>
                <td>
                    <span class="badge badge-${ctx.status === 'match' ? 'success' : 'danger'}">
                        ${ctx.status.toUpperCase()}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="Toast.show('Action not implemented yet.', 'info')">Restore</button>
                </td>
            </tr>
        `).join('');
    }

    function getSeverityColor(severity) {
        switch(severity) {
            case 'low': return 'info';
            case 'medium': return 'warning';
            case 'high': return 'danger';
            case 'critical': return 'danger';
            default: return 'secondary';
        }
    }

    async function resolveAlert(id) {
        try {
            await API.post(`/api/system-admin/security-alerts/${id}/resolve/`);
            Toast.show('Alert resolved successfully', 'success');
            loadData();
        } catch (error) {
            console.error('Failed to resolve alert:', error);
            Toast.show('Failed to resolve alert', 'error');
        }
    }

    function render(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h2>${window.t('Security Center')}</h2>
                    <p class="text-secondary">${window.t('Manage Firewall rules, SELinux, and view security alerts.')}</p>
                </div>
            </div>

            <!-- Security Alerts -->
            <div class="card mb-4">
                <div class="card-header">
                    <h3>${window.t('Security Alerts')}</h3>
                </div>
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>${window.t('Timestamp')}</th>
                                <th>${window.t('Title')}</th>
                                <th>${window.t('Severity')}</th>
                                <th>${window.t('Status')}</th>
                                <th>${window.t('Actions')}</th>
                            </tr>
                        </thead>
                        <tbody id="security-alerts-tbody">
                            <tr><td colspan="5" class="text-center py-4"><div style="display:flex;flex-direction:column;align-items:center;padding:32px 0;"><div class="spinner" style="margin-bottom:16px;"></div><p style="color:var(--clr-text-muted)">Loading...</p></div></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="row">
                <!-- Firewall Rules -->
                <div class="col-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h3 class="m-0">${window.t('Firewall Rules')}</h3>
                            <button class="btn btn-sm btn-primary" onclick="Toast.show('Action not implemented yet.', 'info')">
                                Add Rule
                            </button>
                        </div>
                        <div class="table-responsive">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>${window.t('Port / Protocol')}</th>
                                        <th>${window.t('Action')}</th>
                                        <th>${window.t('Description')}</th>
                                        <th>${window.t('Manage')}</th>
                                    </tr>
                                </thead>
                                <tbody id="firewall-rules-tbody">
                                    <tr><td colspan="4" class="text-center py-4"><div style="display:flex;flex-direction:column;align-items:center;padding:32px 0;"><div class="spinner" style="margin-bottom:16px;"></div><p style="color:var(--clr-text-muted)">Loading...</p></div></td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- SELinux Contexts -->
                <div class="col-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h3 class="m-0">${window.t('SELinux Contexts')}</h3>
                        </div>
                        <div class="table-responsive">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>${window.t('File Path')}</th>
                                        <th>${window.t('Expected Context')}</th>
                                        <th>${window.t('Status')}</th>
                                        <th>${window.t('Actions')}</th>
                                    </tr>
                                </thead>
                                <tbody id="selinux-contexts-tbody">
                                    <tr><td colspan="4" class="text-center py-4"><div style="display:flex;flex-direction:column;align-items:center;padding:32px 0;"><div class="spinner" style="margin-bottom:16px;"></div><p style="color:var(--clr-text-muted)">Loading...</p></div></td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;

        loadData();
    }

    return { render, resolveAlert };
})();

window.SecurityCenterPage = SecurityCenterPage;
