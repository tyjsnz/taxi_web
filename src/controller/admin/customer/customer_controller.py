# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 
from flask import session,request,redirect,url_for
from src.helper.helper import *
from src.controller.admin.base_controller import *
from src.common.const_defined import ORDER_STATUS,USER_STATUS
from src.model.wechat.wechat_user_db import WechatUserDb
class CustomerController(BaseController):
    def __init__(self):
        super().__init__()
        self.db = WechatUserDb()
      
    def get_customer_list(self):
        """获取客户列表"""
        pageindex,pagesize = get_page_param()
        pageindex = pageindex - 1 if pageindex > 1 else 0
        pageindex = pageindex * pagesize
        phone = get_param_by_str('phone')
        where = ''
        if phone != '':
            where = f"where phone like '{phone}%'"
        sql = f"select count(*) as total from ls_wechat_user {where}"
        ret = self.db._query_sql_one(sql)
        record_total = ret['total']

        sql = f"select * from ls_wechat_user {where} order by last_time desc limit {pageindex},{pagesize}"
        result = self.db._query_sql(sql)

        # 乘客对应订单数量及订单价格,及优惠券
        for row in result:
            row['order_num'] = 0
            row['order_total_amount'] = 0
            sql = f"select count(id) as num from ls_order where customer_id={row['id']} and status={ORDER_STATUS.COMPLETED}"
            num = self.db._query_sql_one(sql)
            if num:
                row['order_num'] = num['num']
            sql = f"select sum(total_fee) as total from ls_order where customer_id={row['id']} and status={ORDER_STATUS.COMPLETED}"
            total = self.db._query_sql_one(sql)
            if total:
                row['order_total_amount']
            sql = f"select count(id) as num from ls_coupons_list where uid={row['id']}"
            ret = self.db._query_sql_one(sql)
            if ret:
                row['coupons_num'] = ret['num']                

        return echo_json(0,"",result,record_total)
    
    def update_user_status(self):
        """更新乘客状态"""
        status = get_param_by_json('status')
        id = get_param_by_json('id')

        if status not in [USER_STATUS.DISABLE,USER_STATUS.NORMAL]:
            return echo_json(-1,"用户状态不正确")
        
        ret = self.db.update_user_info(id,{'status': status})
        return echo_json(0,'success')