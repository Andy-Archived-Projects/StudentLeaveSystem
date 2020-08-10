# -*- coding: utf-8 -*-
import logging
from colorlog import ColoredFormatter


class Logger:
    console_fmt = ColoredFormatter(
        '[%(asctime)s] [%(log_color)s%(levelname)s%(reset)s]: '
        '%(message_log_color)s%(message)s%(reset)s',
        log_colors={
            'DEBUG': 'blue',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        },
        secondary_log_colors={
            'message': {
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red'
            }
        },
        datefmt='%H:%M:%S'
    )

    def __init__(self):
        self.logger = logging.getLogger('Client')
        ch = logging.StreamHandler()
        ch.setFormatter(self.console_fmt)

        self.logger.addHandler(ch)
        self.logger.setLevel(logging.INFO)

        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical
        self.exception = self.logger.exception
        self.set_level = self.logger.setLevel
