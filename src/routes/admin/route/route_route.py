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
from src.controller.admin.business.route_controller import RouteController
from src.controller.admin.login_controller import LoginController

route_route = Blueprint('route_route',__name__)

@route_route.before_request
def create_controller():
    # 使用g变量来存储控制器实例
    g._route = RouteController()    
    g._login = LoginController()

@route_route.before_request
def before():
    if Config.APP_DEBUG:
        return
    # 解析URL
    #parsed_url = urlparse(request.path)
    # 获取路径部分
    #url = parsed_url.path
    # 获取路径最后一部分
    #last_part = url.split("/")[-1]

    # if not _login.IsLogin():
    #     flash("未登录")
    #     return render_template("/admin/login.html", title='登录')
    #    return redirect(url_for('admin_route.login'))
    
@route_route.teardown_request
def teardown_request(exception=None):
    """ 执行完成均会调用，可以作些清理工作"""
    if exception is not None:
        write_logger(str(exception))

@route_route.route('/list',methods=['GET'])
def route_list():
    return render_template("/admin/business/intercity_route/index.html")

@route_route.route('/list/json',methods=['GET'])
def route_list_json():
    return g._route.get_list()

@route_route.route('/delete',methods=['GET','POST'])
def route_delete():
    return g._route.delete()

@route_route.route('/update/status',methods=['GET','POST'])
def route_update_status():
    return g._route.update_status()

@route_route.route('/add',methods=['GET','POST'])
def route_add():
    if request.method == 'GET':
        return render_template("/admin/business/intercity_route/add.html")
    else:
        return g._route.add()

@route_route.route('/update',methods=['GET','POST'])
def route_update():
    if request.method == 'GET':        
        return render_template("/admin/business/intercity_route/edit.html")
    else:
        return g._route.update()

@route_route.route('/detail',methods=['GET'])
def route_detail():
    row = g._route.get_one()    
    return echo_json(0, '查询成功', row)