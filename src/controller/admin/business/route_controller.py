# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 
from tkinter import NO
from flask import session,request,redirect,url_for
from src.helper.helper import *
from src.controller.admin.base_controller import *
from src.common.const_defined import ORDER_STATUS,USER_STATUS
from src.model.base_db import PublicDbConnection

class RouteController(BaseController):
    def __init__(self):
        super().__init__()
        self.db = PublicDbConnection()

    def get_one(self):
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(-1,"id为空")
        
        row = self.db._query_sql_one(f"select * from intercity_route where id={id}")
        return row

    def add(self):
        # 新增城际路线
        data = {
            'start_city': get_param_by_json('start_city'),
            'end_city': get_param_by_json('end_city'),
            'start_station': get_param_by_json('start_station'),
            'end_station': get_param_by_json('end_station'),
            'car_type': get_param_by_json('car_type'),
            'price': float(get_param_by_json('price')),
            'estimated_time': int(get_param_by_json('estimated_time')),
            'status': int(get_param_by_json('status')),
            'remark': get_param_by_json('remark')
        }
        _id = self.db.insert_data_by_dict('intercity_route', data)
        if _id:
            return echo_json(0, '添加成功')
        return echo_json(-1, '添加失败')
    
    def update_status(self):
        # 更新路线状态
        id = int(get_param_by_json('id'))
        if id <= 0:
            return echo_json(-1, "id为空")
        status = get_param_by_json('status')
        ret = self.db.update_data_by_id('intercity_route', {'status': status}, id)
        if ret:
            return echo_json(0, '更新成功')
        
        return echo_json(-1, '更新失败')

    def update(self):
        id = int(get_param_by_json('id'))
        if id <= 0:
            return echo_json(-1, "id为空")
        
        data = {
            'start_city': get_param_by_json('start_city'),
            'end_city': get_param_by_json('end_city'),
            'start_station': get_param_by_json('start_station'),
            'end_station': get_param_by_json('end_station'),
            'car_type': get_param_by_json('car_type'),
            'price': float(get_param_by_json('price')),
            'estimated_time': int(get_param_by_json('estimated_time')),
            'status': int(get_param_by_json('status')),
            'remark': get_param_by_json('remark')
        }
        
        ret = self.db.update_data_by_id('intercity_route', data, id)
        if ret is not None:
            return echo_json(0, '更新成功')
        
        return echo_json(-1, '更新失败')
    
    def delete(self):
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(-1, "id为空")
        
        sql = f"delete from intercity_route where id={id}"
        ret = self.db._execute_sql(sql)
        if ret:
            return echo_json(0, '删除成功')
        
        return echo_json(-1, '删除失败')
    
    def get_list(self):
        pageindex, pagesize = get_page_param()
        pageindex = pageindex - 1 if pageindex > 1 else 0
        pageindex = pageindex * pagesize

        start_city = get_param_by_str('start_city')
        end_city = get_param_by_str('end_city')
        status = get_param_by_str('status')

        where = 'id > 0'
        if start_city != '':
            where += f" and start_city like '%{start_city}%'"
        if end_city != '':
            where += f" and end_city like '%{end_city}%'"
        if status != '':
            where += f" and status={status}"

        sql = f"select count(id) as num from intercity_route where {where}"
        ret = self.db._query_sql_one(sql)
        num = ret['num']

        sql = f"select * from intercity_route where {where} limit {pageindex},{pagesize}"
        result = self.db._query_sql(sql)

        return echo_json(0, 'success', result, num)