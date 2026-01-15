# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

from src.model.db_redis import PublicDbConnectionWithRedis


'''
数据业务逻辑处理，继续封装数据库连接池及redis缓存
'''
class PublicDbConnection(PublicDbConnectionWithRedis):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()

    def insert_data_by_dict(self, tb_name, dict_data):
        """ 通过字典形式插入记录
            Args:
                tb_name: 数据表名
                dict_data: 数据字典
            Return: 
                插入结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        columns = ', '.join(dict_data.keys())
        placeholders = ', '.join(['%s'] * len(dict_data))
        sql = f'INSERT INTO {tb_name} ({columns}) VALUES ({placeholders})'
        v = tuple(dict_data.values())

        return self._execute_sql(sql, v)
    
    def update_data_by_id(self, tb_name, dict_data, record_id):
        """ 根据字典，以指定的ID更新信息
            Args:
                tb_name: 数据表名
                dict_data: 需要更新的数据字典
                record_id: 更新的记录id
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        set_clause = ', '.join([f"{key} = %s" for key in dict_data.keys()])
        sql = f"UPDATE {tb_name} SET {set_clause} WHERE id = %s"
        values = list(dict_data.values()) + [record_id]
        return self._execute_sql(sql, tuple(values))