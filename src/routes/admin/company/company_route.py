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
from src.controller.admin.business.company_controller import CompanyController
from src.controller.admin.login_controller import LoginController

# 因index.py中蓝图注册了url前缀，故路由中无需再使用/admin前缀
company_route = Blueprint('company_route',__name__)

@company_route.before_request
def create_controller():
    # 使用g变量来存储控制器实例
    g._company = CompanyController()    
    g._login = LoginController()

@company_route.before_request
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
    
@company_route.teardown_request
def teardown_request(exception=None):
    """ 执行完成均会调用，可以作些清理工作"""
    if exception is not None:
        write_logger(str(exception))

@company_route.route('/list',methods=['GET'])
def company_list():
    return render_template("/admin/business/company/index.html")

@company_route.route('/list/json',methods=['GET'])
def company_list_json():
    return g._company.get_list()

@company_route.route('/delete',methods=['GET','POST'])
def company_delete():
    return g._company.delete()

@company_route.route('/update/status',methods=['GET','POST'])
def company_update_status():
    return g._company.update_status()

@company_route.route('/add',methods=['GET','POST'])
def company_add():
    if request.method == 'GET':
        return render_template("/admin/business/company/add.html")
    else:
        return g._company.add()

@company_route.route('/update',methods=['GET','POST'])
def company_update():
    if request.method == 'GET':
        row = g._company.get_one()
        return render_template("/admin/business/company/edit.html",row=row)
    else:
        return g._company.update()
    
@company_route.route('/delete/img',methods=['POST'])
def company_delete_img():    
    return g._company.delete_img()

@company_route.route('/commission/setup',methods=['GET','POST'])
def commission_setup():
    # 佣金设置页
    if request.method == 'POST':
        # 佣金设置
        return g._company.commission_setup()
    
    return render_template("/admin/business/company/commission_setup.html")

@company_route.route('/commission/setup/json',methods=['GET'])
def commission_setup_json():
    # 佣金列表
    return g._company.get_list()

@company_route.route('/commission/driver/json',methods=['GET'])
def commission_driver_json():
    # 司机佣金
    return g._company.get_commission_driver_list()

@company_route.route('/commission/driver/setup',methods=['POST'])
def commission_driver_setup():
    # 司机佣金
    return g._company.commission_driver_setup()