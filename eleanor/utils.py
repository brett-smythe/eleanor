"""General eleanor utilities"""
import os
import logging
import logging.config
import time


def get_logger():
    """Get a logger with created with values from settings/logging.conf and
    using time.gmtime
    """

    logger = logging.getLogger('eleanor')
    logger.setLevel(logging.DEBUG)
    if 'RUN_ENV' in os.environ:
        if os.environ['RUN_ENV'] == 'production':
            handler = logging.handlers.TimedRotatingFileHandler(
                '/var/log/eleanor/eleanor.log', 'midnight', 1, 0, 'utf-8',
                False, True
            )
    else:
        handler = logging.handlers.TimedRotatingFileHandler(
            '/tmp/eleanor.log', 'midnight', 1, 0, 'utf-8', False,
            True
        )
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

eleanor_logger = get_logger()
