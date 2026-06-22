from system_admin.models import Server, Service, LinuxUser, CronJob, Incident, OperationalScript, DiskVolume, LogicalVolume, BackupJob, FirewallRule, SecurityAlert, SELinuxContext
from accounts.models import User
from django.utils import timezone
import datetime
import random

print("Starting data seed for system_admin...")

# Clean up existing data just in case
Server.objects.all().delete()
AuditLog.objects.all().delete() if 'AuditLog' in globals() else None

# Create Servers
s1 = Server.objects.create(hostname="prod-web-01", ip_address="192.168.1.10", os_type="Ubuntu", os_version="22.04 LTS", environment="production", status="active")
s2 = Server.objects.create(hostname="prod-db-01", ip_address="192.168.1.20", os_type="CentOS", os_version="8 Stream", environment="production", status="active")
s3 = Server.objects.create(hostname="stage-app-01", ip_address="192.168.2.15", os_type="Debian", os_version="11", environment="staging", status="maintenance")
servers = [s1, s2, s3]

# Create Services
Service.objects.create(server=s1, service_name="nginx", service_type="web", status="running", last_restart=timezone.now() - datetime.timedelta(days=2))
Service.objects.create(server=s1, service_name="gunicorn", service_type="app", status="running", last_restart=timezone.now() - datetime.timedelta(days=1))
Service.objects.create(server=s2, service_name="postgresql", service_type="database", status="running", last_restart=timezone.now() - datetime.timedelta(days=15))
Service.objects.create(server=s3, service_name="redis", service_type="cache", status="stopped", last_restart=timezone.now() - datetime.timedelta(days=5))

# Create Linux Users
LinuxUser.objects.create(server=s1, username="admin_deploy", group="wheel", sudo_access=True, status="active")
LinuxUser.objects.create(server=s1, username="nginx", group="www-data", sudo_access=False, status="active")
LinuxUser.objects.create(server=s2, username="postgres", group="postgres", sudo_access=False, status="active")
LinuxUser.objects.create(server=s3, username="dev_tester", group="developers", sudo_access=False, status="locked")

# Create Cron Jobs
CronJob.objects.create(server=s2, name="Database Backup", schedule="0 2 * * *", command="/usr/local/bin/pg_backup.sh", user="postgres", status="active")
CronJob.objects.create(server=s1, name="Log Rotation", schedule="0 0 * * *", command="logrotate /etc/logrotate.conf", user="root", status="active")

# Create Incidents
Incident.objects.create(title="High CPU Usage on Web Node", description="CPU usage spiked to 99% for 10 minutes.", severity="medium", status="investigating", server=s1)
Incident.objects.create(title="Database Replication Lag", description="Replica is lagging behind master by 5 minutes.", severity="high", status="open", server=s2)
Incident.objects.create(title="Staging server out of memory", description="OOM killer terminated the application.", severity="low", status="resolved", server=s3, resolved_at=timezone.now())

# Create Scripts
OperationalScript.objects.create(name="Clear Cache", description="Clears Redis cache", script_content="redis-cli flushall", interpreter="/bin/bash")
OperationalScript.objects.create(name="Restart Web Services", description="Restarts Nginx and Gunicorn", script_content="systemctl restart nginx\nsystemctl restart gunicorn", interpreter="/bin/bash")

# Create Disk Volumes
DiskVolume.objects.create(server=s1, mount_point="/", size="50GB", used="20GB", available="30GB", health="healthy")
DiskVolume.objects.create(server=s2, mount_point="/var/lib/postgresql", size="500GB", used="350GB", available="150GB", health="warning")

# Create Logical Volumes
LogicalVolume.objects.create(server=s2, vg_name="vg_data", lv_name="lv_postgres", size="500GB", status="active")

# Create Backup Jobs
BackupJob.objects.create(server=s2, name="Daily PostgreSQL Full Backup", backup_type="Database", schedule="0 2 * * *", status="active", last_run=timezone.now() - datetime.timedelta(hours=14))
BackupJob.objects.create(server=s1, name="Weekly Media Backup", backup_type="Filesystem", schedule="0 3 * * 0", status="active", last_run=timezone.now() - datetime.timedelta(days=3))

# Create Firewall Rules
FirewallRule.objects.create(server=s1, port="80", protocol="tcp", action="allow", description="Allow HTTP")
FirewallRule.objects.create(server=s1, port="443", protocol="tcp", action="allow", description="Allow HTTPS")
FirewallRule.objects.create(server=s2, port="5432", protocol="tcp", action="allow", description="Allow Postgres from private subnet")

# Create Security Alerts
SecurityAlert.objects.create(server=s1, title="Multiple failed SSH logins", severity="high", message="15 failed login attempts from IP 203.0.113.4", resolved=False)
SecurityAlert.objects.create(server=s3, title="Outdated packages", severity="low", message="5 packages require security updates.", resolved=True)

# Create SELinux Contexts
SELinuxContext.objects.create(server=s1, file_path="/var/www/html", expected_context="httpd_sys_content_t", current_context="httpd_sys_content_t", status="match")
SELinuxContext.objects.create(server=s2, file_path="/var/lib/pgsql/data", expected_context="postgresql_db_t", current_context="unconfined_u:object_r:default_t:s0", status="mismatch")

print("Data seed complete!")
