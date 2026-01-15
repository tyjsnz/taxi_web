# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   redis_client.py
@date     :   2025/05/14 12:55:11
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   redis客户端，注意：程序里消息推送要与此类型匹配
'''

import redis
import json
from loguru import logger

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
CHANNEL_NAME = 'websocket_messages'

def get_redis_connection():
    #return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
    return redis.Redis(connection_pool=pool)

def publish_message(channel=CHANNEL_NAME, message=None):
    r = get_redis_connection()
    r.publish(channel, json.dumps(message))
    logger.debug(f"Published to Redis channel {channel}: {message}")

def subscribe_messages(channel=CHANNEL_NAME):
    ''' 订阅消息
        在需要订阅消息的地方调用即可，如：
        for msg in subscribe_messages():
        print("【订阅处理器】:", msg)
    '''
    r = get_redis_connection()
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    for message in pubsub.listen():
        if message['type'] == 'message':
            yield json.loads(message['data'])