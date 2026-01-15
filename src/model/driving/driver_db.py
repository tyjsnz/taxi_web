# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   driver_db.py
@date     :   2025/03/08 23:51:13
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   司机端数据库操作
'''

from src.model.base_db import PublicDbConnection
from src.helper.helper import *
from src.common.const_defined import *

class DriverDb(PublicDbConnection):
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()
        self._tbname = "ls_driver"

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
        return self._query_sql_one(sql, (username, password),use_cache=False)
    
    def get_user_info_by_id(self, uid,col='*'):
        # 根据用户ID获取用户信息
        sql = f'SELECT {col} FROM {self._tbname} WHERE id = %s'
        row = self._query_sql_one(sql, (uid,),use_cache=False)
        
        if row:
            row['today_online_total_time'] = 0
            row['total_online_time'] = 0
            # 获取当天在线时长
            btime,etime = get_current_begin_end_time()
            sql = f"select sum(online_total_time) as online_total_time from ls_driver_online_time where driver_id = {uid} and created_at between '{btime}' and '{etime}'"
            ret = self._query_sql_one(sql,use_cache=False)
            if ret:
                row['today_online_total_time'] = ret['online_total_time']
            # 总在线时长
            row['total_online_time'] = self.get_driver_total_online_time(uid)
                
        return row
    
    def get_user_info_by_token(self, token,col='*'):
        # 根据用token获取用户信息
        sql = f'SELECT {col} FROM {self._tbname} WHERE token = %s'
        return self._query_sql_one(sql, (token,),use_cache=False)

    def insert_driver(self, driver_data):
        """ 插入新的司机记录
            Args:
                driver_data: 司机数据字典
            Return: 
                插入结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        columns = ', '.join(driver_data.keys())
        placeholders = ', '.join(['%s'] * len(driver_data))
        sql = f'INSERT INTO {self._tbname} ({columns}) VALUES ({placeholders})'
        return self._execute_sql(sql, tuple(driver_data.values()))

    def update_driver_info(self, driver_id, update_data):
        """ 更新司机信息
            Args:
                driver_id: 司机ID
                update_data: 需要更新的数据字典
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
        sql = f"UPDATE {self._tbname} SET {set_clause} WHERE id = %s"
        values = list(update_data.values()) + [driver_id]
        return self._execute_sql(sql, tuple(values))

    def delete_driver(self, driver_id):
        """ 删除司机记录，对应所有相关表均删除，目前证照不删除
            Args:
                driver_id: 司机ID
            Return: 
                删除结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"DELETE FROM {self._tbname} WHERE id = %s"
        ret = self._execute_sql(sql, (driver_id,))
        if ret:
            # 删除资金
            sql = f"delete from ls_driver_account where driver_id={driver_id}"
            self._execute_sql(sql)
            # 删除定位
            sql = f"delete from ls_driver_location where driver_id=%s"
            self._execute_sql(sql,(driver_id,))
            # 抢单库
            sql = f"delete from ls_driver_order_accept where driver_id=%s"
            self._execute_sql(sql,(driver_id,))
        return ret

    def get_all_drivers(self):
        """ 获取所有司机信息
            Args:
                None
            Return: 
                所有司机信息
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        sql = f"SELECT * FROM {self._tbname}"
        return self._query_sql(sql)
    
    def add_score_rewards_log(self,driver_id,score,remark):
        """ 添加司机积分奖励记录
            Args:
                driver_id: 司机ID
                score: 积分
                remark: 备注
            Return: 
                插入结果
            @date:   2025/03/10 00:00:00
            @author: snz
        """
        
        ret = self.insert_data_by_dict("ls_driver_score_log",{'driver_id': driver_id,'score': score, 'remark': remark, 'created_at': get_current_time()})
        if ret:
            sql = f"select score from {self._tbname} where id = {driver_id}"
            row = self._query_sql_one(sql)
            if row:
                score = row['score'] + score
                self.update_data_by_id(self._tbname,{'score': score})
        return ret
    
    def verify_phone(self,phone):
        ''' 验证手机号是否已存在
            Args:
                phone: 
            Return: 
                存在返回ID，不存在返回0
            @date:   2025/05/04 16:35:24
            @author: snz
        '''
        sql = f"select id from {self._tbname} where phone = %s"
        ret = self._query_sql_one(sql,(phone,))
        if ret:
            return ret['id']
        else:
            return 0
        
    def update_driver_online_time(self, driver_id,work_status):
        """ 更新司机在线时间
            Args:
                driver_id: 司机ID
                work_status: 工作状态(1=上班，0=下班)
            Return: 
                更新结果
            @date:   2025/03/10 00:00:00
        """
         # 更新在线时长
        btime,etime = get_current_begin_end_time()
        sql = f"select * from ls_driver_online_time where driver_id={driver_id} and created_at between '{btime}' and '{etime}'"
        row = self._query_sql_one(sql)
        
        # 如果当前时间在上班时间内，则更新在线时长
        if row is None:
            if work_status == DRIVER_WORK_STATUS.WORK_ON:
                # 如果没有记录，则插入
                data = {
                    'driver_id': driver_id,
                    'online_total_time': 0,
                    'created_at': get_current_time()
                }
                self.insert_data_by_dict('ls_driver_online_time',data)
        else:
            # 上班状态，则更新在线时长计时开始时间
            if work_status == DRIVER_WORK_STATUS.WORK_ON:
                self.update_data_by_id('ls_driver_online_time',{'created_at': get_current_time()},row['id'])
            else:
                # 如果有记录，则更新
                online_total_time = row['online_total_time']
                btime = row['created_at']
                # 计算在线时长，首次插入记录的时间与当前时间的差值
                diff_sec = diff_seconds(btime,get_current_time())
                
                if online_total_time is None or online_total_time == '':
                    online_total_time = 0
                else:
                    online_total_time = int(online_total_time)
                
                # 更新在线时长
                online_total_time += diff_sec
                self.update_data_by_id('ls_driver_online_time',{'online_total_time':online_total_time,'created_at': get_current_time()},row['id'])
                # 主表更新当天在线时长
                self.update_driver_info(driver_id, {'today_online_total_time': online_total_time})
        
        # 统计总在线时长更新至主表
        # 更新主表在线时长
        self.update_driver_info(driver_id, {'total_online_time': self.get_driver_total_online_time(driver_id)})
        
        return True
    
    def get_driver_total_online_time(self, driver_id):
        """ 获取司机在线时长
            Args:
                driver_id: 司机ID
            Return: 
                在线时长
            @date:   2025/03/10 00:00:00
        """
        sql = f"select sum(online_total_time) as online_total_time from ls_driver_online_time where driver_id={driver_id}"
        row = self._query_sql_one(sql)
        if row:
            return row['online_total_time']
        else:
            return 0
        
    
        
    def get_driver_service_score_list(self,driver_id):
        """ 获取司机服务评分
            Args:
                driver_id: 司机ID
            Return: 
                服务评分
            @date:   2025/03/10 00:00:00
        """
        sql = f"select * from ls_driver_score_log where driver_id = {driver_id} order by id desc"
        row = self._query_sql(sql)
        return row
        
    def get_driver_service_score(self,driver_id):
        """ 获取司机服务评分
            Args:
                driver_id: 司机ID
            Return: 
                服务评分
            @date:   2025/03/10 00:00:00
        """
        sql = f"select sum(score) as score from ls_driver_score_log where driver_id = {driver_id}"
        row = self._query_sql_one(sql)
        if row:
            return float_ex(row['score'])
        else:
            return 0