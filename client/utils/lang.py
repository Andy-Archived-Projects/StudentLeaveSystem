# -*- coding: utf-8 -*-
import yaml


class Lang:
    def __init__(self, language):
        self.language = language
        self.data = {}
        self.load()

    def load(self):
        with open(f'lang\\{self.language}.yml', encoding='utf8') as f:
            self.data = yaml.safe_load(f)

    def translate(self, text, *args):
        result = self.data[text]
        if len(args) > 0:
            result = result.format(*args)
        return result

    def t(self, text, *args):
        return self.translate(text, *args)
