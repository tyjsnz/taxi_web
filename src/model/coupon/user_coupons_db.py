# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   user_coupons_db.py
@date     :   2025/03/10 00:00:00
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   用户优惠券数据库操作
'''

from src.model.base_db import PublicDbConnection

class UserCouponsDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()
        self._tbname = "ls_user_coupons"

    def get_user_coupon_by_id(self, user_coupon_id):
        """ 根据用户优惠券ID获取用户优惠券信息
            Args:
                user_coupon_id: 用户优惠券ID
            Return: 
                用户优惠券信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'SELECT * FROM {self._tbname} WHERE id = %s'
        return self._query_sql(sql, (user_coupon_id,))

    def insert_user_coupon(self, user_coupon_data):
        """ 插入新的用户优惠券记录
            Args:
                user_coupon_data: 用户优惠券数据字典
            Return: 
                插入结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        columns = ', '.join(user_coupon_data.keys())
        placeholders = ', '.join(['%s'] * len(user_coupon_data))
        sql = f'INSERT INTO {self._tbname} ({columns}) VALUES ({placeholders})'
        return self._execute_sql(sql, tuple(user_coupon_data.values()))

    def update_user_coupon(self, user_coupon_id, update_data):
        """ 更新用户优惠券信息
            Args:
                user_coupon_id: 用户优惠券ID
                update_data: 需要更新的数据字典
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
        sql = f"UPDATE {self._tbname} SET {set_clause} WHERE id = %s"
        values = list(update_data.values()) + [user_coupon_id]
        return self._execute_sql(sql, tuple(values))

    def delete_user_coupon(self, user_coupon_id):
        """ 删除用户优惠券记录
            Args:
                user_coupon_id: 用户优惠券ID
            Return: 
                删除结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"DELETE FROM {self._tbname} WHERE id = %s"
        return self._execute_sql(sql, (user_coupon_id,))

    def get_all_user_coupons(self):
        """ 获取所有用户优惠券记录
            Args:
                None
            Return: 
                所有用户优惠券记录
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"SELECT * FROM {self._tbname}"
        return self._query_sql(sql)