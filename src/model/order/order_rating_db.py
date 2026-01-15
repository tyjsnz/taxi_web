# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   order_rating_db.py
@date     :   2025/03/10 00:00:00
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   订单评分数据库操作
'''

from src.model.base_db import PublicDbConnection

class OrderRatingDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()
        self._tbname = "ls_order_rating"

    def insert_order_rating(self, rating_data):
        """ 插入订单评分
            Args:
                rating_data: 评分数据字典
            Return: 
                插入结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        columns = ', '.join(rating_data.keys())
        placeholders = ', '.join(['%s'] * len(rating_data))
        sql = f'INSERT INTO {self._tbname} ({columns}) VALUES ({placeholders})'
        return self._execute_sql(sql, tuple(rating_data.values()))

    def get_order_rating_by_id(self, rating_id):
        """ 根据评分ID获取订单评分信息
            Args:
                rating_id: 评分ID
            Return: 
                评分信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'SELECT * FROM {self._tbname} WHERE id = %s'
        return self._query_sql(sql, (rating_id,))

    def get_order_ratings_by_order_id(self, order_id):
        """ 根据订单ID获取所有评分信息
            Args:
                order_id: 订单ID
            Return: 
                评分信息列表
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'SELECT * FROM {self._tbname} WHERE order_id = %s'
        return self._query_sql(sql, (order_id,))

    def update_order_rating(self, rating_id, rating_data):
        """ 更新订单评分
            Args:
                rating_id: 评分ID
                rating_data: 评分数据字典
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        set_clause = ', '.join([f'{key} = %s' for key in rating_data.keys()])
        sql = f'UPDATE {self._tbname} SET {set_clause} WHERE id = %s'
        values = list(rating_data.values()) + [rating_id]
        return self._execute_sql(sql, tuple(values))

    def delete_order_rating(self, rating_id):
        """ 删除订单评分
            Args:
                rating_id: 评分ID
            Return: 
                删除结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'DELETE FROM {self._tbname} WHERE id = %s'
        return self._execute_sql(sql, (rating_id,))