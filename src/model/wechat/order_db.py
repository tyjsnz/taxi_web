# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 
'''
@file     :   order_db.py
@date     :   2025/03/18 15:29:53
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   订单数据库操作类
'''

from src.model.base_db import PublicDbConnection
from src.common.const_defined import ORDER_STATUS

class OrderDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()
        self._tbname = 'ls_order'

    def create_order(self, order_data):
        """ 创建订单
            Args:
                order_data: 订单数据字典
            Return:
                订单ID
            @date:   2025/03/18 15:30:03
            @author: snz
        """
        keys = ', '.join(order_data.keys())
        placeholders = ', '.join(['%s'] * len(order_data))
        sql = f"INSERT INTO {self._tbname} ({keys}) VALUES ({placeholders})"
        values = tuple(order_data.values())
        return self._execute_sql(sql, values)

    def get_nopay_order_list(self, customer_id,col="*"):
        """ 获取未支付订单列表
            Args:
                customer_id: 用户ID
                col: 查询字段
            Return:
                订单列表
            @date:   2025/03/18 15:30:03
            @author: snz
        """
        sql = f"SELECT {col} FROM {self._tbname} WHERE customer_id = %s AND status = {ORDER_STATUS.ARRIVED_NO_PAY}"
        return self._query_sql(sql, (customer_id,))