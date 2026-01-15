# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   wechat_controller.py
@date     :   2025/03/09 00:37:59
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   小程序端控制器
'''
from flask import request
import pytz,jwt,datetime
from src.helper.helper import *
from src.controller.web.wechat.wechat_base_controller import WechatBaseController
from src.controller.web.wechat.libs.order_libs import OrderLibs
from src.common.const_defined import ORDER_STATUS,ORDER_TYPE
import json
from src.common.websocket_manager import send_message_to_target_client

class OrderController(WechatBaseController):
    def __init__(self):
        super().__init__()
        self._db = self.wechat_db
        self.order = OrderLibs()        
        
    def get_order_by_id(self,id):
        # 获取订单信息
        return self.order._db.get_order_by_id(id)
    
    def get_order_sn_by_id(self,id):
        # 获取订单信息
        row = self.order._db.get_order_by_id(id,'sn')
        if row is None:
            return ''
        return row['sn']
    
    def update_payment_order_by_id(self,order_id,amount,pay_amount,coupon_id,coupon_amount,coupon_name,add_price):
        """ 小程序提交订单，更新订单信息
        Args:
            order_id: 订单ID
            amount: 实际订单金额
            pay_amount: 实际支付金额
            coupon_id: 优惠券ID
            coupon_amount: 优惠券金额
            coupon_name: 优惠券名称
            add_price: 用户加价
        Return:
            None
        @date:   2025/04/26 19:44:59
        @author: snz
            
        """
        amount = float_ex(amount)
        pay_amount = float_ex(pay_amount)
        coupon_amount = float_ex(coupon_amount)
        add_price = float_ex(add_price)
        
        if amount == 0 or pay_amount == 0:
            return echo_json(-1, "订单金额不能为0")
        if amount < 0 or pay_amount < 0:
            return echo_json(-1, "订单金额不能小于0")
        if coupon_amount < 0:
            return echo_json(-1, "优惠券金额不能小于0")
        if add_price < 0:
            return echo_json(-1, "用户加价不能小于0")
            
        # 更新订单信息，实际订单金额
        ret = self.order._db.update_order(order_id,{'total_fee': amount,'pay_amount': pay_amount,'discount_amount': coupon_amount,'add_price': add_price})
        
        # 更新明细表
        self.order.order_fee_detail.update_order_fee_detail_by_dict(order_id,{
            "coupon_id": coupon_id,
            'coupon_name': coupon_name,
            'discount': coupon_amount,
            'total_fee': amount,
            'user_add_fee': add_price,
        })

    def update_order(self):
        ''' 更新订单，用户再次叫车
            Args:
                : 
            Return: 
                None
            @date:   2025/03/18 15:21:58
            @author: snz
        '''
                
        openid = get_openid()
        token = get_user_token()
        if not token: return echo_json(-1, "token不能为空")

        order_id = get_param_by_json("order_id")
        if not order_id: return echo_json(-1, "订单ID不能为空")

        add_price = get_param_by_json("add_price")

        return self.order.update_order(order_id,add_price,openid)

    def create_order(self):
        ''' 创建订单
            Args:
                : 
            Return: 
                None
            @date:   2025/03/18 15:21:58
            @author: snz
        '''        
        real_ip = get_real_ip()

        uid = 0        
        uid = self.decode_wechat_token()
        if uid is None:
            return echo_json(-1, "token过期或无效")
        
        start = get_param_by_json("start")
        end = get_param_by_json("end")

        if not start or not end: return echo_json(-1, "起点或终点不能为空")

        # 所选择的加盟商，即所选车辆IDS,如：1,2,3,4,5
        company_ids = get_param_by_json("company_ids")

        customer_phone = get_param_by_json("phone")
        if not customer_phone: return echo_json(-1, "手机号不能为空")

        start_city = "city" in start and start['city'] or ""
        end_city = "city" in end and end['city'] or ""

        total_fee = get_param_by_json("total_fee")
        need_after_pay = int_ex(get_param_by_json("need_after_pay"))
        data = {
            "company_ids": company_ids,
            "start_lat": round(float_ex(start['latitude']),6),
            "start_lng": round(float_ex(start['longitude']),6),
            "start_city": start_city,
            "start_name": start['name'],
            "start_address": start["address"],
            "end_lat": round(float_ex(end['latitude']),6),
            "end_lng": round(float_ex(end['longitude']),6),
            "end_city": end_city,
            "end_name": end['name'],
            "end_address": end["address"],
            "cost": self.order.convert_float(get_param_by_json("cost")),
            "duration": get_param_by_json("duration"), # 时长(秒)
            "distance": get_param_by_json("distance"), # 距离(米)
            "customer_phone": customer_phone,
            "total_fee": total_fee,
            "tolls": self.order.convert_float(get_param_by_json("tolls")), # 行程路段收费情况（收费站）
            "need_after_pay": need_after_pay
        }
                
        return self.order.create_order(uid,data)
    
    def cancel_order(self):
        ''' 取消订单
            Args:
                : 
            Return: 
                None
            @date:   2025/03/18 15:21:58
            @author: snz
        '''
        token = get_user_token()
        if not token: return echo_json(-1, "token不能为空")
        order_id = get_param_by_json("order_id")
        if not order_id: return echo_json(-1, "订单ID不能为空")
                   
        return self.order.cancel_order_by_customer(order_id)    
        
    def price_calculate(self):
        ''' 价格计算
            Args:
                : 
            Return: 
                None
            @date:   2025/03/18 15:21:58
            @author: snz
        '''
        
        uid = 0
        uid = self.decode_wechat_token()
        if uid is None:
            return echo_json(-1, "token过期或无效")
        
        distance = get_param_by_json("distance")
        if distance is None: return echo_json(-1, "距离不能为空")
        duration = get_param_by_json("duration")
        cost = get_param_by_json("cost")
        tolls = get_param_by_json("tolls")
        
        return self.order.price_calculate(uid,distance,duration,cost,tolls)
    
    def verify_order_pay_state(self,order_sn,payer_body):
        ''' 验证订单支付状态,支付回调函数中使用
            Args:
                order_sn: 订单号对应SN
                payer_body: 支付信息体
            Return: 
                -1: order_sn is None
                -2: order no exists
                0: success
            @date:   2025/03/18 15:21:58
            @author: snz
        '''
        if order_sn is None: return -1
        sql = f"select id,status,driver_token,driver_id,order_type from ls_order where sn = '{order_sn}' limit 1"
        ret = self.order._db._query_sql_one(sql)
        if ret is None: return -2
        pay_amount = payer_body['payAmount']
        real_pay_amount = payer_body['realPayAmount']
        data = {
            'pay_amount': pay_amount,
            'real_pay_amount': real_pay_amount,
            'status': ORDER_STATUS.COMPLETED,
            'updated_at': payer_body['paySuccessDate']
        }
        self.order._db.update_order(ret['id'],data)
        
        data_json = json.dumps(payer_body)
        # 插入支付结果保存表
        self.order._db.insert_data_by_dict('ls_order_payresult',{'order_id': ret['id'], 'pay_body': data_json})

        # 先付后乘支付成功，但是这时还没有找到司机，所以无法通知司机
        # 这里需要判断是否是先乘后付的订单，如果是，则需要通知司机
        if ret['order_type'] == ORDER_TYPE.USE_AFTER_PAY:
            # 通知司机已经支付成功
            sql = f"select token from ls_driver where id = {ret['driver_id']} limit 1"
            row = self.order._db._query_sql_one(sql)
            if row:
                # 计算订单佣金
                self.order.calculate_driver_commission(ret['id'])
                send_message_to_target_client(row['token'], {'flag': 'pay_success', 'msg': '乘客订单支付成功', 'order_id': ret['id'], 'order_sn': order_sn})
        
        return 0
    def get_my_trip(self,uid):
        ''' 获取我的行程
            Args:
                : 
            Return: 
                None
            @date:   2025/03/18 15:21:58
            @author: snz
        '''
        if uid <= 0: return echo_json(-1, "token过期或无效")
        
        sql = f"select id,order_time,total_fee,start_location,end_location, status,cost,pay_amount,real_pay_amount,discount_amount,add_price from ls_order where customer_id = {uid} order by id desc"
        result = self.order._db._query_sql(sql)
        return echo_json(0, "success", result)
    
    def get_order_detail(self):
        ''' 获取订单详情
            Args:
                : 
            Return: 
                None
            @date:   2025/03/18 15:21:58
            @author: snz
        '''
        order_id = get_param_by_int('order_id')
        if order_id <= 0: 
            order_id = int_ex(get_param_by_json('order_id'))
            if order_id <= 0: 
                return echo_json(-1, "订单ID不能为空")
            
        row = self.order._db.get_order_by_id(order_id)
        if row:
            driver_id = row['driver_id']
            ret = self._db._query_sql_one(f"select truename,phone,score,car_no,car_brand,car_color,car_type from ls_driver where id = {driver_id}")
            row['driver'] = ret
        return echo_json(0, "success", row)

    def trip_comment(self):
        ''' 评价行程
            Args:
                : 
            Return: 
                None
            @date:   2025/03/18 15:21:58
            @author: snz
        '''
        order_id = get_param_by_int('order_id')
        if order_id <= 0: 
            order_id = int_ex(get_param_by_json('order_id'))
            if order_id <= 0: 
                return echo_json(-1, "订单ID不能为空")
            
        rating = get_param_by_int('rating')
        if rating is None: return echo_json(-1, "评价星级不能为空")

        comment = get_param_by_str('comment')
        if comment is None: return echo_json(-1, "评价内容不能为空")
                
        ret = self.order._db._query_sql_one(f"select * from ls_order where id = {order_id}")
        if ret is None: return echo_json(-1, "订单不存在")

        # 系统评价配置
        default_review_score = 0
        bad_review_score = 0 # 差评扣多少分
        row = self.order._db._query_sql_one(f"select * from ls_sys_config limit 1")
        if row:
            if row['driver_config']:
                row['driver_config'] = json.loads(row['driver_config'])
                # 差评扣多少分
                bad_review_score = row['driver_config']['bad_review_score']
                # 默认评价给多少分
                default_review_score = row['driver_config']['default_review_score']

        driver_id = ret['driver_id']
        openid = ret['openid']
        
        created_at = get_current_time()
        items = ''
        if rating == 5:
            items = '非常好'
        elif rating == 4:
            items = '好'
        elif rating == 3:
            items = '一般'
        elif rating == 2:
            # 差评扣分
            rating = float_ex(0 - bad_review_score)
            items = '差'
        elif rating == 1:
            rating = float_ex(0 - bad_review_score)
            items = '非常差'
        else:
            items = '好'

        ret = self.order._db.insert_data_by_dict('ls_order_rating',{'order_id': order_id, 'driver_id': driver_id, 'score_item': items, 'score': rating, 'remark': comment, 'openid': openid, 'created_at': created_at})       

        # 更新司机评价分数
        _driver_score = 0
        sql = f"select score from ls_driver where id = {driver_id} limit 1"
        row = self.order._db._query_sql_one(sql)
        if row:
            # 更新评价记录
            data = {
                "order_id": order_id,
                "driver_id": driver_id,
                "score": rating,
                "remark": f"[{items}]，评价内容：{comment}",
                "created_at": get_current_time()
            }
            self.order._db.insert_data_by_dict("ls_driver_score_log",data)
            # 更新司机评价分数
            self.order._db.update_data_by_id("ls_driver",{"score": row['score'] + rating},driver_id)

            _driver_score = row['score'] + rating
            
        return echo_json(0, "success", {'ret': ret,'score': _driver_score})