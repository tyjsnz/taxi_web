# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   wechat_user_db.py
@date     :   2025/03/09 00:00:08
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   微信用户数据库操作
'''

from src.model.base_db import PublicDbConnection

class WechatUserDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()
        self._tbname = 'ls_wechat_user'

    def get_user_info(self, openid,col="*"):
        """ 获取用户信息
            Args:
                openid: 微信用户openid
                col: 返回列名，默认为*，如："id,username"
            Return: 
                用户信息
            @date:   2025/03/09 00:07:39
            @author: snz
        """
        sql = f"select {col} from {self._tbname} where openid='{openid}' limit 1"
        return self._query_sql_one(sql)
    
    def get_user_by_token(self,token,col="id"):
        """ 根据token获取用户信息
            Args:
                token: 用户token
                col: 返回列名，默认为id，如："id,username"
            Return: 
                用户信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"select {col} from {self._tbname} where token='{token}' limit 1"
        return self._query_sql_one(sql)
    
    def get_user_by_phone(self, phone, col="*"):
        """ 根据手机号获取用户信息
            Args:
                phone: 用户手机号
                col: 返回列名，默认为*，如："id,username"
            Return: 
                用户信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"SELECT {col} FROM {self._tbname} WHERE phone = %s"
        return self._query_sql_one(sql, (phone,))
    
    def get_user_by_openid(self, openid, col="*"):
        """ 根据openid获取用户信息
            Args:
                openid: 用户openid
                col: 返回列名，默认为*，如："id,username"
            Return: 
                用户信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"SELECT {col} FROM {self._tbname} WHERE openid = %s"
        return self._query_sql_one(sql, (openid,))

    def get_user_by_id(self, user_id,col='*'):
        """ 根据用户ID获取用户信息
            Args:
                user_id: 用户ID
                col: 返回列名，默认为*，如："id,username"
            Return: 
                用户信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"SELECT {col} FROM {self._tbname} WHERE id = %s"
        return self._query_sql_one(sql, (user_id,))

    def update_user_info(self, user_id, update_data):
        """ 更新用户信息
            Args:
                user_id: 用户ID
                update_data: 需要更新的数据字典
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
        sql = f"UPDATE {self._tbname} SET {set_clause} WHERE id = %s"
        values = list(update_data.values()) + [user_id]
        return self._execute_sql(sql, tuple(values))

    def delete_user(self, user_id):
        """ 删除用户
            Args:
                user_id: 用户ID
            Return: 
                删除结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"DELETE FROM {self._tbname} WHERE id = %s"
        return self._execute_sql(sql, (user_id,))

    def get_all_users(self):
        """ 获取所有用户信息
            Args:
                None
            Return: 
                所有用户信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"SELECT * FROM {self._tbname}"
        return self._query_sql(sql)
    
    def insert_user(self, user_data):
        """ 插入新用户信息
            Args:
                user_data: 包含用户信息的字典
            Return: 
                插入结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        keys = ', '.join(user_data.keys())
        placeholders = ', '.join(['%s'] * len(user_data))
        sql = f"INSERT INTO {self._tbname} ({keys}) VALUES ({placeholders})"
        values = tuple(user_data.values())
        return self._execute_sql(sql, values)