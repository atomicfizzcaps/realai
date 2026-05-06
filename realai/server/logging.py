"""Structured logging helpers for the RealAI server."""

import json
import logging
import sys
import time

_DEFAULT_LOGGER_NAME = 'realai.server'


def get_logger(name=_DEFAULT_LOGGER_NAME):
    """Return a configured logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def log_event(level, event, **fields):
    """Emit a structured JSON log line."""
    payload = {
        'timestamp': int(time.time()),
        'event': event,
    }
    payload.update(fields)
    get_logger().log(level, json.dumps(payload, sort_keys=True))
