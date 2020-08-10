# -*- coding: utf-8 -*-
import os

SERVER_HOST = '127.0.0.1'
SERVER_PORT = '25300'

DATA_FOLDER = 'data'
USER_DATA_FILE = os.path.join(DATA_FOLDER, 'user_data.json')
LEAVE_FILE = os.path.join(DATA_FOLDER, 'leave.json')

# Log
LOG_FOLDER = 'log'
LATEST_LOG_FILE = os.path.join(LOG_FOLDER, 'latest.log')
