# coding: utf-8

import logging
import logging.config

CONFIGURATION_LOGGER_FILE = 'config/logging.ini'


class LoggerSingleton(object):
    """
    import logging
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger('my_logger')
    logger.warning('And this message comes from another module')
    """

    _logger = None

    def __new__(cls, logger=None):
        if not cls._logger:
            logger_manager = LoggerManager(logger)
            cls._logger = logger_manager.logger
            return cls._logger
        else:
            cls._logger.debug('Singleton logger is already created')
            return cls._logger


class LoggerManager(object):
    logger = None
    enabled = True

    def __init__(self, logger=None, logger_enabled=True):
        if logger:
            self.logger = logger
        elif not self.logger:
            self.set_default_logger()
        self.logger_enabled = logger_enabled

    def set_logger(self, logger):
        self.logger = logger

    def set_default_logger(self, logger_enabled=True, log_level=logging.INFO):

            logger = logging.getLogger('default_logger')
            logger.setLevel(log_level)
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            self.logger = logger
            self.logger_enabled = logger_enabled

    def enable(self):
        self.logger.propagate = True
        self.enabled = True

    def disable(self):
        self.logger.propagate = False
        self.enabled = False

