"""Logging-Konfiguration für TimeTracker."""

import logging
from config import LOG_FORMAT, LOG_LEVEL, LOG_PATH


def setup_logger(name: str) -> logging.Logger:
    """Richte einen Logger auf.
    
    Args:
        name: Name des Loggers (normalerweise __name__)
        
    Returns:
        logging.Logger: Konfigurierter Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Verhindere doppelte Handler
    if logger.handlers:
        return logger
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    # File Handler
    file_handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    
    # Handler hinzufügen
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
