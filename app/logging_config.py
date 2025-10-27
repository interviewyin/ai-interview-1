"""Logging configuration for the LOS Key Validation Service

This module provides a custom formatter that displays extra fields as key-value pairs,
making it easier to track contextual information like client_id, key_id, etc.
"""

import logging


class ExtraFormatter(logging.Formatter):
    """Custom formatter that displays extra fields as key-value pairs"""

    # Standard logging record attributes to exclude from extra fields
    STANDARD_ATTRS = {
        'name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname',
        'levelno', 'lineno', 'module', 'msecs', 'message', 'pathname', 'process',
        'processName', 'relativeCreated', 'thread', 'threadName', 'exc_info',
        'exc_text', 'stack_info', 'asctime', 'taskName'
    }

    def format(self, record):
        # Get the base formatted message
        base_msg = super().format(record)

        # Find extra fields (anything not in standard attributes)
        extra_fields = {
            key: value for key, value in record.__dict__.items()
            if key not in self.STANDARD_ATTRS and not key.startswith('_')
        }

        # If there are extra fields, append them
        if extra_fields:
            extra_str = ' '.join(f'{k}={v}' for k, v in extra_fields.items())
            return f'{base_msg} [{extra_str}]'

        return base_msg


def setup_logging(level=logging.INFO):
    """Configure application logging with custom formatter

    Args:
        level: The logging level (default: logging.INFO)
    """
    handler = logging.StreamHandler()
    handler.setFormatter(ExtraFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))

    logging.root.setLevel(level)
    logging.root.addHandler(handler)
