# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file    :   coupon_controller.py
@date    :   2025/04/13 23:41:05
@author  :   snz
@version :   1.0
@email   :   274043505@qq.com
@copyright:   Copyright (C) kmlskj All Rights Reserved.
@desc    :   优惠券

'''
from flask import session,request,redirect,url_for
from src.helper.helper import *
from src.controller.admin.base_controller import *
from src.common.const_defined import ORDER_STATUS,USER_STATUS,COUPON_TYPE,COUPON_STATUS
from src.model.base_db import PublicDbConnection
import json
from datetime import datetime
class CouponController(BaseController):
    def __init__(self):
        super().__init__()
        self.db = PublicDbConnection()
        
    def add(self):
        """ 优惠券添加
        Args:
            : 
        Return:
            None
        @date:   2025/04/18 15:15:22
        @author: snz
            
        """
        name = get_param_by_json('name')
        _type = get_param_by_json('type')
        
        if _type not in ['voucher','discount','referral']:
            return echo_json(False,message='优惠券类型错误')
       
        
        total = get_param_by_json('total')
        limit = get_param_by_json('limit')
        valid_type = get_param_by_json('validType')
        date_range = get_param_by_json('dateRange')
        valid_days = get_param_by_json('validDays')
        # 代金
        voucherAmount = get_param_by_json('voucherAmount')
        voucherCondition = get_param_by_json('voucherCondition')
        # 满减
        discountAmount = get_param_by_json('discountAmount')
        discountCondition = get_param_by_json('discountCondition')
        # 拉新
        referralAmount = get_param_by_json('referralAmount')
        referralTarget = get_param_by_json('referralTarget')
        referralCondition = get_param_by_json('referralCondition')
        # 适用于, 快车fast, 城际premium，为空则适用于所有服务类型
        service_type = get_param_by_json('serviceType')
        # 可用于城市列表
        city_list = get_param_by_json('selectedCities')
        # 说明
        description = get_param_by_json('description')
        # 16位编码
        code = generate_auth_token(10)
        
        amount = 0
        condition_amount = 0
        use_object = 0
        if _type == 'voucher':
            _type = COUPON_TYPE.CASH
            amount = voucherAmount
            condition_amount = voucherCondition
        elif _type == 'discount':
            _type = COUPON_TYPE.DISCOUNT
            amount = discountAmount
            condition_amount = discountCondition
        elif _type == 'referral':
            _type = COUPON_TYPE.REFERRAL
            amount = referralAmount
            condition_amount = referralCondition
            if referralTarget == 'both':
                use_object = 11
            elif referralTarget == 'inviter':
                use_object = 0
            elif referralTarget == 'invitee':
                use_object = 1
        
        valid_type = valid_type = 0 if valid_type == 'fixed' else 1
        service_type = 0 if service_type == 'fast' else 1
        if city_list:
            city_list = "#".join(city_list)
        else:
            city_list = ''
            
        # 解析日期时间字符串并转换为本地时区
        if valid_type == 0:
            start_date_str = date_range[0]
            end_date_str = date_range[1]
            # 定义日期时间格式
            format_string = '%Y-%m-%dT%H:%M:%S.%fZ'

            # 解析 ISO 8601 格式的日期时间字符串
            start_date = datetime.strptime(start_date_str, format_string)
            end_date = datetime.strptime(end_date_str, format_string)
            
            # 转换为本地时区（假设本地时区为 Asia/Shanghai）
            local_tz = pytz.timezone('Asia/Shanghai')
            start_date = start_date.astimezone(local_tz)
            end_date = end_date.astimezone(local_tz)

        else:
            start_date = None
            end_date = None
            
        data = {
            'name': name,
            'type': _type,
            'code': code,
            'total_num': total,
            'limit_num': limit,
            'surplus': total,
            'valid_type': valid_type,
            'start_date': start_date,
            'end_date': end_date,
            'valid_days': valid_days if valid_type != 0 else 0,
            'description': description,
            'status': 0,
            'amount': amount,
            'condition_amount': condition_amount,
            'use_object': use_object,
            'use_city': city_list,
            'use_range': service_type,
            'uid': self.get_uid(),
            'created_at': get_current_time(),
            'updated_at': get_current_time()
        }
        ret = self.db.insert_data_by_dict('ls_coupons',data)
        if ret:
            return echo_json(0, '添加成功')
        else:
            return echo_json(-1, '添加失败')
        
    def get_list(self):
        # 优惠券列表
        pageindex,pagesize = get_page_param()
        pageindex = pageindex - 1 if pageindex > 0 else 0
        pageindex = pageindex * pagesize
        _type = get_param_by_int('couponType')
        name = get_param_by_str('name')
        amount = get_param_by_str('amount')
        amount_end = get_param_by_str('amount_end')
        btime = get_param_by_str('btime')
        etime = get_param_by_str('etime')
        
        where = 'id > 0'
        if _type > 0:
            where += f' and type = {_type}'
        if name != '':
            where += f' and name like "%{name}%"'
        if amount != '' and amount_end != '':
            where += f' and amount >= {amount} and amount <= {amount_end}'
        if btime != '' and etime != '':
            where += f' and create_time >= "{btime}" and create_time <= "{etime}"'
            
        sql = f"select count(id) as num from ls_coupons where {where}"
        ret = self.db._query_sql_one(sql,use_cache=False)
        if ret is not None:
            num = ret['num']
            
        sql = f"select * from ls_coupons where {where} order by id desc limit {pageindex},{pagesize}"
        result = self.db._query_sql(sql,use_cache=False)
        return echo_json(0,'success',result,{'num':num})
    
    def get_take_list(self):
        """ 领用记录
        Args:
            : 
        Return:
            None
        @date:   2025/04/18 18:24:17
        @author: snz
            
        """
        utype = get_param_by_int('utype')
        flag = get_param_by_int('flag')
        # 优惠券管理中进入
        if flag == -1:
            id = get_param_by_int('id')
            if id <= 0:
                return echo_json(1,'参数错误')
        
            where = f"id={id}"        
        elif flag == 0:
            uid = get_param_by_int('uid')
            if uid <= 0:
                return echo_json(1,'参数错误')
            
            where = f"uid={uid}"
            if utype != '':
                if utype == 0:
                    #乘客
                    where += f" and utype=0"
                elif utype == 1:
                    #司机
                    where += f" and utype=1"
                else:
                    return echo_json(1,'参数错误')
        
        limit = get_page_param_ex()
        sql = f"select count(*) as num from v_coupons_take_list where {where}"
        ret = self.db._query_sql_one(sql)
        num = ret['num'] if ret else 0
            
        sql = f"select * from v_coupons_take_list where {where} {limit}"
        result = self.db._query_sql(sql)        
        return echo_json(0,'success',result,num)
        
        
    
    def delete_coupons(self):
        """ 删除优惠券，注意，如果有用户领取，则不能删除，必须得使用完才可删除
        Args:
            : 
        Return:
            None
        @date:   2025/04/18 19:19:58
        @author: snz
            
        """        
        id = get_param_by_int('id')
        if id:
            sql = f"select count(*) as num from ls_coupons_list where coupon_id={id} and status={COUPON_STATUS.USED}"
            ret = self.db._query_sql_one(sql)
            if ret['num'] > 0:
                return echo_json(1,'优惠券有使用记录，不能删除')
            
            sql = f"delete from ls_coupons where id={id}"
            self.db._execute_sql(sql)
            
            sql = f"delete from ls_coupons_list where coupon_id={id}"
            self.db._execute_sql(sql)
            return echo_json(0,'删除成功')
        else:
            return echo_json(1,'参数错误')
                
    def total_coupons(self):
        """ 活动统计
        Args:
            : 
        Return:
            None
        @date:   2025/04/18 19:23:22
        @author: snz
            
        """
        # 统计各类型优惠券数量
        total_sql = """SELECT 
            COUNT(*) as total, 
            SUM(CASE WHEN type = 1 THEN 1 ELSE 0 END) as voucher, -- 代金券
            SUM(CASE WHEN type = 2 THEN 1 ELSE 0 END) as discount, -- 满减券
            SUM(CASE WHEN type = 3 THEN 1 ELSE 0 END) as referral, -- 拉新券
            SUM(CASE WHEN type = 4 THEN 1 ELSE 0 END) as new_user -- 新用户立减
        FROM ls_coupons"""
        
        # 统计已使用和未使用的优惠券数量
        usage_sql = """
        SELECT 
            COUNT(*) as total, 
            SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as used, -- 已使用
            SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) as unused, -- 未使用
            SUM(CASE WHEN status = -1 THEN 1 ELSE 0 END) as expired -- 已过期
        FROM ls_coupons_list
        """
        
        # 统计总金额和已使用金额
        amount_sql = """
        SELECT 
            SUM(c.amount) as total_amount, 
            SUM(CASE WHEN cl.status = 1 THEN c.amount ELSE 0 END) as used_amount
        FROM ls_coupons c
        LEFT JOIN ls_coupons_list cl ON c.id = cl.coupon_id
        """
        
        # 按类型统计使用情况
        type_usage_sql = """
        SELECT 
            c.type, 
            COUNT(*) as issued, 
            SUM(CASE WHEN cl.status = 1 THEN 1 ELSE 0 END) as used
        FROM ls_coupons c
        LEFT JOIN ls_coupons_list cl ON c.id = cl.coupon_id
        GROUP BY c.type
        """
        
        # 执行查询
        total_stats = self.db._query_sql_one(total_sql)
        usage_stats = self.db._query_sql_one(usage_sql)
        amount_stats = self.db._query_sql_one(amount_sql)
        type_usage = self.db._query_sql(type_usage_sql)
        
        # 构建返回数据
        result = {
            "total": total_stats,
            "usage": usage_stats,
            "amount": amount_stats,
            "type_usage": type_usage
        }
        
        return echo_json(0, "success", result)