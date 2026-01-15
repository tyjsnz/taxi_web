# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   coupons_db.py
@date     :   2025/03/10 00:00:00
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   优惠券数据库操作
'''

from src.model.base_db import PublicDbConnection

class CouponsDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()
        self._tbname = "ls_coupons"

    def get_my_coupon_list(self, user_id,status=-1):
        """ 获取用户领取的优惠券列表
            Args:
                user_id: 用户ID
                status: 优惠券状态,-1为全部
            Return: 
                优惠券列表
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"select * from v_user_coupon where uid = {user_id} and status={status}"
        if status == -1:
            sql = f"select * from v_user_coupon where uid = {user_id}"
        return self._query_sql(sql,use_cache=False)
    
    def get_coupon_by_id(self, coupon_id):
        """ 根据优惠券ID获取优惠券信息
            Args:
                coupon_id: 优惠券ID
            Return: 
                优惠券信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'SELECT * FROM {self._tbname} WHERE id = %s'
        return self._query_sql(sql, (coupon_id,))

    def insert_coupon(self, coupon_data):
        """ 插入新的优惠券记录
            Args:
                coupon_data: 优惠券数据字典
            Return: 
                插入结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        columns = ', '.join(coupon_data.keys())
        placeholders = ', '.join(['%s'] * len(coupon_data))
        sql = f'INSERT INTO {self._tbname} ({columns}) VALUES ({placeholders})'
        return self._execute_sql(sql, tuple(coupon_data.values()))

    def update_coupon(self, coupon_id, update_data):
        """ 更新优惠券信息
            Args:
                coupon_id: 优惠券ID
                update_data: 需要更新的数据字典
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
        sql = f"UPDATE {self._tbname} SET {set_clause} WHERE id = %s"
        values = list(update_data.values()) + [coupon_id]
        return self._execute_sql(sql, tuple(values))

    def delete_coupon(self, coupon_id):
        """ 删除优惠券记录
            Args:
                coupon_id: 优惠券ID
            Return: 
                删除结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"DELETE FROM {self._tbname} WHERE id = %s"
        return self._execute_sql(sql, (coupon_id,))

    def get_all_coupons(self):
        """ 获取所有优惠券记录
            Args:
                None
            Return: 
                所有优惠券记录
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"SELECT * FROM {self._tbname}"
        return self._query_sql(sql)
    
    def take_coupon_is_exists(self, coupon_id, user_id):
        """ 判断用户是否领取过优惠券
            Args:
                coupon_id: 优惠券ID
                user_id: 用户ID
            Return: 
                领取结果True为领取过，反之
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"select id from ls_coupons_list where coupon_id = {coupon_id} and uid = {user_id}"
        ret = self._query_sql_one(sql,use_cache=False)
        if ret:
            return True
        
        return False
        
    def take_coupon(self, coupon_id, user_id):
        """ 用户领取优惠券
            Args:
                coupon_id: 优惠券ID
                user_id: 用户ID
            Return: 
                领取结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"INSERT INTO ls_coupons_list (coupon_id, uid) VALUES ({coupon_id},{user_id})"
        return self._execute_sql(sql)