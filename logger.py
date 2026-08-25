"""Modulo de logging estruturado do FinancePro."""

import logging
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_FILE = LOG_DIR / "financeiro.log"


def setup_logging():
    """Configura o sistema de logging."""
    LOG_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    logger = logging.getLogger("financeiro")
    logger.info("Logging iniciado - FinancePro v4.0.0")
    return logger


logger = setup_logging()
