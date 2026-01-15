# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

from flask import Blueprint, request, render_template,url_for,flash,g
from src.helper.helper import *
from src.controller.admin.login_controller import *
from urllib.parse import urlparse
from settings import Config
from src.helper.captcha import Captcha
from src.controller.admin.order.order_controller import OrderController
from src.controller.admin.driver.driver_controller import DriverController

# 因index.py中蓝图注册了url前缀，故路由中无需再使用/admin前缀
admin_driver_route = Blueprint('admin_driver_route',__name__)

@admin_driver_route.before_request
def create_controller():
    # 使用g变量来存储控制器实例
    g._driver = DriverController()
    g._order = OrderController()
    
@admin_driver_route.teardown_request
def teardown_request(exception=None):
    """ 执行完成均会调用，可以作些清理工作"""
    if exception is not None:
        write_logger(str(exception))


@admin_driver_route.route('/car/list')
def car_list():
    # 注册审核
    return render_template("/admin/driver_car/car_list.html")

@admin_driver_route.route('/register/list/json')
def car_list_json():
    # 注册列表
    return g._driver.get_driver_verify_list()

@admin_driver_route.route('/register/delete',methods=['POST'])
def car_list_delete():
    # 注册删除
    return g._driver.delete_register()

@admin_driver_route.route('/register/verify',methods=['POST'])
def verify_driver_register():
    # 审核司机
    return g._driver.verify_driver_register()

@admin_driver_route.route('/list')
def driver_list():
    return render_template("/admin/driver_car/driver_list.html")

@admin_driver_route.route('/list/json')
def driver_list_json():
    return g._driver.get_driver_list()

@admin_driver_route.route('/update/status',methods=['POST'])
def driver_update_status():
    # 司机状态更新
    return g._driver.driver_update_status()

@admin_driver_route.route('/delete',methods=['POST'])
def driver_delete():
    # 司机删除
    return g._driver.driver_delete()
