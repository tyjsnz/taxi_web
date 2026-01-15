# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   order_db.py
@date     :   2025/03/10 00:00:00
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   订单数据库操作
'''
import time
import random
import string
from src.model.base_db import PublicDbConnection

class OrderDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()
        self._tbname = "ls_order"

    def get_order_status(self, order_id):
        # 订单状态
        sql = f'SELECT status FROM {self._tbname} WHERE id = %s'
        result = self._query_sql_one(sql, (order_id,))
        return result['status'] if result else None
                
    def get_order_by_id(self, order_id, col='*'):
        """ 根据订单ID获取订单信息
            Args:
                order_id: 订单ID
                col: 查询字段，默认为*
            Return: 
                订单信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'SELECT {col} FROM {self._tbname} WHERE id = %s'
        row = self._query_sql_one(sql, (order_id,),use_cache=False)
        if row is None:
            return None
        sql = f"select * from ls_order_fee_details where order_id = {order_id} limit 1"
        ret = self._query_sql_one(sql,use_cache=False)
        row['fee_detail'] = ret
        
        # 最后一次司机的位置，取行程导航推送数据
        sql = f"select latlng from ls_navi where order_id = {order_id} order by id desc limit 1"
        ret_nav = self._query_sql_one(sql,use_cache=False)
        if ret_nav:
            _latlng = ret_nav['latlng'].split(',')
            row['driver_last_lat'] = _latlng[1]
            row['driver_last_lng'] = _latlng[0]
        else:
            row['driver_last_lat'] = 0
            row['driver_last_lng'] = 0
        return row


    def insert_order(self, order_data):
        """ 插入新订单
            Args:
                order_data: 订单数据字典
            Return: 
                插入结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        columns = ', '.join(order_data.keys())
        placeholders = ', '.join(['%s'] * len(order_data))
        sql = f'INSERT INTO {self._tbname} ({columns}) VALUES ({placeholders})'
        return self._execute_sql(sql, tuple(order_data.values()))

    def update_order_status(self, order_id, status):
        """ 更新订单状态
            Args:
                order_id: 订单ID
                status: 新状态 (参见订单状态常量定义 const_defined.py)
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'UPDATE {self._tbname} SET status = %s WHERE id = %s'
        return self._execute_sql(sql, (status, order_id))
    
    def update_order_driver(self,id,driver_id):
        """更新订单接单司机信息
        """
        sql = f'UPDATE {self._tbname} SET driver_id = %s WHERE id = %s'
        return self._execute_sql(sql,(driver_id,id))
    
    def update_order(self,id,dict_data):
        """更新订单记录
        """
        return self.update_data_by_id(self._tbname,dict_data,id)

    def delete_order(self, order_id):
        """ 删除订单
            Args:
                order_id: 订单ID
            Return: 
                删除结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'DELETE FROM {self._tbname} WHERE id = %s'
        return self._execute_sql(sql, (order_id,))
    
    def generate_order_sn(self):
        """ 生成订单号
            Return: 
                20位订单号
        """
        # 获取当前时间戳
        timestamp = int(time.time() * 1000)  # 毫秒级时间戳

        # 获取一个自增序列号
        sequence_number = self.get_next_sequence_number()

        # 生成随机字符串
        #random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        # 组合订单号{random_str}
        order_sn = f"{timestamp:013d}{sequence_number:07d}"
        return order_sn

    def get_next_sequence_number(self):
        """ 获取下一个订单的自增序列号
            Return:
                自增序列号
        """
        sql = "INSERT INTO ls_order_sequence (id) VALUES (0) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id+1)"
        self._execute_sql(sql)
        sql = "SELECT LAST_INSERT_ID() as id"
        result = self._query_sql(sql)
        return result[0]["id"]
    
    def total_order_status_data(self,company_id='',btime='',etime=''):
        """ 统计各状态的订单数据，数量及金额
            Args:
                company_id: 公司ID
                btime: 开始时间
                etime: 结束时间
            Return: 
                {'status':0,'total_count':0,'total_amount':0}
            @date:   2025/04/20 14:01:40
            @author: snz
        """
        # 0=待接单,1=已接单,2=乘客已上车,3=进行中,4=到达目的地(未支付)，5=已完成（支付),-1=用户取消，-2=无司机接单

        where = 'id > 0'
        if company_id != '':
            where += f" AND company_id = '{company_id}'"
        if btime != '' and etime != '':
            where += f" AND order_time >= '{btime}' AND order_time <= '{etime}'"

        sql = f"""
        SELECT 
            status,
            COUNT(*) AS total_count,
            SUM(amount) AS total_amount
        FROM {self._tbname}
        WHERE {where}
        GROUP BY status
        """

        result = self._query_sql(sql)
        return result
        