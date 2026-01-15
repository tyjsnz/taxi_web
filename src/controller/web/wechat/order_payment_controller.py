# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   order_payment_controller.py
@date     :   2025/03/10 00:00:00
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   打车订单微信支付业务逻辑控制器
'''

from flask import Blueprint, request, jsonify
from src.model.order.order_db import OrderDb
from src.service.payment.wechat_pay_service import WechatPayService

order_payment_bp = Blueprint('order_payment', __name__)

@order_payment_bp.route('/pay/<int:order_id>', methods=['POST'])
def pay_order(order_id):
    """ 处理订单支付请求
        Args:
            order_id: 订单ID
        Return: 
            支付结果
        @date:   2025/03/10 00:00:00
        @author: snz
    """
    order_db = OrderDb()
    order = order_db.get_order_by_id(order_id)
    if not order:
        return jsonify({"error": "订单不存在"}), 404

    if order['status'] != 0:
        return jsonify({"error": "订单状态不允许支付"}), 400

    wechat_pay_service = WechatPayService()
    pay_result = wechat_pay_service.create_payment(order_id, order['total_fee'])

    if pay_result['return_code'] == 'SUCCESS' and pay_result['result_code'] == 'SUCCESS':
        return jsonify({"code": 0, "message": "支付成功", "data": pay_result}), 200
    else:
        return jsonify({"code": 1, "message": "支付失败", "data": pay_result}), 400

@order_payment_bp.route('/notify', methods=['POST'])
def payment_notify():
    """ 处理微信支付回调通知
        Args:
            None
        Return: 
            处理结果
        @date:   2025/03/10 00:00:00
        @author: snz
    """
    xml_data = request.data
    wechat_pay_service = WechatPayService()
    notify_result = wechat_pay_service.process_payment_notify(xml_data)

    if notify_result['return_code'] == 'SUCCESS':
        return '<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>', 200
    else:
        return '<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[处理失败]]></return_msg></xml>', 400