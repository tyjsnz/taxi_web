# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   driver_order_accept_db.py
@date     :   2025/03/28 01:46:58
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   司机接单数据库操作
'''

from src.model.base_db import PublicDbConnection
from src.common.const_defined import *
from src.helper.helper import *

class DriverOrderAcceptDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        super().__init__()
        self._tbname = 'ls_driver_order_accept'

    def insert_data(self, data):
        """ 插入抢单的司机记录
            Args:
                data: 数据字典
            Return: 
                插入结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        return self.insert_data_by_dict(self._tbname, data)
    
    def get_one(self,id):
        """ 获取一条记录
            Args:
                id: 记录ID
            Return: 
                记录
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"select * from {self._tbname} where id = {id}"
        return self._query_sql_one(sql)
    
    def get_list_by_reject_order_id(self,order_id):
        """ 获取司机对应订单的拒绝记录
            Args:
                order_id: 订单ID
            Return: 
                记录列表
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"select * from ls_driver_reject_log where order_id = {order_id}"
        return self._query_sql(sql)
    
    def total_driver_reject_by_date(self,driver_id,btime='',e_time=''):
        """ 获取司机被拒绝的订单记录
            Args:
                driver_id: 司机ID
                btime: 开始时间
                e_time: 结束时间
            Return: 
                记录数量
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        where = f"driver_id = {driver_id}"
        if btime != '' and e_time != '':
            where += f" and created_at >= '{btime}' and created_at <= '{e_time}'"
        sql = f"select count(*) as num from ls_driver_reject_log where {where}"
        ret = self._query_sql_one(sql)
        return ret['num'] if ret else 0
    
        
    def get_list_by_driver_id(self,driver_id,page=1,page_size=10,max_second=0):
        """ 获取司机的订单可抢单记录
            Args:
                driver_id: 司机ID
                page: 页码
                page_size: 每页数量
                max_second: 之前多少分秒内的数据
            Return: 
                记录列表
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        
        page = int_ex(page)
        page_size = int_ex(page_size)
        page = page - 1 if page > 0 else 0
        page = page * page_size
        where = ''
        if max_second > 0:
            where = f" AND order_time >= NOW() - INTERVAL {max_second} SECOND"
        sql = f"SELECT * from v_accept_order where driver_id = {driver_id} and `accept_status`!= {DRIVER_ACCEPT_STATUS.REJECT_ACCEPT} and status={ORDER_STATUS.PENDING} {where} order by order_time desc limit {page}, {page_size}"
        
        return self._query_sql(sql)
        

    def delete_order_by_order_id(self,order_id):
        """删除抢单池中的订单记录"""
        sql = f"delete from {self._tbname} where order_id = {order_id}"
        return self._execute_sql(sql)
    
    def update_all_order_status(self, order_id, status):
        """ 更新订单状态，更新订单下发给司机的所有记录状态，在司机端无人接单情况下使用
            Args:
                order_id: 订单ID
                status: 订单状态
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"update {self._tbname} set status = {status} where order_id = {order_id}"
        return self._execute_sql(sql)
    
    def update_order_status_by_id(self, id, status):
        """ 更新订单状态
            Args:
                id: 记录ID
                status: 订单状态
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"update {self._tbname} set status = {status} where id = {id}"
        return self._execute_sql(sql)

    def update_order_status_by_dict(self, id, dict_data):
        """ 更新订单状态
            Args:
                id: 记录ID
                dict_data: 数据字典
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        return self.update_data_by_id(self._tbname, dict_data, id)
    
    def update_order_all_status_by_dict(self, order_id, status):
        """ 更新指定订单ID的所有订单状态
            Args:
                id: 记录ID
                status: 订单状态
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"update {self._tbname} set status = {status} where order_id = {order_id}"
        return self._execute_sql(sql)
    
    def get_order_accept_by_order_id(self, order_id, driver_id):
        """ 获取订单是否已经下发过抢单数据
            Args:
                order_id: 订单ID
                driver_id: 司机ID
            Return: 
                None 表示没有记录
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"select id from {self._tbname} where order_id = {order_id} and driver_id = {driver_id}"
        return self._query_sql_one(sql)
    
    def add_driver_reject(self,order_id,driver_id):
        """ 添加司机拒绝记录，如存在则更新
            Args:
                order_id: 订单ID
                driver_id: 司机ID
            Return: 
                插入结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"select num,id from ls_driver_reject_log where order_id={order_id} and driver_id={driver_id}"
        row = self._query_sql_one(sql)
        if row:
            num = row['num'] + 1
            return self.update_data_by_id("ls_driver_reject_log",{'num': num,'created_at': get_current_time()},row['id'])
        
        return self.insert_data_by_dict("ls_driver_reject_log",{'order_id': order_id, 'driver_id': driver_id, 'num': 1,'created_at': get_current_time()})    
            