import os
import re

dashboard_dir = r"r:\Craft\MicroServices Craft\services\admin-service\dashboard"
sysadmin_dir = r"r:\Craft\MicroServices Craft\services\admin-service\sysadmin_dashboard"

# 1. Clean up dashboard/app.html
with open(os.path.join(dashboard_dir, 'app.html'), 'r', encoding='utf-8') as f:
    html = f.read()
    
# Remove sysadmin scripts
sysadmin_scripts = [
    '<script src="/js/pages/servers.js?v=1"></script>',
    '<script src="/js/pages/services.js?v=1"></script>',
    '<script src="/js/pages/users-linux.js?v=1"></script>',
    '<script src="/js/pages/system-logs.js?v=1"></script>',
    '<script src="/js/pages/storage.js?v=1"></script>',
    '<script src="/js/pages/backups.js?v=1"></script>',
    '<script src="/js/pages/cron-jobs.js?v=1"></script>',
    '<script src="/js/pages/security-center.js?v=1"></script>',
    '<script src="/js/pages/config-management.js?v=1"></script>',
    '<script src="/js/pages/file-explorer.js?v=1"></script>',
    '<script src="/js/pages/containers.js?v=1"></script>',
    '<script src="/js/pages/incidents.js?v=1"></script>',
    '<script src="/js/pages/automation.js?v=1"></script>'
]
for s in sysadmin_scripts:
    html = html.replace(s + '\n', '').replace(s, '')
    
with open(os.path.join(dashboard_dir, 'app.html'), 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Clean up sysadmin_dashboard/app.html
# Need to rewrite the <script> tags to point to /sysadmin/js/ instead of /js/? Actually, maybe not if we serve it from /sysadmin/ path with the same static serving logic, but wait, the scripts have src="/js/...". This is absolute! We should change it to relative src="js/..." or src="/sysadmin/js/...".
# Let's change src="/js/..." to src="/sysadmin/js/..."
with open(os.path.join(sysadmin_dir, 'app.html'), 'r', encoding='utf-8') as f:
    syshtml = f.read()

# Replace all /css/ and /js/ with /sysadmin/css/ and /sysadmin/js/
syshtml = syshtml.replace('href="/css/', 'href="/sysadmin/css/')
syshtml = syshtml.replace('src="/js/', 'src="/sysadmin/js/')

ecommerce_scripts = [
    '<script src="/sysadmin/js/pages/overview.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/tasks.js?v=1"></script>',
    '<script src="/sysadmin/js/pages/approvals.js?v=1"></script>',
    '<script src="/sysadmin/js/pages/orders.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/returns.js?v=6"></script>',
    '<script src="/sysadmin/js/pages/products.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/users.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/payments.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/withdrawals.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/courses.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/reviews.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/coupons.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/reports.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/notifications.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/support-tickets.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/disputes.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/supplier-performance.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/delivery-performance.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/reconciliation.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/fraud-alerts.js?v=4"></script>',
    '<script src="/sysadmin/js/pages/product-moderation.js?v=5"></script>',
]
for s in ecommerce_scripts:
    syshtml = syshtml.replace(s + '\n', '').replace(s, '')

# Change title
syshtml = syshtml.replace('<title>Craft Dashboard</title>', '<title>Craft SysAdmin Portal</title>')

with open(os.path.join(sysadmin_dir, 'app.html'), 'w', encoding='utf-8') as f:
    f.write(syshtml)

# Clean up sidebar.js in dashboard
with open(os.path.join(dashboard_dir, 'js/components/sidebar.js'), 'r', encoding='utf-8') as f:
    sb = f.read()

# Remove infrastructure, security, operations, automation
sb_cleaned = re.sub(r"\{\s*section:\s*window\.t\('Infrastructure'\).*?\]\s*\},", "", sb, flags=re.DOTALL)
sb_cleaned = re.sub(r"\{\s*section:\s*window\.t\('Security'\).*?\]\s*\},", "", sb_cleaned, flags=re.DOTALL)
sb_cleaned = re.sub(r"\{\s*section:\s*window\.t\('Operations'\).*?\]\s*\},", "", sb_cleaned, flags=re.DOTALL)
sb_cleaned = re.sub(r"\{\s*section:\s*window\.t\('Automation'\).*?\]\s*\},", "", sb_cleaned, flags=re.DOTALL)

with open(os.path.join(dashboard_dir, 'js/components/sidebar.js'), 'w', encoding='utf-8') as f:
    f.write(sb_cleaned)

# Clean up sidebar.js in sysadmin_dashboard
with open(os.path.join(sysadmin_dir, 'js/components/sidebar.js'), 'r', encoding='utf-8') as f:
    sys_sb = f.read()

sys_sb_cleaned = re.sub(r"\{\s*section:\s*window\.t\('Main'\).*?\]\s*\},", "", sys_sb, flags=re.DOTALL)
sys_sb_cleaned = re.sub(r"\{\s*section:\s*window\.t\('Management'\).*?\]\s*\},", "", sys_sb_cleaned, flags=re.DOTALL)
sys_sb_cleaned = re.sub(r"\{\s*section:\s*window\.t\('Operations'\),\s*items:\s*\[.*?support-tickets.*?\].*?\],?", "", sys_sb_cleaned, flags=re.DOTALL)
sys_sb_cleaned = re.sub(r"\{\s*section:\s*window\.t\('Content'\).*?\]\s*\},", "", sys_sb_cleaned, flags=re.DOTALL)
sys_sb_cleaned = sys_sb_cleaned.replace("window.t('Craft Dashboard')", "window.t('Craft SysAdmin')")
sys_sb_cleaned = sys_sb_cleaned.replace("logo.jpg", "/sysadmin/logo.jpg")

with open(os.path.join(sysadmin_dir, 'js/components/sidebar.js'), 'w', encoding='utf-8') as f:
    f.write(sys_sb_cleaned)

print("Cleanup script executed.")
