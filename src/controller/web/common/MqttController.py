# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 目前未使用

'''
@file     :   MQTTController.py
@date     :   2025/03/09 14:44:21
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   公共MQTT控制器
'''
from src.helper.mqtt_client import MQTTClient
import threading
from src.common.const_defined import *

class MQTTController():
    def __init__(self,topic='test/topic') -> None:
        self.topic = topic
        self.mqtt_client = MQTTClient(debug=True)
        self.mqtt_client.set_message_callback(self.mqtt_custom_on_message)
    def start_mqtt_worker(self):
        th = threading.Thread(target=self._init_mqtt)
        th.daemon = True
        th.start()

    def _init_mqtt(self):
        self.mqtt_client.connect()
        self.mqtt_client.subscribe(self.topic)

    def subscribe(self,topic):
        """增加订阅主题，注意要连接成功后才可订阅
        """
        self.mqtt_client.subscribe(topic)

    def disconnect(self):
        """断开连接
        """
        self.mqtt_client.disconnect()

    def mqtt_custom_on_message(self,client, userdata, msg):
        # 自定义mqtt消息处理，此处作为公共mqtt消息处理
        print((f"mqtcontroller mqtt received [{msg.topic}]: {msg.payload.decode()}"))

if __name__ == '__main__':
     # 启动 MQTT 客户端
    mqtt = MQTTController()
    mqtt.start_mqtt_worker()
    time.sleep(2)
    mqtt.subscribe("demo")