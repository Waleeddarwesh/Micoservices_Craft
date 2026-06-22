from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Server, AuditLog, Service, LinuxUser, CronJob, Incident, OperationalScript
from .serializers import (
    ServerSerializer, AuditLogSerializer, ServiceSerializer, 
    LinuxUserSerializer, CronJobSerializer, IncidentSerializer, OperationalScriptSerializer
)
from .utils import run_system_command

class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    permission_classes = [IsAuthenticated]

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def execute_command(self, request, pk=None):
        service = self.get_object()
        cmd_action = request.data.get('action') # start, stop, restart, status
        if cmd_action not in ['start', 'stop', 'restart', 'status']:
            return Response({'error': 'Invalid action'}, status=400)
            
        # Example for local execution: systemctl start nginx
        result = run_system_command(['sudo', 'systemctl', cmd_action, service.service_name])
        return Response(result)

class LinuxUserViewSet(viewsets.ModelViewSet):
    queryset = LinuxUser.objects.all()
    serializer_class = LinuxUserSerializer
    permission_classes = [IsAuthenticated]

class CronJobViewSet(viewsets.ModelViewSet):
    queryset = CronJob.objects.all()
    serializer_class = CronJobSerializer
    permission_classes = [IsAuthenticated]

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]

class OperationalScriptViewSet(viewsets.ModelViewSet):
    queryset = OperationalScript.objects.all()
    serializer_class = OperationalScriptSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        script = self.get_object()
        # In a real environment, you'd write the script to a temp file and execute it
        # For security, extreme caution is needed here.
        return Response({'success': True, 'output': f'Mock execution of {script.name} completed.'})

from .models import DiskVolume, LogicalVolume, BackupJob
from .serializers import DiskVolumeSerializer, LogicalVolumeSerializer, BackupJobSerializer

class DiskVolumeViewSet(viewsets.ModelViewSet):
    queryset = DiskVolume.objects.all()
    serializer_class = DiskVolumeSerializer
    permission_classes = [IsAuthenticated]

class LogicalVolumeViewSet(viewsets.ModelViewSet):
    queryset = LogicalVolume.objects.all()
    serializer_class = LogicalVolumeSerializer
    permission_classes = [IsAuthenticated]

class BackupJobViewSet(viewsets.ModelViewSet):
    queryset = BackupJob.objects.all()
    serializer_class = BackupJobSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def run_backup(self, request, pk=None):
        job = self.get_object()
        # Mocking the backup run
        import datetime
        job.last_run = datetime.datetime.now()
        job.save()
        return Response({'success': True, 'output': f'Backup {job.name} completed successfully.'})

from .models import FirewallRule, SecurityAlert, SELinuxContext
from .serializers import FirewallRuleSerializer, SecurityAlertSerializer, SELinuxContextSerializer

class FirewallRuleViewSet(viewsets.ModelViewSet):
    queryset = FirewallRule.objects.all()
    serializer_class = FirewallRuleSerializer
    permission_classes = [IsAuthenticated]

class SecurityAlertViewSet(viewsets.ModelViewSet):
    queryset = SecurityAlert.objects.all()
    serializer_class = SecurityAlertSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.resolved = True
        alert.save()
        return Response({'success': True, 'message': 'Alert marked as resolved.'})

class SELinuxContextViewSet(viewsets.ModelViewSet):
    queryset = SELinuxContext.objects.all()
    serializer_class = SELinuxContextSerializer
    permission_classes = [IsAuthenticated]

from .models import Container, SystemLog
from .serializers import ContainerSerializer, SystemLogSerializer

class ContainerViewSet(viewsets.ModelViewSet):
    queryset = Container.objects.all()
    serializer_class = ContainerSerializer
    permission_classes = [IsAuthenticated]

class SystemLogViewSet(viewsets.ModelViewSet):
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [IsAuthenticated]
