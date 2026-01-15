# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   websocket_manager.py
@date     :   2025/03/27 20:36:11
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   websocket管理器,用于处理websocket连接，pip install flask-sock支持。
             app.py中引入
             @sock.route('/websocket')
             def websocket_connect(ws: Server):
                connect(ws)
'''

from src.libs.websocket_client.redis_client import publish_message

def send_test(message):
    publish_message(message=message)
def send_message_to_target_client(target_token, message):
    """ 发送消息给指定客户端
        Args:
            target_token: 目标客户端token
            message: 消息内容
        Return: 
            None
        @date:   2025/03/28 00:40:05
        @author: snz
    """
    if 'target_token' not in message:
        message['target_token'] = target_token
    msg = {'target_token': target_token, 'data':  message}

    publish_message(message=msg)

def send_message_to_all_client(message):
    """ 发送消息给所有客户端
        Args:
            message: 消息内容
        Return: 
            None
        @date:   2025/03/28 00:43:33
        @author: snz
    """
    message['target_token'] = 'all'
    msg = {'target_token': all, 'data':  message}
    publish_message(message=message)

if __name__ == '__main__':
    pass

'''
from flask import request
from flask_sock import Server
import json

# 存储客户端连接，client_id 为键，ws 和 token 为值
# client_id需要唯一，可以使用用户ID或其他唯一标识
clients = {}

def connect(ws: Server):
    client_id = request.args.get('client_id')
    token = request.args.get('token')
    if not client_id or not token:
        #ws.send('client_id is required or token is required')
        ws.close()
        return

    #print(f'检测到客户端连接, client_id: {client_id}')
    item = {'ws': ws, 'token': token}
    clients[client_id] = item

    try:
        while True:
            data = ws.receive()
            if data is None:
                break
            #print(f'Received message from {client_id}: {data}')
            try:
                data = json.loads(data)
                # 不包含flag字段或flag字段为close时，关闭连接
                if 'flag' not in data or 'close' in data['flag']:
                    clients.pop(client_id, None)
                    ws.close()
                    return

                # 心跳包，客户端定时发送ping，服务端返回pong，后续扩展长时间无心跳断开连接
                if data['flag'] == 'ping':
                    ws.send('pong')
                    continue

                # 检查消息是否包含目标客户端ID，如没有则断开连接
                if 'target_token' not in data:
                    clients.pop(client_id, None)
                    ws.close()
                    return

                send_message_to_target_client(
                    data['target_token'], message=data)

            except Exception as e:
                print(f'Error: {e}')
            # 处理消息
    except Exception as e:
        print(f'Error: {e}')
    finally:
        print(f'Client {client_id} disconnected')
        clients.pop(client_id, None)


def send_message_to_target_client(target_token, message):
    """ 发送消息给指定客户端
        Args:
            target_token: 目标客户端token
            message: 消息内容
        Return: 
            None
        @date:   2025/03/28 00:40:05
        @author: snz
    """
    for id in clients:
        if clients[id]['token'] == target_token:
            send_message_to_client(id, message)
            return

def send_message_to_all_client(message):
    """ 发送消息给所有客户端
        Args:
            message: 消息内容
        Return: 
            None
        @date:   2025/03/28 00:43:33
        @author: snz
    """
    message = json.dumps(message)

    for client_id in clients:
        try:
            clients[client_id]['ws'].send(message)
            #print(f'Sent message to {client_id}: {message}')
        except Exception as e:
            print(f'Error sending message to {client_id}: {e}')
            clients.pop(client_id, None)


def send_message_to_client(client_id, message):
    """ 发送消息给指定客户端
        Args:
            client_id: 客户端ID
            message: 消息内容
        Return: 
            None
        @date:   2025/03/28 00:43:33
        @author: snz
    """
    try:

        message = json.dumps(message)
        clients[client_id]['ws'].send(message)
        #print(f'Sent message to {client_id}: {message}')
    except Exception as e:
        print(f'Error sending message to {client_id}: {e}')
        clients.pop(client_id, None)

def send_message_to_dispatch(order_id):
    """通知调度人员有订单无司机接单
    """
    pass

if __name__ == '__main__':
    pass
'''