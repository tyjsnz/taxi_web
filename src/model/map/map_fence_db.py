# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   map_fence_db.py
@date     :   2025/03/10 08:09:16
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   地图电子围栏数据库操作
'''
from src.model.base_db import PublicDbConnection

class MapFenceDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()
        self._tbname = "ls_map_fence"

    def get_fence_by_id(self, fence_id):
        """ 根据电子围栏ID获取电子围栏信息
            Args:
                fence_id: 电子围栏ID
            Return: 
                电子围栏信息
            @date:   2025/03/10 08:09:16
            @author: snz
        """
        sql = f'SELECT * FROM {self._tbname} WHERE id = %s'
        return self._query_sql(sql, (fence_id,))

    def insert_fence(self, fence_data):
        """ 插入新的电子围栏记录
            Args:
                fence_data: 电子围栏数据字典
            Return: 
                插入结果
            @date:   2025/03/10 08:09:16
            @author: snz
        """
        columns = ', '.join(fence_data.keys())
        placeholders = ', '.join(['%s'] * len(fence_data))
        sql = f'INSERT INTO {self._tbname} ({columns}) VALUES ({placeholders})'
        return self._execute_sql(sql, tuple(fence_data.values()))

    def update_fence(self, fence_id, update_data):
        """ 更新电子围栏信息
            Args:
                fence_id: 电子围栏ID
                update_data: 需要更新的数据字典
            Return: 
                更新结果
            @date:   2025/03/10 08:09:16
            @author: snz
        """
        set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
        sql = f"UPDATE {self._tbname} SET {set_clause} WHERE id = %s"
        values = list(update_data.values()) + [fence_id]
        return self._execute_sql(sql, tuple(values))

    def delete_fence(self, fence_id):
        """ 删除电子围栏记录
            Args:
                fence_id: 电子围栏ID
            Return: 
                删除结果
            @date:   2025/03/10 08:09:16
            @author: snz
        """
        sql = f"DELETE FROM {self._tbname} WHERE id = %s"
        return self._execute_sql(sql, (fence_id,))

    def get_all_fences(self):
        """ 获取所有电子围栏记录
            Args:
                None
            Return: 
                所有电子围栏记录
            @date:   2025/03/10 08:09:16
            @author: snz
        """
        sql = f"SELECT * FROM {self._tbname}"
        return self._query_sql(sql)
    
    def get_all_fences_by_companyId(self,company_id):
        """ 获取指定公司的所有电子围栏记录
            Args:
                company_id: 公司ID
            Return: 
                所有电子围栏记录
            @date:   2025/03/10 08:09:16
            @author: snz
        """
        sql = f"SELECT * FROM {self._tbname} where company_id = {company_id}"
        return self._query_sql(sql)