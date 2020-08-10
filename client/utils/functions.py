# -*- coding: utf-8 -*-
import sys
import msvcrt
import json
import re
import time
import qrcode
from datetime import datetime

CHARACTERS = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')']
status_dict = {
    0: 'application.status.sent',
    1: 'application.status.first_passed',
    2: 'application.status.final_passed',
    -1: 'application.status.refused'
}


def login(client):
    """Login"""
    client.logger.info(client.lang.t('login.input_info'))
    username = input(client.lang.t('input.username'))
    print(client.lang.t('input.password'), end='')
    password = input_password(client)
    data = {
        'username': username,
        'password': password
    }
    r = client.session.post(get_url(client, 'login'), json=data).json()
    if r['code'] == -2:
        client.logger.error(client.lang.t('login.error_username'))
        sys.exit()
    elif r['code'] == -1:
        client.logger.error(client.lang.t('login.error_password'))
        sys.exit()
    elif r['code'] == 0:
        client.logger.info(client.lang.t('login.success'))
    return username


def set_self_password(client):
    print(client.lang.t('input.new_password'), end='')
    password = input_password(client)
    r = client.session.post(
        get_url(client, 'set_self_password'),
        json={'password': password}
    ).json()
    client.logger.debug(f'服务器返回信息: {json_dumps(r)}')
    if r['code'] == 0:
        client.logger.info(client.lang.t('operation_success'))
    elif r['code'] == -1:
        client.logger.info(client.lang.t('permission_denied'))


def get_permission(client) -> int:
    permission = client.session.get(get_url(client, 'get_permission')).json()
    return permission['data']['permission']


def input_password(client) -> str:
    """
    Input password secret
    :return password str
    """
    password = []
    while True:
        ch = msvcrt.getch()
        # 回车
        if ch == b'\r':
            msvcrt.putch(b'\n')
            break
        # 退格
        elif ch == b'\x08':
            if password:
                password.pop()
                msvcrt.putch(b'\b')
                msvcrt.putch(b' ')
                msvcrt.putch(b'\b')
        else:
            password.append(ch)
            msvcrt.putch(b'*')
    password = b''.join(password).decode()
    pattern = re.compile(r'\w')
    for i in password:
        if i not in CHARACTERS and pattern.match(i) is None:
            client.logger.error(
                client.lang.t('reminder.password_illegal_character', i))
            sys.exit()
    return password


def get_url(client, route: str) -> str:
    """Trans the api route to whole url"""
    return 'http://{}:{}/{}'.format(
        client.config["server_host"],
        client.config["server_port"],
        route
    )


def select_target(client, permission: int) -> int:
    if permission == 1:
        user_type = 'student'
    elif permission in [2, 3]:
        user_type = 'approver'
    elif permission == 4:
        user_type = 'admin'
    else:
        user_type = 'student'
    target_type = client.lang.t(f'select.{user_type}')
    for i in target_type.splitlines():
        client.logger.info(i)
    i = ''
    while not i.isdigit():
        i = input(client.lang.t('input.select'))
        if i.isdigit():
            break
        else:
            client.logger.warning(client.lang.t('reminder.must_int'))
    return int(i)


def json_dumps(d: dict) -> str:
    return json.dumps(d, indent=4, ensure_ascii=False)


def time_fmt(t: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))


def str_to_time(s: str) -> time.localtime():
    s = s.split('-')
    if len(s) == 5:
        try:
            s = [int(i) for i in s]
            return datetime(*s).timestamp()
        except ValueError:
            return None


def show_application_info(client, application_id: str, info: dict):
    comment = 'None' if info['comment'] == '' else info['comment']
    log = (client.lang.t(
        'application.info',
        application_id,
        info['username'],
        time_fmt(info['start_time']),
        time_fmt(info['end_time']),
        info['reason'],
        comment,
        client.lang.t(status_dict[info['status']])
    ))
    for i in log.splitlines():
        client.logger.info(i)


def set_application(client, permission, application_id):
    # 检查申请存在
    if client.session.get(
            get_url(client, 'is_application'),
            params={'application_id': application_id}
    ).json()['code'] == 0:
        client.logger.error(client.lang.t('application_not_exists'))
        return
    # 显示信息
    application_info = client.session.get(
        get_url(client, 'get_application_info'),
        params={'application_id': application_id}
    ).json()['data']
    show_application_info(client, application_id, application_info)
    # 显示选择
    log = client.lang.t('select.status')
    for i in log.splitlines():
        client.logger.info(i)
    # 设置状态
    status = input(client.lang.t('input.select'))
    if status == '1':
        status = permission - 1
    elif status == '2':
        status = -1
    else:
        client.logger.error(client.lang.t('reminder.input_must_in', [1, 2]))
        return
    # 批示
    comment = input(client.lang.t('input.comment'))
    data = {
        'application_id': application_id,
        'status': status
    }
    if comment != '':
        data['comment'] = comment
    # 发送
    r = client.session.post(
        get_url(client, 'set_application_status'),
        json=data
    ).json()
    if r['code'] == 0:
        client.logger.info(client.lang.t('operation_success'))
    elif r['code'] == -1:
        client.logger.info(client.lang.t('permission_denied'))
    elif r['code'] == -3:
        client.logger.info(client.lang.t('has_operated'))
    elif r['code'] == -2:
        client.logger.info(client.lang.t('application_not_exists'))


def create_qr_code(client, username):
    qr = qrcode.make(f'{get_url(client, "check_leave")}?username={username}')
    qr.save(f'{username}.png')
    client.logger.info(f'文件已保存到 {username}.png 中')
