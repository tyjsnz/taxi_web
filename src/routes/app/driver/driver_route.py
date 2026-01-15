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
@file    :   driver_route.py
@date    :   2024/06/07 09:40:51
@author  :   snz 
@version :   1.0
@email   :   274043505@qq.com
@desc    :   driver端路由，主要针对app程序
'''

from flask import Blueprint, request, render_template,url_for,flash,g
from src.helper.helper import *
from src.controller.web.app.driver.driver_controller import *

# 因index.py中蓝图注册了url前缀，故路由中无需再使用/admin前缀
driver_route = Blueprint('driver_route',__name__)

@driver_route.before_request
def create_controller():
    # 使用g变量来存储控制器实例
    if not hasattr(g, '_driver'):
        g._driver = DriverController()
    pass
    
@driver_route.teardown_request
def teardown_request(exception=None):
    """ 执行完成均会调用，可以作些清理工作"""
    if exception is not None:
        write_logger(str(exception))
        
@driver_route.before_request
def before_request_func():
    """验证中间件"""

    if Config.APP_DEBUG:
        return None
    auth_response = g._driver.auth_token_middleware(['/app/api/driver/v1/login','/app/api/driver/v1/push_location'])
    if auth_response:
        return auth_response
    
@driver_route.route('/login', methods=['GET', 'POST'])
def driver_login():
    return g._driver.app_login()

@driver_route.route('/logout', methods=['POST'])
def driver_logout():
    return g._driver.app_logout()

@driver_route.route('/verify_phone', methods=['POST'])
def driver_verify_phone():
    # 司机手机号是否已注册
    return g._driver.verify_phone()

@driver_route.route('/get_sms_code', methods=['POST'])
def get_sms_code():
    # 获取验证码
    return g._driver.get_sms_code()

@driver_route.route('/verify_phone_code', methods=['POST'])
def verify_phone_code():
    # 验证手机号和验证码
    return g._driver.verify_phone_code()

@driver_route.route('/pwd_setup', methods=['POST'])
def pwd_setup():
    # 修改密码
    return g._driver.pwd_setup()

@driver_route.route('/push_location',methods=['GET','POST'])
def push_location():
    """司机端推送位置
    """
    return g._driver.update_driver_latlng()

@driver_route.route('/push_navi',methods=['GET','POST'])
def update_navi_latlng():
    """导航位置推送
    """
    return g._driver.update_navi_latlng()

@driver_route.route('/work_status',methods=['POST'])
def work_status():
    """修改司机工作状态"""
    return g._driver.update_work_status()

@driver_route.route('/order/bill/send',methods=['POST'])
def update_order_status():
    """司机端发送订单账单"""
    return g._driver.update_order_bill()

@driver_route.route('/order/accept/confirm',methods=['POST'])
def order_accept():
    """司机端接单"""
    return g._driver.order_accept()

@driver_route.route('/order_reject',methods=['POST'])
def order_reject():
    """司机端拒绝接单"""
    return g._driver.order_reject()

@driver_route.route('/take_cash/apply',methods=['POST'])
def take_cash_apply():
    """司机端申请提现"""
    return g._driver.apply_take_cash()

@driver_route.route('/order/trip',methods=['POST'])
def order_trip():
    """司机端订单行程"""
    return g._driver.order_trip()

@driver_route.route('/heatmap',methods=['GET'])
def get_heatmap():
    """获取热力图数据"""
    return g._driver.get_heatmap_data()

@driver_route.route('/heat_order_data',methods=['GET'])
def get_order_total_by_day():
    """获取当天订单统计数据，及指定前几天的数据"""
    return g._driver.get_order_total_by_day()

@driver_route.route('/get_score_list',methods=['GET'])
def get_score_list():
    """获取司机积分列表"""
    return g._driver.get_score_list()

@driver_route.route('/set_driver_accept_order_model',methods=['POST'])
def set_driver_accept_order_model():
    """司机接单模式设置"""
    return g._driver.set_driver_accept_order_model()

@driver_route.route('/order/detail',methods=['GET'])
def get_order_detail():
    """获取订单详情"""
    return g._driver.get_order_by_id()

@driver_route.route('/reward/list',methods=['GET'])
def reward_list():
    """司机奖励列表"""
    return echo_json(0,'success')