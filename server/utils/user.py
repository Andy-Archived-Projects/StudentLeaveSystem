# -*- coding: utf-8 -*-
import json
import time
import os
import uuid

from utils import constant
from utils.session import Session
from utils.logger import Logger
from utils import functions as func


class Leave:
    """管理外出的类"""

    def __init__(self, logger):
        self.logger = logger
        self.data = {}
        self.path = constant.LEAVE_FILE

        if os.path.isfile(self.path):
            self.load()
        self.__check()
        self.clean_apply()

    def clean_apply(self):
        save_flag = False
        new_dict = dict(self.data['applications'])
        for i, value in new_dict.items():
            if value['end_time'] < time.time():
                self.logger.info(f'删除过期请假信息: {i}')
                self.logger.debug(f'信息内容如下: {func.json_dumps(value)}')
                del self.data['applications'][i]
                save_flag = True
        if save_flag:
            self.save()

    def clean_user(self, username: str):
        save_flag = False
        new_dict = dict(self.data['applications'])
        for key, value in new_dict.items():
            if value['username'] == username:
                self.logger.info(f'清除用户 {username} 的请假信息')
                del self.data['applications'][key]
                save_flag = True
        if save_flag:
            self.save()

    def get_my_list(self, username: str) -> dict:
        self.clean_apply()
        all_applications_list = self.get_all_applications_list()
        my_list = {}
        for key, value in all_applications_list.items():
            if value['username'] == username:
                my_list[key] = value
        return my_list

    def get_all_applications_list(self) -> dict:
        return self.data['applications']

    def get_application_info(self, application_id: str) -> dict or bool:
        if application_id in self.data['applications'].keys():
            return self.data['applications'][application_id]
        else:
            return False

    def is_application(self, application_id: str):
        if application_id in self.data['applications'].keys():
            return True
        else:
            return False

    def add_application(self, username: str, start_time: int,
                        end_time: int, reason: str):
        application_id = str(uuid.uuid4())
        self.data['applications'][application_id] = {
            'username': username,
            'start_time': start_time,
            'end_time': end_time,
            'reason': reason,
            'comment': '',
            'operations': [],
            'status': 0
        }
        self.logger.info('{} 发送申请, 申请ID {}, 申请数据 {}'.format(
            username,
            application_id,
            func.json_dumps(self.data["applications"][application_id]))
        )
        self.save()

    def remove_application(self, application_id: str) -> bool:
        if self.is_application(application_id):
            del self.data['applications'][application_id]
            self.save()
            return True
        else:
            return False

    def set_status(self, application_id: str,
                   operator: str, status: int, comment: str = None) -> int:
        """
        Set the application status
        :return:
        0:Set success
        -1:No application
        -2:Status error
        -3:Have operated
        """
        if status not in [-1, 0, 1, 2]:
            return -2
        elif self.is_application(application_id):
            self.data['applications'][application_id]['status'] = status
            if comment is not None:
                self.data['applications'][application_id]['comment'] = comment
            self.data['applications'][application_id]['operations'].append(
                {
                    'operator': operator,
                    'status': status,
                    'comment': comment
                }
            )
            self.save()
            return 0
        else:
            return -1

    def save(self):
        self.clean_apply()
        self.data['update_time'] = int(time.time())
        with open(self.path, 'w', encoding='utf8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def load(self):
        with open(self.path, encoding='utf8') as f:
            self.data = json.load(f)

    def __touch_dict(self, key, value):
        if key not in self.data.keys():
            self.data[key] = value
            return True
        else:
            return False

    def __check(self):
        save_flag = False
        save_flag |= self.__touch_dict('update_time', int(time.time()))
        save_flag |= self.__touch_dict('applications', {})
        if save_flag:
            self.save()


class User:
    """管理用户的类"""

    def __init__(self):
        self.logger = Logger()
        self.leave = Leave(self.logger)
        self.session = Session()

        self.data = {}
        self.path = constant.USER_DATA_FILE
        if os.path.isfile(self.path):
            self.load()
        self.__check()

    def add_user(self, username: str) -> bool:
        """
        Add a user to user data
        If there are already had the user, return False
        Return True if create success
        """
        if self.is_user(username):
            return False
        else:
            self.data['users'][username] = {
                'password': '123456',
                'permission': 1
            }
            self.save()
            return True

    def is_user(self, username: str) -> bool:
        """:return True or False if user is or not in the user data"""
        if username in self.data['users'].keys():
            return True
        else:
            return False

    def del_user(self, username: str) -> bool:
        """
        Remove the user from user data
        If th user is undefined, return False
        Return True if remove success
        """
        if not self.is_user(username):
            return False
        else:
            del self.data['users'][username]
            self.leave.clean_user(username)
            self.save()
            return True

    def get_user_list(self) -> dict:
        return self.data['users']

    def get_username(self, request) -> bool or str:
        return self.session.get_username(request.cookies['session'])

    def set_password(self, username: str, password: str) -> bool:
        """
        Set the password for the user
        If the user is undefined return False
        Return True if set password success
        """
        if not self.is_user(username):
            return False
        else:
            self.data['users'][username]['password'] = password
            self.save()
            return True

    def check_password(self, username: str, password: str) -> bool:
        """:return True or False if password is correct or wrong"""
        if self.data['users'][username]['password'] == password:
            return True
        else:
            return False

    def set_permission(self, username: str, permission: int) -> bool:
        """
        Set the permission for the user
        If the user is undefined return False
        Return True if set permission success
        """
        if isinstance(permission, int):
            if permission not in [1, 2, 3, 4] or not self.is_user(username):
                return False
            else:
                self.data['users'][username]['permission'] = permission
                self.save()
                return True

    def get_permission(self, request) -> int:
        """
        Get the permission
        :return Permission level
        """
        username = self.get_username(request)
        return self.data['users'][username]['permission']

    def save(self):
        self.data['update_time'] = int(time.time())
        with open(self.path, 'w', encoding='utf8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def load(self):
        with open(self.path, encoding='utf8') as f:
            self.data = json.load(f)

    def __check_admin(self):
        if not self.is_user('Admin'):
            self.add_user('Admin')
            self.set_permission('Admin', 4)
            return True
        else:
            return False

    def __touch_dict(self, key, value):
        if key not in self.data.keys():
            self.data[key] = value
            return True
        else:
            return False

    def __check(self):
        save_flag = False
        save_flag |= self.__touch_dict('update_time', int(time.time()))
        save_flag |= self.__touch_dict('users', {})
        save_flag |= self.__check_admin()
        if save_flag:
            self.save()
