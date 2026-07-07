import logging
import os

LOG_DIR = "logs"
LOG_FILE = "dealhunter.log"

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("DealHunterAI")
