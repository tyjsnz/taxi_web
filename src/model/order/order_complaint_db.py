# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   order_complaint_db.py
@date     :   2025/03/10 00:00:00
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   订单投诉数据库操作
'''

from src.model.base_db import PublicDbConnection

class OrderComplaintDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()
        self._tbname = "ls_order_complaint"

    def get_complaint_by_id(self, complaint_id):
        """ 根据投诉ID获取投诉信息
            Args:
                complaint_id: 投诉ID
            Return: 
                投诉信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'SELECT * FROM {self._tbname} WHERE id = %s'
        return self._query_sql(sql, (complaint_id,))

    def insert_complaint(self, complaint_data):
        """ 插入新的订单投诉记录
            Args:
                complaint_data: 投诉数据字典
            Return: 
                插入结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        columns = ', '.join(complaint_data.keys())
        placeholders = ', '.join(['%s'] * len(complaint_data))
        sql = f'INSERT INTO {self._tbname} ({columns}) VALUES ({placeholders})'
        return self._execute_sql(sql, tuple(complaint_data.values()))

    def update_complaint_remark(self, complaint_id, remark):
        """ 更新订单投诉的处理结果
            Args:
                complaint_id: 投诉ID
                remark: 处理结果
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'UPDATE {self._tbname} SET remark = %s WHERE id = %s'
        return self._execute_sql(sql, (remark, complaint_id))

    def delete_complaint(self, complaint_id):
        """ 删除订单投诉记录
            Args:
                complaint_id: 投诉ID
            Return: 
                删除结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'DELETE FROM {self._tbname} WHERE id = %s'
        return self._execute_sql(sql, (complaint_id,))

    def get_all_complaints(self):
        """ 获取所有订单投诉记录
            Args:
                None
            Return: 
                所有订单投诉记录
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'SELECT * FROM {self._tbname}'
        return self._query_sql(sql)