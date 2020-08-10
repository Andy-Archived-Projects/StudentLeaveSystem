# -*- coding: utf-8 -*-
import time
import secrets


class Session:
    def __init__(self):
        self.data = []

    def create_token(self, username: str) -> str:
        """Create token for the user, return the token has created"""
        for i, data in enumerate(self.data):
            if data['username'] == username:
                del self.data[i]
        data = {
            'username': username,
            'token': secrets.token_urlsafe(16),
            'token_life': int(time.time()) + (60 * 20)
        }
        self.data.append(data)
        return data['token']

    def get_username(self, token: str) -> bool or str:
        """
        Get username with token
        Return False if token is undefined or overdue
        Return username if founded
        """
        for i in self.data:
            if i['token'] == token:
                if time.time() > i['token_life']:
                    return False
                else:
                    return i['username']
        return False
