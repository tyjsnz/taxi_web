# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   driver_account_db.py
@date     :   2025/03/10 00:00:00
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   司机帐目数据库操作
'''

from src.model.base_db import PublicDbConnection

class DriverAccountDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()
        self._tbname = "ls_driver_account"

    def get_account_info_by_driver_id(self, driver_id):
        """ 根据司机ID获取帐目信息
            Args:
                driver_id: 司机ID
            Return: 
                帐目信息列表
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f'SELECT * FROM {self._tbname} WHERE driver_id = %s'
        return self._query_sql(sql, (driver_id,))

    def insert_driver_account(self, account_data):
        """ 插入新的司机帐目记录
            Args:
                account_data: 帐目数据字典
            Return: 
                插入结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        columns = ', '.join(account_data.keys())
        placeholders = ', '.join(['%s'] * len(account_data))
        sql = f'INSERT INTO {self._tbname} ({columns}) VALUES ({placeholders})'
        return self._execute_sql(sql, tuple(account_data.values()))

    def update_driver_account(self, account_id, update_data):
        """ 更新司机帐目信息
            Args:
                account_id: 帐目ID
                update_data: 需要更新的数据字典
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
        sql = f"UPDATE {self._tbname} SET {set_clause} WHERE id = %s"
        values = list(update_data.values()) + [account_id]
        return self._execute_sql(sql, tuple(values))

    def delete_driver_account(self, account_id):
        """ 删除司机帐目记录
            Args:
                account_id: 帐目ID
            Return: 
                删除结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"DELETE FROM {self._tbname} WHERE id = %s"
        return self._execute_sql(sql, (account_id,))

    def get_all_accounts(self):
        """ 获取所有司机帐目记录
            Args:
                None
            Return: 
                所有司机帐目记录
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"SELECT * FROM {self._tbname}"
        return self._query_sql(sql)
    
    def get_account_by_id(self, driver_id):
        """ 根据司机ID获取司机帐目记录
            Args:
                driver_id: 司机ID
            Return: 
                司机帐目记录
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"SELECT * FROM {self._tbname} WHERE id = {driver_id}"
        return self._query_sql_one(sql)
    
    def total_account_by_id(self, driver_id,begin_time = '', end_time = ''):
        """ 根据司机ID获取司机总帐目记录
            Args:
                driver_id: 司机ID
                begin_time: 开始时间
                end_time: 结束时间
            Return: 
                [收入，支出]
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        # 入帐金额
        sql = f"select sum(amount) as fee from {self._tbname} where driver_id = {driver_id} and amount > 0"
        if begin_time != '' and end_time != '':
            sql += f" and created_at between '{begin_time}' and '{end_time}'"
            
        in_pay = self._query_sql_one(sql)
        if in_pay:
            in_pay = in_pay['fee']
        in_pay = float(in_pay) if in_pay else 0
            
        # 提现金额
        sql = f"select sum(amount) as fee from {self._tbname} where driver_id = {driver_id} and amount < 0"
        if begin_time != '' and end_time != '':
            sql += f" and created_at between '{begin_time}' and '{end_time}'"
            
        out_pay = self._query_sql_one(sql)
        if out_pay:
            out_pay = out_pay['fee']
        out_pay = float(out_pay) if out_pay else 0
            
        return [in_pay, out_pay]
    
    def get_driver_balance_by_id(self, driver_id):
        """ 根据司机ID获取司机总余额记录
            Args:
                driver_id: 司机ID
            Return: 
                [余额，收入，支出]
            @date:   2025/03/10 00:00:00
        """
        sql = f"select sum(amount) as fee from {self._tbname} where driver_id = {driver_id}"
        total_pay = self._query_sql_one(sql)
        if total_pay:
            total_pay = total_pay['fee']
            
        total_pay = float(total_pay) if total_pay else 0
        return total_pay
        
    def get_driver_account_detail(self,driver_id,begin_time = '', end_time = ''):
        """ 根据司机ID获取司机订单帐目记录
            Args:
                driver_id: 司机ID
                begin_time: 开始时间
                end_time: 结束时间
            Return: 
                司机帐目记录: [订单记录,订单数量,订单金额]
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        where = f"driver_id = {driver_id}"
        if begin_time != '' and end_time != '':
            where += f" and created_at between '{begin_time}' and '{end_time}'"
            
        sql = f"select sum(amount) as fee,count(*) as num from v_driver_account where {where}"
        ret = self._query_sql_one(sql)
        num = ret['num'] if ret else 0
        fee = ret['fee'] if ret else 0
        
        sql = f"select * from v_driver_account where {where}"
        result = self._query_sql(sql)
        return result,num,fee
        