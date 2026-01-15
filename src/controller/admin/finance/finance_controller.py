# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

# -*- encoding: utf-8 -*-
'''
@file     :   finance_controller
@date     :   2025/04/20 07:31:48
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   财务管理控制器
'''

from flask import session,request,redirect,url_for
from src.helper.helper import *
from src.controller.admin.base_controller import *
from src.model.driving.driver_db import DriverDb
import struct
from src.common.const_defined import DRIVER_CASH_VERIFY_STATUS,ORDER_STATUS,COMMISSION_SETTLE_STATUS
from datetime import datetime, timedelta

class FinanceController(BaseController):
    def __init__(self):
        super().__init__()
        self.db = DriverDb()

    def total_data(self):
        """ 数据统计
            Args:
                : 
            Return: 
                None
            @date:   2025/04/20 14:00:40
            @author: snz
        """
        # 总订单数量
        pass
    def get_commission_list(self):
        # 佣金列表
        pageindex,pagesize = get_page_param()
        if pageindex > 0:
            pageindex = pageindex - 1
        pageindex = pageindex * pagesize
        name = get_param_by_str('name')
        phone = get_param_by_str('phone')
        company = get_param_by_str('company')
        car_no = get_param_by_str('car_no')
        btime = get_param_by_str('btime')
        etime = get_param_by_str('etime')
        
        where = ''
        if name != '':
            where += f" and truename like '%{name}%'"
        if phone != '':
            where += f" and phone='{phone}'"
        if car_no != '':
            where += f" and car_no='{car_no}'"
        if company != '':
            where += f" and company_id={company}"
        if btime != '' and etime != '':
            if ":" not in btime:
                btime += " 00:00:00"
            if ":" not in etime:
                etime += " 23:59:59"
            where += f" and created_at between '{btime}' and '{etime}'"

        sql = f"select count(id) as num from ls_driver where id > 0 {where}"
        ret = self.db._query_sql_one(sql)
        num = ret['num']
        
        # sql = f"select * from ls_driver where {where} order by created_at desc limit {pageindex},{pagesize}"
        # result = self.db._query_sql(sql)
        # # 接单数量
        # for row in result:
        #     sql = f"select count(id) as num,sum(driver_commission) as fee,sum(total_fee) as total_fee from ls_order where driver_id={row['id']} and status={ORDER_STATUS.COMPLETED} and commission_settle={COMMISSION_SETTLE_STATUS.NO_SETTLEMENT}"
        #     ret = self.db._query_sql_one(sql)
        #     row['order_count'] = ret['num']
        #     row['total_fee'] = ret['total_fee']
        #     row['order_commission'] = ret['fee']
        
        sql = f"""
            SELECT 
                d.id,
                d.truename,
                d.phone,
                d.car_no,
                d.created_at,
                COUNT(o.id) AS order_count,
                SUM(o.driver_commission) AS order_commission,
                SUM(o.total_fee) AS total_fee
            FROM ls_driver d
            LEFT JOIN ls_order o 
                ON d.id = o.driver_id 
                AND o.status = {ORDER_STATUS.COMPLETED}
                AND o.commission_settle = {COMMISSION_SETTLE_STATUS.NO_SETTLEMENT}
            WHERE d.id > 0 {where} and order_count > 0
            GROUP BY d.id, d.truename, d.phone, d.car_no, d.created_at
            ORDER BY d.created_at DESC
            LIMIT {pageindex}, {pagesize};
            """

        result = self.db._query_sql(sql)

        # 总未结算佣金
        sql = f"select count(id) as num,sum(driver_commission) as fee,sum(total_fee) as total_fee from ls_order where status={ORDER_STATUS.COMPLETED} and commission_settle={COMMISSION_SETTLE_STATUS.NO_SETTLEMENT}"
        ret = self.db._query_sql_one(sql)
        data = {
            'num': ret['num'],
            'commission': ret['fee'],
            'order': ret['total_fee']
        }

        return echo_json(0,"",result,data)

    def get_take_list(self):
        """ 提现列表
            Args:
                : 
            Return: 
                None
            @date:   2025/04/20 06:10:45
            @author: snz
        """
        page_limit = get_page_param_ex()
        name = get_param_by_str('driver_name')
        phone = get_param_by_str('phone')
        status = get_param_by_str('status')
        company = get_param_by_str('company')
        
        where = 'id > 0'
        data_range = get_param_by_str('date_range')
        if data_range != '':
            _data = data_range.split(' - ')
            btime = _data[0]
            etime = _data[1]
            if ":" not in btime:
                btime += " 00:00:00"
            if ":" not in etime:
                etime += " 23:59:59"
            where += f" and created_at between '{btime}' and '{etime}'"

        if name != '':
            where += f" and driver_name like '%{name}%'"
        if phone != '':
            where += f" and phone='{phone}'"
        if status != '':
            where += f" and status={status}"
        if company != '':
            where += f" and company_id={company}"
        
        sql = f"select count(*) as num from v_driver_take_cash where {where}"
        ret = self.db._query_sql_one(sql)
        num = 0
        if ret:
            num = ret['num']

        sql = f"select * from v_driver_take_cash where {where} {page_limit}"
        result = self.db._query_sql(sql)

        # 待审核提现
        sql = f"select count(id) as num from ls_driver_take_cash where status={DRIVER_CASH_VERIFY_STATUS.VERIFYING}"
        ret = self.db._query_sql_one(sql)
        verifying = ret['num']
        # 今日提现总金额
        sql = f"select sum(amount) as total_amount from ls_driver_take_cash where status={DRIVER_CASH_VERIFY_STATUS.PAID} and created_at between '{get_day_time_range()[0]}' and '{get_day_time_range()[1]}'"
        ret = self.db._query_sql_one(sql)
        total_amount = ret['total_amount']
       
        #本周提现总金额
        week_start, week_end = get_week_time_range()
        sql = f"select sum(amount) as total_amount from ls_driver_take_cash where status={DRIVER_CASH_VERIFY_STATUS.PAID} and created_at between '{week_start}' and '{week_end}'"
        ret = self.db._query_sql_one(sql)
        week_total_amount = ret['total_amount']

        # 本月提现总金额
        sql = f"select sum(amount) as total_amount from ls_driver_take_cash where status={DRIVER_CASH_VERIFY_STATUS.PAID} and created_at between '{get_month_time_range()[0]}' and '{get_month_time_range()[1]}'"
        ret = self.db._query_sql_one(sql)
        month_total_amount = ret['total_amount']

        _total ={
            'verifying': verifying,
            'total_amount': total_amount,
            'week_total_amount': week_total_amount,
            'month_total_amount': month_total_amount
        }

        # 公司列表
        sql = f"select id,name from ls_company"
        result_company = self.db._query_sql(sql)
        return echo_json(0,'success',result,{'total': num,'company': result_company,'total': _total})

    def take_cash_audit(self):
        """ 提现审核或拒绝
            Args:
                : 
            Return: 
                None
            @date:   2025/04/20 13:30:43
            @author: snz
        """
        remark = get_param_by_str('reason')
        _type = get_param_by_str('type')
        if _type not in ['approve','reject']:
            return echo_json(-1,'参数错误')
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(-1,'参数错误')
        
        sql = f"select id from ls_driver_take_cash where id={id}"
        row = self.db._query_sql_one(sql)
        if row is None:
            return echo_json(-1,'记录不存在')
        
        # 更新状态
        if _type == 'approve':
            self.db.update_data_by_id("ls_driver_take_cash",{'status': DRIVER_CASH_VERIFY_STATUS.VERIFY_SUCCESS,'remark': '等待系统打款'},id)
            ret = self.db._query_sql_one(sql)
            if ret is None:
                return echo_json(-1,'审核失败')
            # 这里触发支付打款，收到支付成功后再更新系统状态，并扣减司机帐户金额
            return echo_json(0,"审核成功,待系统自动打款")
        elif _type == 'reject':
            ret = self.db.update_data_by_id("ls_driver_take_cash",{'status': DRIVER_CASH_VERIFY_STATUS.VERIFY_REJECT,'remark': remark},id)
            if ret is None:
                return echo_json(-1,'审核失败')
            return echo_json(0,'操作成功')
        
    def get_invoice(self):
        """ 获取发票列表
            Args:
                : 
            Return: 
                None
            @date:   2025/04/20 13:30:43
            @author: snz
        """
        limit = get_page_param_ex()
        btime = get_param_by_str('btime')
        etime = get_param_by_str('etime')
        phone = get_param_by_str('phone')
        status = get_param_by_str('status')
        where = "where id > 0"
        if phone != '':
            where += f" and user_phone like '{phone}%'"
        if status != '':
            where += f" and status = '{status}'"
        if btime != '' and etime != '':
            where += f" and apply_time between '{btime}' and '{etime}'"
        sql = f"select * from ls_invoice {where} order by id desc {limit}"
        result = self.db._query_sql(sql)
        return echo_json(0,'操作成功',result)
    
    def invoice_approve(self):
        # 通过
        id = get_param_by_int('id')
        status = get_param_by_str('status')

        sql = f"update ls_invoice set status = '{status}' where id = {id}"
        ret = self.db._execute_sql(sql)
        if ret:
            return echo_json(0,'操作成功',ret)
        else:
            return echo_json(1,'操作失败')
        
    def invoice_reject(self):
        # 拒绝
        id = get_param_by_int('id')
        reason = get_param_by_str('reason')
        status = get_param_by_str('status')
        sql = f"update ls_invoice set status = '{status}',reject_reason = '{reason}' where id = {id}"
        ret = self.db._execute_sql(sql)
        if ret:
            return echo_json(0,'操作成功',ret)
        else:
            return echo_json(1,'操作失败')
        