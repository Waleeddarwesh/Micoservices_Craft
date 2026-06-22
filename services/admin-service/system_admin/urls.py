from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServerViewSet, AuditLogViewSet, ServiceViewSet, 
    LinuxUserViewSet, CronJobViewSet, IncidentViewSet, OperationalScriptViewSet,
    DiskVolumeViewSet, LogicalVolumeViewSet, BackupJobViewSet,
    FirewallRuleViewSet, SecurityAlertViewSet, SELinuxContextViewSet,
    ContainerViewSet, SystemLogViewSet
)

router = DefaultRouter()
router.register(r'servers', ServerViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'linux-users', LinuxUserViewSet)
router.register(r'cron-jobs', CronJobViewSet)
router.register(r'incidents', IncidentViewSet)
router.register(r'scripts', OperationalScriptViewSet)
router.register(r'disk-volumes', DiskVolumeViewSet)
router.register(r'logical-volumes', LogicalVolumeViewSet)
router.register(r'backup-jobs', BackupJobViewSet)
router.register(r'firewall-rules', FirewallRuleViewSet)
router.register(r'security-alerts', SecurityAlertViewSet)
router.register(r'selinux-contexts', SELinuxContextViewSet)
router.register(r'containers', ContainerViewSet)
router.register(r'system-logs', SystemLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
