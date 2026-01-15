# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   order_transfer_db.py
@date     :   2025/03/10 00:00:00
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   订单转派数据库操作
'''

from src.model.base_db import PublicDbConnection

class OrderTransferDb(PublicDbConnection):
    def __init__(self):
        super().__init__()
        self._tbname = "ls_order_transfer"

    def get_transfer_by_id(self, transfer_id):
        """ 根据转派ID获取转派信息
            Args:
                transfer_id: 转派ID
            Return: 
                转派信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'SELECT * FROM {self._tbname} WHERE id = %s'
        return self._query_sql(sql, (transfer_id,))

    def insert_transfer(self, transfer_data):
        """ 插入新的订单转派记录
            Args:
                transfer_data: 转派数据字典
            Return: 
                插入结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        columns = ', '.join(transfer_data.keys())
        placeholders = ', '.join(['%s'] * len(transfer_data))
        sql = f'INSERT INTO {self._tbname} ({columns}) VALUES ({placeholders})'
        return self._execute_sql(sql, tuple(transfer_data.values()))

    def update_transfer_remark(self, transfer_id, remark):
        """ 更新订单转派的备注信息
            Args:
                transfer_id: 转派ID
                remark: 备注信息
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'UPDATE {self._tbname} SET remark = %s WHERE id = %s'
        return self._execute_sql(sql, (remark, transfer_id))

    def delete_transfer(self, transfer_id):
        """ 删除订单转派记录
            Args:
                transfer_id: 转派ID
            Return: 
                删除结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'DELETE FROM {self._tbname} WHERE id = %s'
        return self._execute_sql(sql, (transfer_id,))

    def get_all_transfers(self):
        """ 获取所有订单转派记录
            Args:
                None
            Return: 
                所有订单转派记录
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'SELECT * FROM {self._tbname}'
        return self._query_sql(sql)