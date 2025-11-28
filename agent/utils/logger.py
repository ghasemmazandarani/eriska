import logging
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class CustomFormatter(logging.Formatter):
    format_str = "%(asctime)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: Fore.CYAN + format_str + Style.RESET_ALL,
        logging.INFO: Fore.GREEN + format_str + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + format_str + Style.RESET_ALL,
        logging.ERROR: Fore.RED + format_str + Style.RESET_ALL,
        logging.CRITICAL: Fore.RED + Style.BRIGHT + format_str + Style.RESET_ALL
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)

def setup_logger(name="EriskaAgent", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(CustomFormatter())

    if not logger.handlers:
        logger.addHandler(ch)

    return logger

log = setup_logger()
