# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 
'''
@file     :   order_fee_detail_db.py
@date     :   2025/03/21 14:51:37
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   订单费用详情数据库
'''
from src.model.base_db import PublicDbConnection
class OrderFeeDetailDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()
        self._tbname = "ls_order_fee_details"

    def update_order_fee_detail_by_dict(self,order_id, data_dict):
        # 更新记录
        return self.update_data_by_id(self._tbname, data_dict, order_id)
    def get_order_fee_details_by_order_id(self, order_id):
        """ 根据订单ID获取订单费用详情
            Args:
                order_id: 订单ID 
            Return: 
                None
            @date:   2025/03/21 14:53:01
            @author: snz
        """
        
        sql = "SELECT * FROM %s WHERE order_id = %s" % (self._tbname, order_id)
        return self._query_sql(sql)
    
    def insert_order_fee_detail(self, order_fee_detail_data):
        """ 插入订单费用详情
            Args:
                order_fee_detail_data: 订单费用详情数据
            Return: 
                None
            @date:   2025/03/21 14:53:01
            @author: snz
        """
        columns = ', '.join(order_fee_detail_data.keys())
        placeholders = ', '.join(['%s'] * len(order_fee_detail_data))
        sql = f'INSERT INTO {self._tbname} ({columns}) VALUES ({placeholders})'
        return self._execute_sql(sql, tuple(order_fee_detail_data.values()))
    
    def update_order_add_fee(self, order_id, price):
        """ 更新加价叫车费用
            Args:
                order_id: 订单id
                price: 加价金额
            Return: 
                None
            @date:   2025/03/21 14:53:01
            @author: snz
        """
        sql = f"update {self._tbname} set user_add_fee = {price} where order_id = {order_id}"
        return self._execute_sql(sql)
