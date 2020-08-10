# -*- coding: utf-8 -*-
import os
import time
from flask import Flask, request

from utils import constant
from utils.user import User
from utils import functions as func

if not os.path.isdir(constant.DATA_FOLDER):
    os.mkdir(constant.DATA_FOLDER)
server = Flask(__name__)
server.config['JSON_AS_ASCII'] = False
user = User()
user.logger.info('正在启动服务端')

status_dict = {
    0: '已申请',
    1: '初审通过',
    2: '终审通过',
    -1: '申请拒绝'
}


@server.route('/check_leave', methods=['GET'])
def check_leave():
    username = request.args['username']
    data = user.leave.get_my_list(username)
    for application_id, info in data.items():
        if info['start_time'] < time.time() < info['end_time']:
            data = {
                'username': info['username'],
                'start_time': func.time_fmt(info['start_time']),
                'end_time': func.time_fmt(info['end_time']),
                'reason': info['reason'],
                'comment': info['comment'],
                'status': status_dict[info['status']]
            }
            user.logger.info(f'未知用户申请查看 {username} 的申请 {application_id}')
            return func.json_dumps(data)
    return '没有当前时间的外出数据'


@server.route('/login', methods=['POST'])
def login():
    """
    :return code
    0: Success
    -1: Error password
    -2: Undefined user
    -3: Illegal client
    """
    return func.check_password(user, request)


@server.route('/get_permission', methods=['GET'])
def get_permission():
    permission = user.get_permission(request)
    username = user.get_username(request)
    user.logger.info(f'{username} 获取权限完成, 返回 {permission}')
    return func.create_response(code=0, data={'permission': permission})


@server.route('/add_user', methods=['GET'])
def add_user():
    """
    :return code
    0: Success
    -1: Permission denied
    -2: User has created
    """
    if user.get_permission(request) == 4:
        username = request.args['username']
        if user.add_user(username):
            user.logger.info(f'{user.get_username(request)} 创建用户 {username}')
            return func.create_response(code=0, message='操作成功')
        else:
            return func.create_response(code=-2, message='用户已存在')
    else:
        return func.create_response(code=-1, message='权限不足')


@server.route('/del_user', methods=['GET'])
def del_user():
    """
    :return code
    0: Success
    -1: Permission denied
    -2: User is undefined
    """
    if user.get_permission(request) == 4:
        username = request.args['username']
        if user.del_user(username):
            user.logger.info(f'{user.get_username(request)} 删除用户 {username}')
            return func.create_response(code=0, message='操作成功')
        else:
            return func.create_response(code=-2, message='用户不存在')
    else:
        return func.create_response(code=-1, message='权限不足')


@server.route('/get_user_list', methods=['GET'])
def get_user_list():
    if user.get_permission(request) == 4:
        user.logger.info(f'{user.get_username(request)} 申请获取用户列表')
        return func.create_response(code=0, data=user.get_user_list())
    else:
        return func.create_response(code=-1, message='权限不足')


@server.route('/set_password', methods=['POST'])
def set_password():
    data = request.json
    operator = user.get_username(request)
    if user.get_permission(request) == 4:
        username = data['username']
        password = data['password']
        if user.set_password(username, password):
            user.logger.info(f'{operator} 修改用户 {username} 的密码为 "{password}"')
            return func.create_response(code=0, message='操作成功')
        else:
            return func.create_response(code=-2, message='用户不存在')
    else:
        return func.create_response(code=-1, message='权限不足')


@server.route('/set_self_password', methods=['POST'])
def set_self_password():
    data = request.json
    operator = user.get_username(request)
    password = data['password']
    if user.set_password(operator, password):
        user.logger.info(f'{operator} 修改自身密码为 "{password}"')
        return func.create_response(code=0, message='操作成功')
    else:
        return func.create_response(code=-2, message='用户不存在')


@server.route('/set_permission', methods=['POST'])
def set_permission():
    data = request.json
    if user.get_permission(request) == 4:
        username = data['username']
        permission = data['permission']
        if user.set_permission(username, permission):
            user.logger.info(f'修改用户 {username} 的权限等级为 "{permission}"')
            return func.create_response(code=0, message='操作成功')
        else:
            return func.create_response(code=-2, message='用户不存在')
    else:
        return func.create_response(code=-1, message='权限不足')


@server.route('/is_application', methods=['GET'])
def is_application():
    if user.leave.is_application(request.args['application_id']):
        return func.create_response(code=1)
    else:
        return func.create_response(code=0)


@server.route('/get_all_applications_list', methods=['GET'])
def get_all_applications_list():
    if user.get_permission(request) >= 2:
        user.logger.info(f'{user.get_username(request)} 申请获取申请信息列表')
        return func.create_response(code=0,
                                    data=user.leave.get_all_applications_list())
    else:
        return func.create_response(code=-1, message='权限不足')


@server.route('/get_my_list', methods=['GET'])
def get_my_list():
    if user.get_permission(request) == 1:
        username = user.get_username(request)
        my_list = user.leave.get_my_list(username)
        user.logger.info(f'{user.get_username(request)} 申请获取本人申请信息列表')
        return func.create_response(code=0, data=my_list)
    else:
        return func.create_response(code=-1, message='权限错误')


@server.route('/get_application_info', methods=['GET'])
def get_application_info():
    application_id = request.args['application_id']
    data = user.leave.get_application_info(application_id)
    if data:
        user.logger.info(f'{user.get_username(request)} '
                         f'申请获取 {application_id} 申请信息列表')
        return func.create_response(code=0, data=data)
    else:
        return func.create_response(code=-2, message='申请不存在')


@server.route('/send_application', methods=['POST'])
def send_application():
    data = request.json
    if user.get_permission(request) == 1:
        username = user.get_username(request)
        start_time = int(data['start_time'])
        end_time = int(data['end_time'])
        reason = data['reason']
        user.leave.add_application(username, start_time, end_time, reason)
        return func.create_response(code=0, message='操作成功')
    else:
        return func.create_response(code=-1, message='权限不足')


@server.route('/recall_application', methods=['POST'])
def recall_application():
    data = request.json
    if user.get_permission(request) == 1:
        application_id = data['application_id']
        if user.leave.remove_application(application_id):
            user.logger.info(
                f'{user.get_username(request)} 撤回申请 {application_id}')
            return func.create_response(code=0, message='操作成功')
        else:
            return func.create_response(code=-2, message='申请不存在')
    else:
        return func.create_response(code=-1, message='权限不足')


@server.route('/set_application_status', methods=['POST'])
def set_application_status():
    data = request.json
    operator = user.get_username(request)
    if user.get_permission(request) >= 2:
        application_id = data['application_id']
        status = data['status']
        comment = data['comment'] if 'comment' in data.keys() else None
        set_result = user.leave.set_status(application_id, operator,
                                           status, comment)
        if set_result == 0:
            user.logger.info(f'{operator} 将 {application_id} 状态设为 {status}')
            return func.create_response(code=0, message='操作成功')
        elif set_result == -1:
            return func.create_response(code=-2, message='申请不存在')
        elif set_result == -3:
            return func.create_response(code=-3, message='已经操作过了')
    else:
        return func.create_response(code=-1, message='权限不足')


server.run(host=constant.SERVER_HOST, port=constant.SERVER_PORT)
