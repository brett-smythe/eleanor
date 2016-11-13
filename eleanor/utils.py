"""General eleanor utilities"""
import os
import logging
import logging.config
import time

eleanor_logger = logging.getLogger('eleanor')
eleanor_logger.setLevel(logging.DEBUG)
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
eleanor_logger.addHandler(handler)
eleanor_logger.propagate = False
