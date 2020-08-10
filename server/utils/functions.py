# -*- coding: utf-8 -*-
import json
import time
import os
from flask import Response

from utils import constant


def create_response(**kwargs) -> Response:
    """
    Create response object
    If response is dict, use response to create Response
    If response is not None, use kwargs to create Response
    """
    if kwargs is not None:
        return Response(json.dumps(dict(**kwargs)), mimetype='application/json')
    else:
        response = {
            'code': 500,
            'message': '内部错误'
        }
        return Response(json.dumps(response), mimetype='application/json')


def check_password(user, request) -> Response:
    """Check user password and add token"""
    data = request.json
    headers = request.headers
    set_cookie = False
    r = {}
    username = ''
    if 'User-Agent' in headers.keys() and 'python' in headers['User-Agent']:
        if ('username' and 'password') in data.keys() and len(data.keys()) == 2:
            username = data['username']
            if user.is_user(username):
                if user.check_password(username, data['password']):
                    r['message'] = '登录成功'
                    r['code'] = 0
                    set_cookie = True
                    user.logger.info(f'用户 {username} 登陆成功')
                else:
                    r['message'] = '密码错误'
                    r['code'] = -1
                    user.logger.info(f'尝试登陆的用户 {username} 密码错误')
            else:
                r['message'] = '用户不存在'
                r['code'] = -2
                user.logger.info(f'尝试登陆的用户名 {username} 不存在')
        else:
            r['message'] = 'Illegal client'
            r['code'] = -3
    else:
        r['message'] = 'Illegal client'
        r['code'] = -3
    response = create_response(**r)
    if set_cookie:
        token = user.session.create_token(username)
        response.set_cookie('session', token)
        user.logger.info(f'为用户 {username} 分配SessionToken {token}')
    return response


def make_log_backup():
    """Create log backup on startup"""
    file_name = constant.LATEST_LOG_FILE
    if os.path.isfile(file_name):
        modify_time = time.strftime('%Y-%m-%d', time.localtime(
            os.stat(file_name).st_mtime))
        counter = 0
        while True:
            counter += 1
            new_file_name = '{}/{}-{}.log'.format(
                os.path.dirname(file_name), modify_time, counter)
            if not os.path.isfile(new_file_name):
                break
        os.rename(file_name, new_file_name)


def json_dumps(d: dict) -> str:
    return json.dumps(d, indent=4, ensure_ascii=False)


def time_fmt(t: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
