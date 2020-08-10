# -*- coding: utf-8 -*-
import os
import yaml


class Config:
    def __init__(self):
        self.data = None
        self.path = 'config.yml'
        if os.path.isfile(self.path):
            with open(self.path, encoding='utf8') as file:
                self.data = yaml.safe_load(file)
        self.check_config()

    def touch(self, key, default):
        if self.data is None:
            self.data = {}
        if key not in self.data:
            self.data[key] = default
            with open(self.path, 'a', encoding='utf8') as file:
                yaml.safe_dump({key: default}, file)

    def check_config(self):
        self.touch('language', 'zh_cn')
        self.touch('server_host', '98.126.219.155')
        self.touch('server_port', '31379')
        self.touch('debug_mode', False)

    def __getitem__(self, item):
        return self.data[item]
