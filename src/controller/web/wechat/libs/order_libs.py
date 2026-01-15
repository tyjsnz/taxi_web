# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   order.py
@date     :   2025/03/18 15:19:32
@author   :   snz
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   订单处理类
'''
from src.helper.helper import *
from src.model.order.order_db import OrderDb
from src.model.common.taxi_fee_settings_db import TaxiFeeSettingsDb
from src.model.driving.driver_location_db import DriverLocationDb
from src.model.driving.driver_db import DriverDb
from src.model.driving.driver_order_accept_db import DriverOrderAcceptDb
from src.model.order.order_fee_detail_db import OrderFeeDetailDb
from src.model.driving.driver_account_db import DriverAccountDb
from src.controller.web.wechat.libs.price_calculate_lib import PriceCalculateLibs
from src.common.const_defined import *
from src.common.websocket_manager import send_message_to_target_client
from loguru import logger
from datetime import datetime
from src.controller.web.wechat.libs.driver_find_libs import DriverFinder
from flask import current_app
import json

class OrderLibs:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        self._db = OrderDb()
        self._fee_setting = TaxiFeeSettingsDb()
        self.driver_location = DriverLocationDb()
        self.driver = DriverDb()
        self.driver_accept = DriverOrderAcceptDb()
        self.order_fee_detail = OrderFeeDetailDb()
        self.driver_account = DriverAccountDb()
        self.price_lib = PriceCalculateLibs()

        #等待时长秒
        self.find_waiting_time = 60 
        # 司机查找范围5公里
        self.driver_find_region = 15000
        
    def convert_float(self,v):
        try:
            num = float(v)
        except ValueError:
            num = 0
        finally:
            return num
    def order_increase_cost(self, order_id, cost):
        """ 订单加价找车
            Args:
                order_id: 订单ID
                cost: 加价金额
            Return:
                None
            @date:   2025/03/18 15:34:13
            @author: snz
        """
        row = self._db.get_order_by_id(order_id,'status,order_type')
        if row is None:
            return echo_json(-1, "order not found")
        
        # 只有在待接单状态可加价
        if row['status'] == ORDER_STATUS.PENDING:
            detail = OrderFeeDetailDb()
            detail.update_order_add_fee(order_id, cost)
            return echo_json(0, "订单加价成功")
        else:
            return echo_json(-1, "订单状态不允许加价")

    def start_driver_finder(self,order_id, openid, start_lat, start_lng, order_time,reject_driver_ids='',company_ids='',start_location='',end_location='',end_lat='', end_lng=''):
        """ 启动司机查找线程
            Args:
        Args:
            order_id: 订单ID
            openid: 乘客openid
            start_lat: 起点纬度
            start_lng: 起点经度
            order_time: 下单时间
            reject_driver_ids: 拒绝司机ID列表
            company_ids: 所选打车的车辆所属于id列表, 1,2,3,4
            start_location: 起点地址
            end_location: 终点地址
            end_lat: 终点纬度
            end_lng: 终点经度
        Return:
            None
        @date:   2025/04/14 11:21:08
        @author: snz
            
        """
        finder = DriverFinder(order_id, openid, start_lat, start_lng, order_time,reject_driver_ids,company_ids=company_ids,start_location=start_location,end_location=end_location,end_lat=end_lat,end_lng=end_lng)
        finder.start()
        
    def create_order(self, customer_id, orderInfo):
        ''' 创建订单，找司机
            Args:
                customer_id: 用户id
                orderInfo: 订单信息
            Return:
                None
            @date:   2025/03/18 15:34:13
            @author: snz
        '''
        # 订单编号，与支付时编号一致，支付成功要验证
        order_sn = "ORDER" + generate_auth_token(10)
        data = {
            'sn': order_sn,
            'customer_id': customer_id,
            'customer_phone': orderInfo['customer_phone'],
            'start_location': orderInfo['start_city'] + orderInfo['start_name'],
            'start_latlng': f"{orderInfo['start_lat']},{orderInfo['start_lng']}",
            'end_location': orderInfo['end_city'] + orderInfo['end_name'],
            'end_latlng': f"{orderInfo['end_lat']},{orderInfo['end_lng']}",
            'cost': orderInfo['cost'],
            'duration': orderInfo['duration'],
            'distance': orderInfo['distance'],
            'tolls': orderInfo['tolls'],
            'order_time': get_current_time(),
            'status': ORDER_STATUS.PENDING,
            'created_at': get_current_time(),
            'company_ids':  orderInfo['company_ids'],
        }

        total_fee = self.convert_float(orderInfo['total_fee'])
                
        # 乘客当前是使用先付后乘还是先用后付的方式来进行打车
        data['order_type'] = orderInfo['need_after_pay']# ORDER_TYPE.USE_AFTER_PAY # 默认为先用后付

        # 打车点
        start_latitude = orderInfo['start_lat']
        start_longitude = orderInfo['start_lng']
        end_latitude = orderInfo['end_lat']
        end_longitude = orderInfo['end_lng']
        
        # 预计用时分钟
        duration_minutes = data['duration']
        if duration_minutes == None or duration_minutes == '':
            duration_minutes = 0
            
        if duration_minutes > 0:
            duration_minutes = int(duration_minutes) / 60

        ## 这里根据用户选择的公司的预估价作为填充，后面司机接单后才设置为当家公司的预估价，因为这里是有多家公司并存的订单，所以要以最终选择为准
        
        # 计算的费用即订单费用
        data['total_fee'] = 0
        # 实际费用先填充，支付成功后会真实填充
        data['pay_amount'] = 0
        # 设置一个预估价范围，供司机接单时参考
        data['ev_price'] = str(data['cost']) + "~" + str(total_fee)

        # 乘客openid
        openid = get_openid()
        data['customer_token'] = get_user_token()
        data['openid'] = openid

        # 生成订单
        order_id = self._db.insert_order(data)
        if order_id > 0:
            # 为订单添加价格明细, 这里在司机接单后再以所属于公司的价格来填充明细
            # fee_detail['order_id'] = order_id
            # self.order_fee_detail.insert_order_fee_detail(fee_detail)
            
            # 所以只有先乘后付时，才找司机，如果是先付后乘时，这里只是创建订单并未实际支付
            # 待支付成功后小程序端会调用更新订单方式来找司机
            if int_ex(orderInfo['need_after_pay']) == ORDER_TYPE.USE_AFTER_PAY:                
                logger.info(f"先用后乘模式，创建订单成功，开始找司机")
                self.start_driver_finder(order_id,openid, start_latitude, start_longitude,data['order_time'],reject_driver_ids=[],company_ids = orderInfo['company_ids'],start_location=data['start_location'],end_location=data['end_location'],end_lat = end_latitude, end_lng = end_longitude)
            else:
                logger.info(f"先付后乘模式，创建订单成功，等待支付")
                
            return echo_json(0, "订单创建成功",{'order_id': order_id, 'total_fee': total_fee,'order_sn': order_sn})
        else:
            return echo_json(-1, "订单创建失败")
                    
    def update_order(self, order_id, add_price,openid):
        ''' 重新提交订单，找司机
            Args:
                order_id: 订单ID
                add_price: 加价金额
                openid: 乘客openid
            Return:
                None
            @date:   2025/03/18 15:34:13
            @author: snz
        '''
        row = self._db.get_order_by_id(order_id)
        if row is None:
            return echo_json(-1, "order not found")

        # 第几次抢单超时        
        find_num = 1
        if row['find_num']:
            find_num = int(row['find_num']) + 1
        # 更新订单为“待接单”
        self._db.update_order(order_id,{'status': ORDER_STATUS.PENDING, 'order_time': get_current_time(),'add_price': add_price,'openid': openid,'find_num': find_num})
        
        start_latlng = row['start_latlng']
        start_latitude = start_latlng.split(',')[0]
        start_longitude = start_latlng.split(',')[1]
        
        end_latlng = row['end_latlng']
        end_lat = end_latlng.split(',')[0]
        end_lng = end_latlng.split(',')[1]

        # 当前订单，排除拒绝过的司机
        result = self.driver_accept.get_list_by_reject_order_id(order_id)
        ids = []
        for item in result:
            ids.append(item['driver_id'])
            logger.info(f"当前订单，排除拒绝过的司机，司机ID：{item['driver_id']}")
                
        # 再次查找司机,在开始查找前会删除此订单之前的抢单记录
        self.start_driver_finder(order_id,openid, start_latitude, start_longitude,get_current_time(),reject_driver_ids=ids,company_ids=row['company_ids'],start_location=row['start_location'],end_location=row['end_location'],end_lat=end_lat,end_lng=end_lng)

        # 发送消息给乘客
        return echo_json(0, "等待司机接单",{'order_id':order_id})

    def confirm_accept_order(self,order_id,driver_id,accept_order_id,driver_lat,driver_lng,company_id):
        """ 司机确认接单
            Args:
                order_id: 订单ID
                driver_id: 司机ID
                driver_lat: 司机纬度
                driver_lng: 司机经度
                accept_order_id: 接单记录ID
                company_id: 所属公司ID
            Return: 
                None
            @date:   2025/03/29 22:50:08
            @author: snz
        """
        
        order_id = int(order_id)
        driver_id = int(driver_id)
        accept_order_id = int(accept_order_id)
    
        order = self._db.get_order_by_id(order_id,"*")
        if not order:
            return echo_json(-1, '订单已取消或不存在')
        
        # 无司机接单 或 待接单状态才可确认
        if order['status'] == ORDER_STATUS.CANCELED:
            return echo_json(-1, '订单已取消')
        
        if order['status'] != ORDER_STATUS.NO_DRIVER and order['status'] != ORDER_STATUS.PENDING:
            return echo_json(-1, '来晚了订单已被手快的师傅抢走了')
        
        # 司机接单成功，更新订单状态和司机信息
        row = self.driver_accept.get_one(accept_order_id)
        if row is None:
            return echo_json(-1, '接单记录不存在')
        
        # 乘客下单时间
        send_time = row['send_time']
        # 司机接单时间相距多少秒
        diff_sec = calculate_time_difference(send_time)
        # 更新状态
        self.driver_accept.update_order_status_by_dict(accept_order_id, {
            'status': DRIVER_ACCEPT_STATUS.ACCEPT,
            'accept_time': get_current_time(),
            'second': diff_sec,
            'lat': driver_lat,
            'lng': driver_lng
            })
        
        # 司机信息，推送信息至客户......................................
        driver = self.driver.get_user_info_by_id(driver_id)
        score = driver['score']
        
        # 更新司机所在公司的价格预估方案，因为会同时选多家公司，所以最终以接单司机所在公司计算
        # 预计用时分钟
        duration_minutes = order['duration']
        if duration_minutes == None or duration_minutes == '':
            duration_minutes = 0
            
        if duration_minutes > 0:
            duration_minutes = int(duration_minutes) / 60
            
        total_fee, fee_detail = self.price_lib.calculate_order_fee_by_companyid(driver['company_id'],get_current_time(),order['distance'],duration_minutes,0,order['tolls'],0,is_wechat_calculate=False)
        if total_fee == None or fee_detail == None:
            return echo_json(-1, '所属运营商未设置行程价格!')
        
        fee_detail['order_id'] = order_id
        
        
        driver_config = get_current_driver_config()
        if driver_config and "order_dispatch_bonus" in driver_config:
            _bonus = float_ex(driver_config['order_dispatch_bonus'])
            score = score + _bonus
        
        # 更新司机当前工作状态为“正在接送乘客”,如有奖励则增加
        self.driver.update_driver_info(driver_id, {'accept_order_status': DRIVER_ACCEPT_ORDER_STATUS.YES_ACCEPT,'score': score})
        
        # 打出司机所在公司的客服电话
        sql = f"select service_phone from ls_company where id = {driver['company_id']}"
        service_phone = self._db._query_sql_one(sql)
        if service_phone:
            service_phone = service_phone['service_phone']
        else:
            service_phone = ''
            
        
        # 以防万一
        try:
            self.order_fee_detail.insert_order_fee_detail(fee_detail)
        except Exception as e:
            print(e)
        
        # 更新订单状态为“已接单”，并更新接单司机
        self._db.update_order(order_id,{
            'status': ORDER_STATUS.ACCEPTED,
            'car_no': driver['car_no'],
            'driver_id': driver_id,
            'driver_phone': driver['phone'],
            'driver_name': driver['truename'],
            'waiting_time': diff_sec,
            'accept_time': get_current_time(),
            'driver_lat': driver_lat,
            'driver_lng': driver_lng,
            'company_id': driver['company_id'],
            'total_fee': total_fee, # 计算的费用即订单费用
            "pay_amount": total_fee # 实际费用先填充，支付成功后会真实填充
        })

        # 与乘客的接单数据由司机端与乘客端自行websocket通信完成
        # 这里由服务下发至乘客端
        web_msg = {
            'flag': 'trip_ready_start',
            'order_id': order_id,
            'driver_id': driver_id,
            'truename': driver['truename'],
            'car_no': driver['car_no'],
            'phone': driver['phone'],
            'car_type': driver['car_type'],
            'car_color': driver['car_color'],
            'car_brand': driver['car_brand'],
            'level': driver['level'],
            'score': driver['score'],
            'order_total': driver['order_total'],
            'driving_age': driver['driving_age'],
            'msg': '正在飞速前来接驾',
            'target_token': order['openid'],
            'driver_lat': driver_lat,
            'driver_lng': driver_lng,
            'service_phone': service_phone,
        }
        send_message_to_target_client(order['openid'],web_msg)
        
        return echo_json(0, 'Order confirmed',data={"order_id": order_id,'total_fee':total_fee},code=200)
    
    def reject_accept_order(self,accept_id):
        """ 拒绝接单，由系统派单时，司机才可能拒绝，这时要重新找司机
            Args:
                accept_id: 接单记录ID
                driver_id: 司机ID
            Return: 
                None
            @date:   2025/03/29 22:50:08
            @author: snz
        """
        row = self.driver_accept.get_one(accept_id)
        if row is None: return echo_json(-1, '接单记录不存在')
        # 订单ID
        order_id = row['order_id']
        # 司机
        driver_id = row['driver_id']
        
        order_row = self._db.get_order_by_id(order_id,"order_type,find_num,openid")
        if order_row is None:
            return echo_json(-1,"订单不存在")

        # 将此次司机的拒绝记录进行存档，以便于此订单排除此司机，及统计之用
        self.driver_accept.add_driver_reject(order_id,driver_id)
        
        # 更新接单池中状态为司机拒绝
        self.driver_accept.update_order_status_by_dict(id, {'status': DRIVER_ACCEPT_STATUS.REJECT_ACCEPT})
        
        # 再找下一位司机,也就是模拟用户再次叫车
        return self.update_order(order_id,0,order_row['openid'])
    
    def cancel_order_by_customer(self,order_id):
        """ 乘客取消订单
            Args:
                order_id: 订单ID
            Return: 
                None
            @date:   2025/03/29 22:50:08
            @author: snz
        """
        # 给司机发送取消订单消息,这里是在没有接单情况下，如果有在行程中的订单时要重新给司机发数据
        # result = self.driver_accept.get_list_by_driver_id(order_id,"driver_id")
        # for row in result:
        #     driver_id = row['driver_id']
        #     info = self.driver.get_user_info_by_id(driver_id,"token")
        #     if info:
        #         send_message_to_target_client(info['token'], {'flag': 'cancel_order', 'target_token': info['token'], 'order_id': order_id, 'msg': '乘客取消订单'})
                        
        # 取消订单，删除先前抢单池中的订单记录
        self.driver_accept.delete_order_by_order_id(order_id)

        # 更新订单状态为“已取消”
        self._db.update_order_status(order_id, {'status': ORDER_STATUS.CANCELED})
        
        # 查看是否有司机接单了，如是，则更新司机状态为“空闲”
        row = self._db.get_order_by_id(order_id,"driver_id,status")
        if row and row['driver_id'] > 0:
            # 取司机token并给司机发信息
            driver_info = self.driver.get_user_info_by_id(row['driver_id'])
            send_message_to_target_client(driver_info['token'], {'flag': 'cancel_order', 'target_token': driver_info['token'], 'order_id': order_id, 'msg': '乘客取消订单'})
            
            self.driver.update_driver_info(row['driver_id'], {'accept_order_status': DRIVER_ACCEPT_ORDER_STATUS.NO_ACCEPT})

        return echo_json(0,"订单取消成功")
    
    def price_calculate(self,customer_id,distance,duration,cost,tolls):
        ''' 价格计算(预估)
            Args:
                customer_id: 用户ID
                distance: 距离
                duration: 时长
                cost: 小程序端高德地图预估费用
                tolls: Toll 费用
            Return:
                None
            @date:   2025/03/18 15:34:13
            @author: snz
        '''
        # 预计用时分钟
        duration_minutes = duration
        if duration_minutes == None or duration_minutes == '':
            duration_minutes = 0
            
        if duration_minutes > 0:
            duration_minutes = int(duration_minutes) / 60
            
        # 取系统配置参数
        customer_config = get_current_customer_config()
            
        params = {
            "pay_flag": 0,
            "pay_limit": 0,
            "timeout": 0,
            "add_price_limit": 0,
            "auto_debit": 0
        }
        
        if customer_config:            
            params = customer_config
                     
        # 计算订单费用,这里是小程序计算
        fee_detail_list = self.price_lib.calculate_order_fee(get_current_time(),distance,duration_minutes,0,tolls,0)
        # 预估价格
        params["total_fee"] = 0
        
        ###################### 相当重要 #######################
        
        # 检查是否开启了先付后乘的功能，如开启了，则计算出的费用是否在先传后乘的限制范围内，如未超出范围则订单继续以先乘后付来进行。
        # 如果超出范围，则订单以先付后乘的方式进行，并提示司机先付后乘
        pay_flag = int_ex(params["pay_flag"])
        pay_limit = float_ex(params["pay_limit"])

        params['need_after_pay'] = ORDER_TYPE.USE_AFTER_PAY
        
        # 先算一个平均价,给先付后乘使用
        avg_price = 0
        is_have_pay_after_pay = False

        # 如果开了先付后乘功能。
        if pay_flag == ORDER_TYPE.PAY_AFTER_USE:
            for item in fee_detail_list:
                avg_price += item['total_fee']

                # 需要先付后乘
                if item['total_fee'] > pay_limit:
                    item['need_after_pay'] = ORDER_TYPE.PAY_AFTER_USE
                    is_have_pay_after_pay = True
                else:
                    item['need_after_pay'] = ORDER_TYPE.USE_AFTER_PAY # 默认先用后付
                
        # 只要有一家的价格超过，就使用先付后乘，因为多家时这个先付后用只能以一个为标准
        if is_have_pay_after_pay:
            params['need_after_pay'] = ORDER_TYPE.PAY_AFTER_USE

        if len(fee_detail_list) > 0:
            avg_price = round(avg_price / len(fee_detail_list),2)
        params['avg_price'] = avg_price
        # 小程序端高德地图预估费用
        params['cost'] = cost

        ######################## 相当重要 #######################
        
        return echo_json(0, params,fee_detail_list)
        
    def calculate_driver_commission(self,order_id):
        """ 计算司机佣金
            Args:
                order_id: 订单ID: 
            Return: 
                订单对应的司机佣金（实际支付金额*司机佣金比例
            @date:   2025/04/30 13:46:24
            @author: snz
        """
        row = self._db.get_order_by_id(order_id)
        if row is None:
            return 0
        driver_id = row['driver_id']

        # 佣金以实际支付金额为准
        pay_amount = float_ex(row['pay_amount'])

        # 司机佣金比例
        driver_info = self.driver.get_user_info_by_id(driver_id,'commission_rate')
        commission_rate = float_ex(driver_info['commission_rate'])
        commission = 0
        if commission_rate > 0:
            commission = round(pay_amount * commission_rate / 100,2)
        
        data = {
            'amount': commission,
            'driver_id': driver_id,
            'order_id': order_id,
            'remark': '订单佣金',
            'created_at': get_current_time(),
        }
        # 更新司机帐目表
        self.driver_account.insert_driver_account(data)

        return commission

        
if __name__ == '__main__':
    order = OrderLibs()
    
    lng = 102.16236416200229
    lat = 24.013375595069245
    minute = 30000
        
        
    result = order.find_nearby_drivers('token',lat,lng,1000,minute)