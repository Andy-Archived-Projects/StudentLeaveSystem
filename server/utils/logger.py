# -*- coding: utf-8 -*-
import logging
import os
from colorlog import ColoredFormatter

from utils import constant
from utils import functions as func


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
    file_fmt = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s',
                                 datefmt='%Y-%m-%d %H:%M:%S',)

    def __init__(self):
        if not os.path.isdir(constant.LOG_FOLDER):
            os.mkdir(constant.LOG_FOLDER)
        self.logger = logging.getLogger('StudentLeaveSystem')
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

        func.make_log_backup()
        ch = logging.StreamHandler()
        ch.setFormatter(self.console_fmt)
        fh = logging.FileHandler(constant.LATEST_LOG_FILE, encoding='utf8')
        fh.setFormatter(self.file_fmt)

        self.logger.addHandler(ch)
        self.logger.addHandler(fh)
        self.logger.setLevel(logging.DEBUG)

        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical
        self.exception = self.logger.exception
        self.set_level = self.logger.setLevel
