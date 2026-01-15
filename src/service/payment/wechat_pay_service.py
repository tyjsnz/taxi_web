# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 
'''
@file     :   wechat_pay_service.py
@date     :   2025/03/10 00:00:00
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   微信支付服务
'''

import requests
from src.config import WECHAT_PAY_CONFIG

class WechatPayService:
    def create_payment(self, order_id, total_fee):
        """ 创建微信支付订单
            Args:
                order_id: 订单ID
                total_fee: 订单总金额
            Return: 
                支付结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        data = {
            "appid": WECHAT_PAY_CONFIG['appid'],
            "mch_id": WECHAT_PAY_CONFIG['mch_id'],
            "nonce_str": self._generate_nonce_str(),
            "body": "打车订单支付",
            "out_trade_no": str(order_id),
            "total_fee": int(total_fee * 100),  # 微信支付单位为分
            "spbill_create_ip": "127.0.0.1",
            "notify_url": WECHAT_PAY_CONFIG['notify_url'],
            "trade_type": "JSAPI",
            "openid": "user_openid",  # 需要替换为实际的用户openid
        }
        data['sign'] = self._generate_sign(data)
        response = requests.post(url, data=data)
        return response.json()

    def process_payment_notify(self, xml_data):
        """ 处理微信支付回调通知
            Args:
                xml_data: 微信支付回调通知的XML数据
            Return: 
                处理结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        # 解析XML数据并处理支付结果
        # 这里需要使用一个XML解析库，例如xml.etree.ElementTree
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_data)
        result_code = root.find('result_code').text
        if result_code == 'SUCCESS':
            # 更新订单状态等操作
            pass
        return {"return_code": result_code}

    def _generate_nonce_str(self):
        """ 生成随机字符串
            Args:
                None
            Return: 
                随机字符串
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    def _generate_sign(self, data):
        """ 生成签名
            Args:
                data: 需要签名的数据
            Return: 
                签名
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        import hashlib
        import urllib.parse
        stringA = '&'.join(['{}={}'.format(k, v) for k, v in sorted(data.items()) if v])
        stringSignTemp = '{}&key={}'.format(stringA, WECHAT_PAY_CONFIG['key'])
        return hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest().upper()