from django.db import connection
cursor = connection.cursor()
tables = [
    'system_admin_firewallrule',
    'system_admin_securityalert',
    'system_admin_selinuxcontext',
    'system_admin_backupjob',
    'system_admin_diskvolume',
    'system_admin_logicalvolume',
    'system_admin_incident',
    'system_admin_cronjob',
    'system_admin_linuxuser',
    'system_admin_service',
    'system_admin_auditlog',
    'system_admin_operationalscript',
    'system_admin_server'
]
for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
cursor.execute("DELETE FROM django_migrations WHERE app='system_admin';")
print("Dropped system_admin tables and migrations.")
