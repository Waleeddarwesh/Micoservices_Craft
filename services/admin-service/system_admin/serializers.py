from rest_framework import serializers
from .models import Server, AuditLog, Service, LinuxUser, CronJob, Incident, OperationalScript

class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class LinuxUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinuxUser
        fields = '__all__'

class CronJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CronJob
        fields = '__all__'

class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = '__all__'

class OperationalScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationalScript
        fields = '__all__'

from .models import DiskVolume, LogicalVolume, BackupJob

class DiskVolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiskVolume
        fields = '__all__'

class LogicalVolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogicalVolume
        fields = '__all__'

class BackupJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupJob
        fields = '__all__'

from .models import FirewallRule, SecurityAlert, SELinuxContext

class FirewallRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirewallRule
        fields = '__all__'

class SecurityAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityAlert
        fields = '__all__'

class SELinuxContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = SELinuxContext
        fields = '__all__'

from .models import Container, SystemLog

class ContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Container
        fields = '__all__'

class SystemLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemLog
        fields = '__all__'
