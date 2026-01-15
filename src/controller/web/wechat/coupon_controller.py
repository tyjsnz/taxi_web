# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   coupon_controller.py
@date     :   2025/04/26 04:37:52
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   优惠券控制器
'''

from flask import request,current_app,session
import pytz,jwt,datetime
from settings import Config
from src.helper.helper import *
from src.controller.web.wechat.wechat_base_controller import WechatBaseController
from src.model.coupon.coupons_db import CouponsDb
from src.model.wechat.wechat_user_db import WechatUserDb

class CouponController(WechatBaseController):
    def __init__(self):
        super().__init__()
        self._db = CouponsDb()
        self._user = WechatUserDb()

    def get_coupon_my_list(self,uid):
        """我的优惠券列表，这里要在小程序中用，所以要根据路由传参
        """
        if uid <= 0:
            return echo_json(-1,'id 为空')

        status = -1        
        
        # 如果从小程序访问，则只返回可用券
        if self.is_wechat_mini_program():
            status = 0

        result = self._db.get_my_coupon_list(uid,status)
        return echo_json(0,'success',result)

    def get_coupon_list(self,uid):
        ''' 获取优惠券列表,卡券中心使用
            Args:
                uid: 指定时返回的记录中ls_take_me为1表示已经被我领券，0表示未领取
            Return: 
                None
            @date:   2025/03/18 15:21:58
            @author: snz
        '''
                
        if uid <= 0:
            return echo_json(-1,'id 为空')
        
        limit = get_page_param_ex(50)
        sql = f"select * from ls_coupons where status = 0 order by id desc {limit}"
        sql=f"""
        SELECT 
            c.*,
            IF(
                EXISTS (
                    SELECT 1 
                    FROM ls_coupons_list cl 
                    WHERE cl.coupon_id = c.id AND cl.uid = {uid}
                ), 
                1, 
                0
            ) AS is_take_me
        FROM 
            ls_coupons c
        ORDER BY 
            c.id;
    """
        result = self._db._query_sql(sql,use_cache=False)
        return echo_json(0,'success',result)
    
    def take_coupon(self,uid,coupon_id):
        ''' 领取优惠券
            Args:
                uid: 用户id
                coupon_id: 优惠券id
            Return: 
                None
            @date:   2025/03/18 15:21:58
            @author: snz
        '''
        if uid <= 0:
            return echo_json(-1,'id 为空')
        
        if coupon_id <= 0:
            return echo_json(-1,'优惠券id 为空')
        
        if self._db.take_coupon_is_exists(coupon_id,uid):
            return echo_json(-1,'已经领取过了')

        row = self._user.get_user_by_id(uid,"phone,nickname")
        if row is None:
            return echo_json(-1,'用户不存在')
        
        data = {
            "uid":uid,
            "phone":row['phone'],
            "truename":row['nickname'],
            "coupon_id":coupon_id,
            "created_at":get_current_time(),
            "status":0,
            'utype': 0,
        }
        if self._db.insert_data_by_dict("ls_coupons_list",data):
            return echo_json(0,'success')
        else:
            return echo_json(-1,'领取失败')