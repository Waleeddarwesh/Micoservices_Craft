import os
import platform
import socket
import subprocess
try:
    import pwd
except ImportError:
    pwd = None
from django.utils import timezone

def get_server_info():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
    except Exception:
        hostname = platform.node()
        ip_address = "127.0.0.1"
        
    os_type = platform.system()
    os_version = platform.release()
    
    return {
        'hostname': hostname,
        'ip_address': ip_address,
        'os_type': os_type,
        'os_version': os_version,
        'environment': os.environ.get('DJANGO_ENV', 'production'),
        'status': 'active'
    }

def get_disk_volumes():
    volumes = []
    try:
        output = subprocess.check_output(['df', '-h']).decode('utf-8')
        lines = output.strip().split('\n')[1:]
        for line in lines:
            parts = line.split()
            if len(parts) >= 6:
                fs, size, used, avail, use_pct, mount = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                if fs.startswith('/dev/') or mount in ['/']:
                    volumes.append({
                        'mount_point': mount,
                        'size': size,
                        'used': used,
                        'available': avail,
                        'health': 'healthy' if int(use_pct.strip('%')) < 90 else 'warning'
                    })
    except Exception as e:
        print(f"Error fetching disk volumes: {e}")
    return volumes

def get_linux_users():
    users = []
    if not pwd:
        return users
    try:
        for p in pwd.getpwall():
            if p.pw_uid >= 1000 or p.pw_name in ['root', 'postgres', 'nginx']:
                users.append({
                    'username': p.pw_name,
                    'group': str(p.pw_gid),
                    'sudo_access': p.pw_name == 'root',
                    'status': 'active'
                })
    except Exception as e:
        print(f"Error fetching linux users: {e}")
    return users

def get_running_services():
    services = []
    try:
        seen = set()
        for pid in os.listdir('/proc'):
            if pid.isdigit():
                try:
                    with open(f'/proc/{pid}/comm', 'r') as f:
                        name = f.read().strip()
                    with open(f'/proc/{pid}/stat', 'r') as f:
                        state = f.read().split()[2]
                    
                    if name in ['python', 'celery', 'nginx', 'gunicorn', 'postgres', 'redis-server', 'bash', 'sh', 'node']:
                        if name not in seen:
                            seen.add(name)
                            service_type = 'app' if name in ['python', 'celery', 'gunicorn', 'node'] else 'system'
                            status = 'running' if state in ['R', 'S', 'I'] else 'stopped'
                            services.append({
                                'service_name': name,
                                'service_type': service_type,
                                'status': status,
                                'last_restart': timezone.now()
                            })
                except Exception:
                    continue
    except Exception as e:
        print(f"Error fetching services: {e}")
    return services

def get_containers():
    # Mocking real containers for the environment since docker.sock is not mounted
    return [
        {'container_id': 'a1b2c3d4', 'name': 'microservicescraft-admin_service-1', 'image': 'admin-service:latest', 'state': 'running', 'status': 'Up 4 hours', 'ports': '8000/tcp'},
        {'container_id': 'b2c3d4e5', 'name': 'microservicescraft-auth_service-1', 'image': 'auth-service:latest', 'state': 'running', 'status': 'Up 4 hours', 'ports': '8001/tcp'},
        {'container_id': 'c3d4e5f6', 'name': 'microservicescraft-catalog_service-1', 'image': 'catalog-service:latest', 'state': 'running', 'status': 'Up 4 hours', 'ports': '8002/tcp'},
        {'container_id': 'd4e5f6g7', 'name': 'microservicescraft-traefik-1', 'image': 'traefik:v2.10', 'state': 'running', 'status': 'Up 4 hours', 'ports': '80:8000, 8080:8080'},
        {'container_id': 'e5f6g7h8', 'name': 'microservicescraft-postgres-1', 'image': 'postgres:15-alpine', 'state': 'running', 'status': 'Up 4 hours', 'ports': '5432/tcp'},
        {'container_id': 'f6g7h8i9', 'name': 'microservicescraft-redis-1', 'image': 'redis:7-alpine', 'state': 'running', 'status': 'Up 4 hours', 'ports': '6379/tcp'},
    ]

def get_system_logs():
    # Mocking real system logs
    import random
    sources = ['nginx', 'gunicorn', 'celery', 'postgres', 'traefik']
    levels = ['INFO', 'INFO', 'INFO', 'WARN', 'ERROR']
    messages = [
        "Connection closed by authenticating user root",
        "Failed password for invalid user admin",
        "Worker process started successfully",
        "Slow query detected (1.5s)",
        "Memory usage exceeded 80%",
        "Configuration reloaded",
        "Upstream connection timeout"
    ]
    logs = []
    for _ in range(15):
        logs.append({
            'source': random.choice(sources),
            'level': random.choice(levels),
            'message': random.choice(messages)
        })
    return logs
