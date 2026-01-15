# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file    :   scheduler_route.py
@date    :   2024/06/07 09:40:51
@author  :   snz 
@version :   1.0
@email   :   274043505@qq.com
@desc    :   user端路由
'''

from flask import Blueprint, request, render_template,url_for,flash,g
from src.helper.helper import *
from src.controller.web.app.dispatch.dispatch_controller import DisPatchController

dispatch_route = Blueprint('dispatch_route',__name__)

@dispatch_route.before_request
def create_controller():
    # 使用g变量来存储控制器实例
    g.dispatch = DisPatchController()
    
@dispatch_route.teardown_request
def teardown_request(exception=None):
    """ 执行完成均会调用，可以作些清理工作"""
    if exception is not None:
        write_logger(str(exception))
        
@dispatch_route.before_request
def before_request_func():
    """验证中间件"""

    auth_response = dispatch.auth_token_middleware(['/app/api/dispatch/v1/login'])
    if auth_response:
        return auth_response
    
@dispatch_route.route('/login')
def index():
    return dispatch.login()