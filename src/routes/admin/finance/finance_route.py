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
from src.controller.admin.driver.driver_controller import DriverController
from src.controller.admin.finance.finance_controller import FinanceController

finance_route = Blueprint('finance_route',__name__)

@finance_route.before_request
def create_controller():
    # 使用g变量来存储控制器实例
    g._company = CompanyController()    
    g._login = LoginController()
    g._driver = DriverController()
    g._finance = FinanceController()

@finance_route.before_request
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
    
@finance_route.teardown_request
def teardown_request(exception=None):
    """ 执行完成均会调用，可以作些清理工作"""
    if exception is not None:
        write_logger(str(exception))
        

@finance_route.route('/commission/list',methods=['GET'])
def commission_list():
    # 佣金管理
    return render_template("/admin/finance/commission.html")

@finance_route.route('/commission/list/json',methods=['GET'])
def commission_list_get():
    # 佣金管理
    return g._finance.get_commission_list()


@finance_route.route('/take_cash',methods=['GET'])
def driver_take_cash():
    # 司机提现
    return render_template('/admin/finance/take_cash.html')

@finance_route.route('/take_cash/json',methods=['GET'])
def driver_take_cash_json():
    # 司机提现列表
    return g._finance.get_take_list()

@finance_route.route('/take_cash/audit',methods=['POST'])
def driver_take_cash_audit():
    # 司机提现审核，通过、拒绝
    return g._finance.take_cash_audit()

@finance_route.route('/invoice',methods=['GET','POST'])
def invoice():
    if request.method == 'GET':
        return render_template('/admin/finance/invoice.html')
    else:
        pass

@finance_route.route('/invoice/json',methods=['GET'])
def invoice_json():
    return g._finance.get_invoice()

@finance_route.route('/invoice/approve',methods=['POST'])
def invoice_approve():
    return g._finance.invoice_approve()

@finance_route.route('/invoice/reject',methods=['POST'])
def invoice_reject():
    return g._finance.invoice_reject()

@finance_route.route('/baodan',methods=['GET'])
def baodan():
    return render_template("/admin/finance/baodan.html")

@finance_route.route('/report',methods=['GET'])
def report():
    return render_template('/admin/finance/report.html')

@finance_route.route('/report/total',methods=['GET'])
def report_total():
    pass