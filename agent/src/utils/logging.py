"""Shared logger configuration."""

import logging

from .config import config

logging.basicConfig(
    level=config.log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger("patient_agent")
