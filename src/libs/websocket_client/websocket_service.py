# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
WebSocket服务，用于处理Redis消息队列中的数据，将其发送到指定NodeSocketServer服务端。
@file     :   websocket_service.py
@date     :   2025/03/14 09:59:41
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   websocket服务

nohup python3 websocket_service.py > websocket.log 2>&1 &
'''

import signal
import sys,time
from websocket_client import WebSocketClient
from redis_client import subscribe_messages,publish_message

def custom_message_handler(message):
    #print("【自定义处理器】收到下行消息:", message)
    # 转发到 Redis
    publish_message(channel="websocket_downstream", message={
        "type": "websocket",
        "content": message,
        "timestamp": time.time()
    })
def start_websocket_service():
    #uri = 'ws://ws.flacn.net:8080?client_id=11flask_backend&token=your_secret_token'
    #client = WebSocketClient(uri=uri)
    # 本地
    client = WebSocketClient()
    client.register_handler(custom_message_handler)

    # 确保心跳线程已启动
    if not client.running:
        client._start_heartbeat()

    # 等待连接成功
    while not client.conn or client._is_closed(client.conn):
        print("Waiting for initial WebSocket connection...")
        time.sleep(1)
        client._connect()  # 主动尝试重连
    
    def graceful_shutdown(*args):
        print("Shutting down WebSocket service...")
        client.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    print("WebSocket service started, waiting for messages...")
    for msg in subscribe_messages():
        if "target_token" not in msg:
            continue
        
        target = msg.get('target_token')
        data = msg.get('data')
        if data:
            client.send_msg(target, data)


if __name__ == "__main__":
    start_websocket_service()