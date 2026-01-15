# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 
'''
@file     :   company_db.py
@date     :   2025/03/10 00:00:00
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   公司数据库、佣金操作模型
'''

from src.model.base_db import PublicDbConnection

class CompanyDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()
        self._tbname = "ls_company"

    def get_company_by_id(self, company_id):
        """ 根据公司ID获取公司信息
            Args:
                company_id: 公司ID
            Return: 
                公司信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'SELECT * FROM {self._tbname} WHERE id = %s'
        return self._query_sql_one(sql, (company_id,))

class CompanyCommissionDb(PublicDbConnection):
    def __init__(self):
        super().__init__()
        self._tbname = "ls_company_comission"

    def get_commission_by_id(self, commission_id):
        """ 根据佣金ID获取佣金信息
            Args:
                commission_id: 佣金ID
            Return: 
                佣金信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'SELECT * FROM {self._tbname} WHERE id = %s'
        return self._query_sql_one(sql, (commission_id,))