# -*- coding: utf-8 -*-
import requests
from logging import DEBUG

from utils.lang import Lang
from utils.logger import Logger
from utils.config import Config
import utils.functions as func


class Client:
    def __init__(self):
        self.config = Config()
        self.lang = Lang(self.config['language'])
        self.logger = Logger()
        self.session = requests.Session()


client = Client()
# set this to True to turn on debug info
if client.config['debug_mode']:
    client.logger.set_level(DEBUG)
    client.logger.debug(client.lang.t('init.set_debug'))

client.logger.info(client.lang.t('login.welcome'))
username = func.login(client)
permission = func.get_permission(client)
client.logger.debug(f'权限等级为: {permission}')

while True:
    # 申请者
    target = func.select_target(client, permission)
    if permission == 1:
        # 查看申请
        if target == 1:
            r = client.session.get(func.get_url(client, 'get_my_list')).json()
            client.logger.debug(f'服务器返回信息: {func.json_dumps(r)}')
            if len(r['data']) == 0:
                client.logger.info(client.lang.t('none_data'))
            else:
                for key, value in r['data'].items():
                    func.show_application_info(client, key, value)
        # 发送申请
        elif target == 2:
            start_time = func.str_to_time(
                input(client.lang.t('input.start_time')))
            end_time = func.str_to_time(input(client.lang.t('input.end_time')))
            if start_time is None or end_time is None:
                client.logger.warning(client.lang.t('reminder.time_format'))
                continue
            data = {
                'start_time': start_time,
                'end_time': end_time,
                'reason': input(client.lang.t('input.reason'))
            }
            r = client.session.post(
                func.get_url(client, 'send_application'), json=data).json()
            if r['code'] == 0:
                client.logger.info(client.lang.t('operation_success'))
            elif r['code'] == -1:
                client.logger.info(client.lang.t('permission_denied'))
        # 撤回申请
        elif target == 3:
            application_id = input(client.lang.t('input.application_id'))
            r = client.session.post(
                func.get_url(client, 'recall_application'), json={
                    'application_id': application_id}).json()
            if r['code'] == 0:
                client.logger.info(client.lang.t('operation_success'))
            elif r['code'] == -1:
                client.logger.info(client.lang.t('permission_denied'))
            elif r['code'] == -2:
                client.logger.info(client.lang.t('application_not_exists'))
        # 生成二维码
        elif target == 4:
            func.create_qr_code(client, username)
        # 修改密码
        elif target == 5:
            func.set_self_password(client)
    # 审核
    elif permission in [2, 3]:
        # 开始审核
        if target == 1:
            r = client.session.get(
                func.get_url(client, 'get_all_applications_list')).json()
            client.logger.debug(f'服务器返回信息: {func.json_dumps(r)}')
            data = {}
            # 排除无用信息
            for key, value in r['data'].items():
                if value['status'] == permission - 2:
                    data[key] = value
            if len(data) == 0:
                client.logger.info(client.lang.t('none_data'))
            else:
                for application_id in data.keys():
                    func.set_application(client, permission, application_id)
        # 查看列表
        elif target == 2:
            r = client.session.get(
                func.get_url(client, 'get_all_applications_list')).json()
            client.logger.debug(f'服务器返回信息: {func.json_dumps(r)}')
            for key, value in r['data'].items():
                func.show_application_info(client, key, value)
        # 修改许可
        elif target == 3:
            application_id = input(client.lang.t('input.application_id'))
            func.set_application(client, permission, application_id)
        # 修改密码
        elif target == 4:
            func.set_self_password(client)
    # 管理员
    elif permission == 4:
        # 查看用户列表
        if target == 1:
            r = client.session.get(func.get_url(client, 'get_user_list')).json()
            client.logger.debug(f'服务器返回信息: {func.json_dumps(r)}')
            for key, value in r['data'].items():
                log = client.lang.t(
                    'user.user_info',
                    key,
                    value['password'],
                    value['permission']
                )
                for i in log.splitlines():
                    client.logger.info(i)
        # 添加用户
        elif target == 2:
            username = input(client.lang.t('input.username'))
            r = client.session.get(
                func.get_url(client, 'add_user'),
                params={'username': username}
            ).json()
            client.logger.debug(f'服务器返回信息: {func.json_dumps(r)}')
            client.logger.info(r['message'])
        # 删除用户
        elif target == 3:
            username = input(client.lang.t('input.username'))
            r = client.session.get(
                func.get_url(client, 'del_user'),
                params={'username': username}
            ).json()
            client.logger.debug(f'服务器返回信息: {func.json_dumps(r)}')
            client.logger.info(r['message'])
        # 修改密码
        elif target == 4:
            username = input(client.lang.t('input.username'))
            print(client.lang.t('input.new_password'), end='')
            password = func.input_password(client)
            r = client.session.post(
                func.get_url(client, 'set_password'),
                json={'username': username, 'password': password}
            ).json()
            client.logger.debug(f'服务器返回信息: {func.json_dumps(r)}')
            client.logger.info(r['message'])
        # 修改权限等级
        elif target == 5:
            username = input(client.lang.t('input.username'))
            p = input(client.lang.t('input.permission_level'))
            if p not in ['1', '2', '3', '4']:
                client.logger.warning(
                    client.lang.t('reminder.input_must_in', [1, 2, 3, 4]))
            else:
                r = client.session.post(
                    func.get_url(client, 'set_permission'),
                    json={'username': username, 'permission': int(p)}
                ).json()
                client.logger.debug(f'服务器返回信息: {func.json_dumps(r)}')
                client.logger.info(r['message'])
