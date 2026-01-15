# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   order_controller.py
@date     :   2025/03/10 07:39:52
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   App,wechat端统计数据控制器
'''

from src.model.order.order_db import OrderDb
from src.helper.helper import *

class AppTotalController():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        super().__init__()
        self._db = OrderDb()
        
    def get_order_total(self):
        """ 获取订单统计数据
        Args:
            None
        Return:
            订单统计数据
        @date:   2025/03/10 07:39:52
        """
        hour = get_param_by_str('hour')
        where = "id > 0"
        if hour != '':
            where += f" and hour = {hour}"
            
        btime = get_param_by_str('btime')
        etime = get_param_by_str('etime')
        if btime != '' and etime != '':
            where += f" and created_at between '{btime}' and '{etime}'"
        else:
            btime,etime = get_current_begin_end_time()
            where += f" and created_at between '{btime}' and '{etime}'"
            
        sql = f"select * from ls_order_hours_total where {where} order by hour desc"
        result = self._db._query_sql(sql)
        
        return echo_json(0, "success", result)
    
    def get_order_total_by_day(self):
        """ 获取当天订单统计数据，及指定前几天的数据
        Args:
            None
        Return:
            订单统计数据
        @date:   2025/03/10 07:39:52
        """
        day = get_param_by_int('day')
        
        # 获取当天数据
        btime,etime = get_current_begin_end_time()
        where = f"created_at between '{btime}' and '{etime}'"
            
        sql = f"select * from ls_order_hours_total where {where} order by hour desc"
        result = self._db._query_sql(sql)
        
        # -1为前1天，1=后1天
        btime,etime = get_n_days_ago(day)
        where = f"created_at between '{btime}' and '{etime}'"
        sql = f"select * from ls_order_hours_total where {where} order by hour desc"
        pre_nex_result = self._db._query_sql(sql)
        
        return echo_json(0, "success", {'current':result,'pre_next':pre_nex_result})

    def get_heatmap_data(self):
        """ 获取热力图数据"""
        
        where = "id > 0"
        btime = get_param_by_str('btime')
        etime = get_param_by_str('etime')
        if btime != '' and etime != '':
            where += f" and created_at between '{btime}' and '{etime}'"
        else:
            btime,etime = get_current_begin_end_time()
            where += f" and created_at between '{btime}' and '{etime}'"
            
        sql = f"select * from ls_order_heatmap where {where} order by created_at desc"
        result = self._db._query_sql(sql,use_cache=False)
        
        return echo_json(0, "success", result)