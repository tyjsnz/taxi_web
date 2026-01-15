# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   taxi_fee_settings_db.py
@date     :   2025/03/21 16:54:23
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   出租车费用设置数据库
'''
from src.model.base_db import PublicDbConnection

class TaxiFeeSettingsDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()
        self._tbname = "ls_taxi_fee_settings"

    def get_taxi_fee_settings_by_starttime(self, taxi_time):
        """ 获取出租车费用设置
            Args:
                taxi_time: 打车时间 ，12:12:23 时间部分 datetime.strptime(taxi_time, '%Y-%m-%d %H:%M:%S').time()可取出
            Return: 
                所有加盟商对应的价格配置
            @date:   2025/03/21 17:49:16
            @author: snz
        """

        query = f"select a.*,c.short_name from {self._tbname} as a, ls_company as c where a.company_id=c.id and '{taxi_time}' >= start_time and '{taxi_time}' <=end_time"
        result = self._query_sql(query)
        if result is None or len(result) == 0:
            # 找出默认时段
            query = f"select a.*,c.short_name from {self._tbname} as a, ls_company as c where a.company_id=c.id and is_default=1"
            result = self._query_sql(query)
            
        # 公司的时段未设置时，选有默认时段的记录，不管存在与否
        if result is None:
            query =  f"select a.*,c.short_name from {self._tbname} as a,ls_company as c where a.company_id=c.id and is_default = 1 limit 1"
            result = self._query_sql_one(query)
            
        return result
        
    def get_taxi_fee_settings_by_starttime_and_company_id(self, company_id, taxi_time):
        """ 根据公司ID获取出租车费用设置音单记录
            Args:
                taxi_time: 打车时间 ，12:12:23 时间部分 datetime.strptime(taxi_time, '%Y-%m-%d %H:%M:%S').time()可取出
            Return: 
                所有加盟商对应的价格配置
            @date:   2025/03/21 17:49:16
            @author: snz
        """

        query = f"select a.*,c.short_name from {self._tbname} as a,ls_company as c where a.company_id=c.id and company_id={company_id} and '{taxi_time}' >= start_time and '{taxi_time}' <=end_time limit 1"
        result = self._query_sql_one(query)
        if result is None:
            # 找出默认时段
            query = f"select a.*,c.short_name from {self._tbname} as a,ls_company as c where a.company_id=c.id and company_id={company_id} and is_default=1 limit 1"
            result = self._query_sql_one(query)
            
        # 公司的时段未设置时，选有默认时段的记录，不管存在与否
        if result is None:
            query =  f"select a.*,c.short_name from {self._tbname} as a,ls_company as c where a.company_id=c.id and is_default = 1 limit 1"
            result = self._query_sql_one(query)
            
        return result