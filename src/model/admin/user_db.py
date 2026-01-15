# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 
'''
@file     :   user_db.py
@date     :   2025/03/09 00:15:35
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   后端用户数据库操作,包含调度端用户
'''

from src.model.base_db import PublicDbConnection

class UserDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        super().__init__()
        self._tbname = 'ls_user'

    def get_user_info_by_id(self,id):
        sql = f"select * from {self._tbname} where id = %s"
        return self._query_sql_one(sql, (id,))
    
    def get_user_info(self, username, password, columns='*'):
        """ 获取用户信息
            Args:
                username: 用户名
                password: 密码
                columns: 查询字段 
            Return: 
                None
            @date:   2025/03/09 00:06:38
            @author: snz
        """
        sql = f'SELECT {columns} FROM {self._tbname} WHERE username = %s AND password = %s limit 1'
        return self._query_sql_one(sql, (username, password))