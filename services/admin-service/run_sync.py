from system_admin.models import Server, DiskVolume, LinuxUser, Service
from system_admin.system_monitor import get_server_info, get_disk_volumes, get_linux_users, get_running_services
from django.utils import timezone

print("Starting dynamic system metrics sync...")

server_info = get_server_info()
server, created = Server.objects.update_or_create(
    hostname=server_info['hostname'],
    defaults={
        'ip_address': server_info['ip_address'],
        'os_type': server_info['os_type'],
        'os_version': server_info['os_version'],
        'environment': server_info['environment'],
        'status': server_info['status'],
        'last_seen': timezone.now()
    }
)
print(f"Synced Server: {server.hostname}")

DiskVolume.objects.filter(server=server).delete()
volumes = get_disk_volumes()
for vol in volumes:
    DiskVolume.objects.create(
        server=server,
        mount_point=vol['mount_point'],
        size=vol['size'],
        used=vol['used'],
        available=vol['available'],
        health=vol['health']
    )
print(f"Synced {len(volumes)} Disk Volumes")

LinuxUser.objects.filter(server=server).delete()
users = get_linux_users()
for u in users:
    LinuxUser.objects.create(
        server=server,
        username=u['username'],
        group=u['group'],
        sudo_access=u['sudo_access'],
        status=u['status']
    )
print(f"Synced {len(users)} Linux Users")

Service.objects.filter(server=server).delete()
services = get_running_services()
for s in services:
    Service.objects.create(
        server=server,
        service_name=s['service_name'],
        service_type=s['service_type'],
        status=s['status'],
        last_restart=s['last_restart']
    )
print(f"Synced {len(services)} Services")

print("System sync completed successfully!")
