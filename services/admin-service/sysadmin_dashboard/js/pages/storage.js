const StoragePage = (() => {
    function render(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h2>${window.t('Storage Administration')}</h2>
                    <p class="text-secondary">${window.t('Manage disks, mounts, and LVM volumes.')}</p>
                </div>
                <div class="header-actions">
                    <button class="btn btn-primary" onclick="Toast.show('Add volume functionality not implemented yet.', 'info')">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        ${window.t('New Volume')}
                    </button>
                </div>
            </div>

            <!-- Disk Volumes Section -->
            <h3 class="mt-4 mb-3">${window.t('Disk Volumes')}</h3>
            <div class="card mb-4">
                <div class="table-responsive">
                    <table class="table" id="disk-table">
                        <thead>
                            <tr>
                                <th>${window.t('Mount Point')}</th>
                                <th>${window.t('Server')}</th>
                                <th>${window.t('Size')}</th>
                                <th>${window.t('Used')}</th>
                                <th>${window.t('Available')}</th>
                                <th>${window.t('Health')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="6" class="text-center py-4"><div style="display:flex;flex-direction:column;align-items:center;padding:32px 0;"><div class="spinner" style="margin-bottom:16px;"></div><p style="color:var(--clr-text-muted)">Loading disks...</p></div></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Logical Volumes Section -->
            <h3 class="mb-3">${window.t('Logical Volumes (LVM)')}</h3>
            <div class="card">
                <div class="table-responsive">
                    <table class="table" id="lvm-table">
                        <thead>
                            <tr>
                                <th>${window.t('VG Name')}</th>
                                <th>${window.t('LV Name')}</th>
                                <th>${window.t('Server')}</th>
                                <th>${window.t('Size')}</th>
                                <th>${window.t('Status')}</th>
                                <th>${window.t('Actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="6" class="text-center py-4"><div style="display:flex;flex-direction:column;align-items:center;padding:32px 0;"><div class="spinner" style="margin-bottom:16px;"></div><p style="color:var(--clr-text-muted)">Loading logical volumes...</p></div></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        loadData();
    }

    async function loadData() {
        try {
            // Load Disks
            const disks = await API.get('/api/system-admin/disk-volumes/');
            const diskTbody = document.querySelector('#disk-table tbody');
            if (!disks || disks.length === 0) {
                diskTbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-border);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('No Data Available')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">${window.t('No disk volumes found.')}</p>
    </div>
</td></tr>`;
            } else {
                diskTbody.innerHTML = disks.map(disk => `
                    <tr>
                        <td class="font-medium"><code>${disk.mount_point}</code></td>
                        <td>${disk.server ? `Server #${disk.server}` : 'Local'}</td>
                        <td>${disk.size}</td>
                        <td>${disk.used}</td>
                        <td>${disk.available}</td>
                        <td>
                            <span class="badge badge-${disk.health === 'healthy' ? 'success' : 'danger'}">${disk.health}</span>
                        </td>
                    </tr>
                `).join('');
            }

            // Load LVMs
            const lvms = await API.get('/api/system-admin/logical-volumes/');
            const lvmTbody = document.querySelector('#lvm-table tbody');
            if (!lvms || lvms.length === 0) {
                lvmTbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-border);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('No Data Available')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">${window.t('No logical volumes found.')}</p>
    </div>
</td></tr>`;
            } else {
                lvmTbody.innerHTML = lvms.map(lvm => `
                    <tr>
                        <td class="font-medium">${lvm.vg_name}</td>
                        <td class="font-medium">${lvm.lv_name}</td>
                        <td>${lvm.server ? `Server #${lvm.server}` : 'Local'}</td>
                        <td>${lvm.size}</td>
                        <td>
                            <span class="badge badge-${lvm.status === 'active' ? 'success' : 'warning'}">${lvm.status}</span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-outline" onclick="Toast.show('Extend functionality coming soon', 'info')">${window.t('Extend')}</button>
                        </td>
                    </tr>
                `).join('');
            }

        } catch (error) {
            console.error('Error loading storage data:', error);
            document.querySelector('#disk-table tbody').innerHTML = 
                `<tr><td colspan="6" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-danger);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('Error')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">${window.t('Failed to load storage data')}</p>
    </div>
</td></tr>`;
            document.querySelector('#lvm-table tbody').innerHTML = 
                `<tr><td colspan="6" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:var(--clr-danger);margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">${window.t('Error')}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">${window.t('Failed to load storage data')}</p>
    </div>
</td></tr>`;
        }
    }

    return { render, loadData };
})();

window.StoragePage = StoragePage;
