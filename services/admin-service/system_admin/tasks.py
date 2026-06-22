import logging
from celery import shared_task
from django.core.management import call_command

logger = logging.getLogger(__name__)

@shared_task
def sync_system_data():
    """
    Periodic task to synchronize real OS metrics into the system_admin database models.
    Calls the custom management command 'sync_sysadmin'.
    """
    logger.info("Starting background synchronization of system metrics...")
    try:
        call_command('sync_sysadmin')
        logger.info("System metrics synchronized successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to synchronize system metrics: {str(e)}")
        return False
