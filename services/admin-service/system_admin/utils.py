import subprocess
import logging

logger = logging.getLogger(__name__)

def run_system_command(command, shell=False):
    """
    Executes a system command securely.
    :param command: List of command arguments or string if shell=True.
    :param shell: Boolean indicating whether to run via shell.
    :return: dict with 'success', 'output', 'error', 'returncode'
    """
    try:
        # Note: In production, consider adding timeout and further sanitization.
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'error': result.stderr.strip(),
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {command}")
        return {'success': False, 'output': '', 'error': 'Command timed out', 'returncode': -1}
    except Exception as e:
        logger.exception(f"Error executing command: {command}")
        return {'success': False, 'output': '', 'error': str(e), 'returncode': -1}
