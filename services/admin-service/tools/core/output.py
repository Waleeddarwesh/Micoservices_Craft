import logging

# Set up logging globally
logger = logging.getLogger("craft_tools")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def setup_output(verbose=False, quiet=False):
    if quiet:
        logger.setLevel(logging.CRITICAL)
    elif verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

def print_info(message):
    logger.info(f"[*] {message}")

def print_success(message):
    logger.info(f"[+] {message}")

def print_warning(message):
    logger.warning(f"[!] {message}")

def print_error(message):
    logger.error(f"[ERROR] {message}")

def print_debug(message):
    logger.debug(f"[DEBUG] {message}")

def print_raw(message):
    logger.info(message)
