"""General eleanor utilities"""
import os
import logging
import logging.config
import time


def get_logger(module_name):
    """Get a logger with created with values from settings/logging.conf and
    using time.gmtime
    """
    here = os.path.abspath(os.path.dirname(__file__))
    logging_conf_path = '{0}/{1}'.format(here, 'settings/logging.conf')
    logging.config.fileConfig(logging_conf_path)
    logging.Formatter.converter = time.gmtime
    logger = logging.getLogger(module_name)
    return logger
