from django.core.management.base import BaseCommand
from system_admin.models import Server, DiskVolume, LinuxUser, Service
from system_admin.system_monitor import get_server_info, get_disk_volumes, get_linux_users, get_running_services
from django.utils import timezone

class Command(BaseCommand):
    help = 'Synchronizes real OS metrics into the system_admin database models.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting dynamic system metrics sync..."))
        
        # 1. Update/Create Server
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
        self.stdout.write(self.style.SUCCESS(f"Synced Server: {server.hostname}"))

        # 2. Sync Disk Volumes
        DiskVolume.objects.filter(server=server).delete() # Wipe old
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
        self.stdout.write(self.style.SUCCESS(f"Synced {len(volumes)} Disk Volumes"))

        # 3. Sync Linux Users
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
        self.stdout.write(self.style.SUCCESS(f"Synced {len(users)} Linux Users"))

        # 4. Sync Services
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
        self.stdout.write(self.style.SUCCESS(f"Synced {len(services)} Services"))

        # 5. Sync Containers
        from system_admin.models import Container, SystemLog
        from system_admin.system_monitor import get_containers, get_system_logs
        Container.objects.filter(server=server).delete()
        containers = get_containers()
        for c in containers:
            Container.objects.create(
                server=server,
                container_id=c['container_id'],
                name=c['name'],
                image=c['image'],
                state=c['state'],
                status=c['status'],
                ports=c['ports']
            )
        self.stdout.write(self.style.SUCCESS(f"Synced {len(containers)} Containers"))

        # 6. Sync System Logs
        SystemLog.objects.filter(server=server).delete()
        syslogs = get_system_logs()
        for l in syslogs:
            SystemLog.objects.create(
                server=server,
                source=l['source'],
                level=l['level'],
                message=l['message']
            )
        self.stdout.write(self.style.SUCCESS(f"Synced {len(syslogs)} System Logs"))

        self.stdout.write(self.style.SUCCESS("System sync completed successfully!"))
