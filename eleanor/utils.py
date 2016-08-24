"""General eleanor utilities"""
import logging
import logging.config
import time

dev = False


def get_logger(module_name):
    """Get a logger with created with values from settings/logging.conf and
    using time.gmtime
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)
    if dev:
        handler = logging.handlers.TimedRotatingFileHandler(
            '/tmp/eleanor.log', 'midnight', 1, 0, 'utf-8', False,
            True
        )
    else:
        handler = logging.handlers.TimedRotatingFileHandler(
            '/var/log/eleanor/eleanor.log', 'midnight', 1, 0, 'utf-8', False,
            True
        )
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
