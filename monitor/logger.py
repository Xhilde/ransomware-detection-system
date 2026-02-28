import logging
import os

# Ensure logs directory exists (relative to project root)
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "alerts.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

def log_info(message):
    logging.info(message)

def log_warning(message):
    logging.warning(message)

def log_critical(message):
    logging.critical(message)