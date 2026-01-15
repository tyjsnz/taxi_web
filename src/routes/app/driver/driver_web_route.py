# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file    :   driver_web_route.py
@date    :   2025/04/08 12:37:09
@author  :   snz
@version :   1.0
@email   :   274043505@qq.com
@copyright:   Copyright (C) kmlskj All Rights Reserved.
@desc    :   司机端h5路由

'''

from flask import Blueprint, request, render_template,abort,g,session
from src.helper.helper import *
from src.controller.web.app.driver.driver_controller import *
import pytz,jwt,datetime,logging
from loguru import logger
import inspect
import os

driver_web_route = Blueprint('driver_web_route',__name__)

@driver_web_route.before_request
def create_controller():    
    # 使用g变量来存储控制器实例
    if not hasattr(g, '_driver'):
        g._driver = DriverController()
    
@driver_web_route.teardown_request
def teardown_request(exception=None):
    """ 执行完成均会调用，可以作些清理工作"""
    if exception is not None:
        write_logger(str(exception))
    try:
        _driver = getattr(g, '_driver', None)
        if _driver is not None:
            pass
            #g._driver.close_all_db()        
    except Exception as e:
        write_logger(str(e))
        
@driver_web_route.before_request
def before_request_func():
    """验证中间件"""

    # get 访问情况下这几个页直接打开，故不检测toek，由页面自行在get参数中检测token
    if request.method == 'GET' and request.path in ['/app/driver/','/app/driver/register','/app/driver/register/upload','/app/driver/member','/app/driver/chat']:
        return None
    
    return None
    token = get_header_token_by_bearer()
    uid = decode_token(token)
    if uid:
        pass
    else:
        # 测试，正式时要打开
        if Config.APP_DEBUG:
            return None
        return abort(404)

def verify_rquest():
    """在使用web打开页面时检查token,并得到用户ID"""
    if session.get('driver_id') != None and session.get('token') != None:
        return session.get('driver_id'),session.get('token')

    d = session.get('driver_id')
    t = session.get('token')
    token = get_param_by_str('token')
    driver_id = decode_token(token)
        
    if Config.APP_DEBUG:
        if driver_id != 0:
            session["driver_id"] = driver_id
            session['token'] = token
            return driver_id, token
        
        return get_param_by_int('driver_id'),token
    
    if token == None or not driver_id:
        return abort(404)
    
    session["driver_id"] = driver_id
    session['token'] = token
    
    return driver_id,token
@driver_web_route.route('/',methods=['POST','GET'])
def driver_index():
    """司机首页"""
    if request.method == "GET":
        driver_id,token = verify_rquest()
        
        # return render_template('/app/driver_home.html',token=token,driver_id=driver_id)
        return render_template('/app/test/index.html',token=token,driver_id=driver_id)
    else:
        return echo_json(0,"ok",{'data': 'data'})

@driver_web_route.route('/register',methods=['POST','GET'])
def driver_register():
    # 注册时带了手机号
    phone = get_param_by_str('phone')
    return render_template('/app/test/driver_register.html',phone=phone)

@driver_web_route.route('/member',methods=['POST','GET'])
def driver_member():
    # 暂不用
    driver_id,token = verify_rquest()
    return render_template('/app/driver_member.html',token=token,driver_id=driver_id)

@driver_web_route.route('/chat',methods=['POST','GET'])
def driver_chat_message():
    # 暂不用
    return render_template('/app/driver_chat_message.html')

@driver_web_route.route('/order/accept/list',methods=['GET'])
def order_accept_list():
    driver_id = get_param_by_int('driver_id')
    if driver_id <= 0 or driver_id == '':
        driver_id = session.get('driver_id')
    return g._driver.get_accept_order_list(driver_id)

@driver_web_route.route('/order/total_data',methods=['GET'])
def my_order_total_data():
    driver_id = get_param_by_int('driver_id')
    if driver_id <= 0 or driver_id == '':
        driver_id = session.get('driver_id')

    if driver_id == None or driver_id == '':
        driver_id = 0
        
    # 工作状态,用于更新在线时长
    work_status = get_param_by_int('work_status')
    return g._driver.get_my_order_total_data(driver_id,work_status)

@driver_web_route.route('/order/today_order_data',methods=['GET'])
def get_today_order():
    #今天完单
    driver_id = get_param_by_int('driver_id')
    if driver_id <= 0 or driver_id == '':
        driver_id = session.get('driver_id')
    return g._driver.get_today_order(driver_id)

@driver_web_route.route('/order/list',methods=['GET'])
def my_order_list():
    """接单列表页"""
    driver_id,token = verify_rquest()
    return render_template('/app/driver_order_list.html',token=token,driver_id=driver_id)

@driver_web_route.route('/order/list/json',methods=['GET'])
def my_order_list_json():
    """接单列表页"""
    driver_id = get_param_by_int('driver_id')
    return g._driver.get_my_order_list(driver_id)

@driver_web_route.route('/order/income_detail',methods=['GET'])
def amount_list():
    """收入明细"""
    driver_id,token = verify_rquest()
    return render_template('/app/driver_amount.html',token=token,driver_id=driver_id)

@driver_web_route.route('/order/check_out_pay',methods=['GET'])
def check_out_pay():
    #提现
    driver_id,token = verify_rquest()
    return render_template('/app/driver_pay_checkout.html',token=token,driver_id=driver_id)

@driver_web_route.route('/take_cash/json',methods=['GET','POST'])
def take_cash_json():
    # 提现记录及余额
    if request.method == 'GET':
        return g._driver.driver_take_cash_list()
    else:
        # 提现申请
        return g._driver.apply_take_cash()

@driver_web_route.route('/edit',methods=['GET'])
def driver_edit():
    #修改
    driver_id,token = verify_rquest()
    return render_template('/app/driver_edit.html',token=token,driver_id=driver_id)

@driver_web_route.route('/profile/json',methods=['GET','POST'])
def driver_edit_json():
    # 司机信息获取
    if request.method == 'GET':
        return g._driver.get_my_profile()
    else:
        return g._driver.update_my_profile()

@driver_web_route.route('/suggest',methods=['GET'])
def driver_suggest():
    #建议
    driver_id,token = verify_rquest()
    return render_template('/app/driver_suggest.html',token=token,driver_id=driver_id)
@driver_web_route.route('/suggest/submit',methods=['POST'])
def driver_suggest_submit():
    #建议
    return g._driver.driver_suggest_submit()
@driver_web_route.route('/agreement',methods=['GET'])
def driver_agreement():
    #协议
    driver_id,token = verify_rquest()
    return render_template('/app/driver_agreement.html',token=token,driver_id=driver_id)

@driver_web_route.route('/register/upload',methods=['POST'])
def register_upload():
    #注册上传图片 
    return g._driver.driver_license_upload()

@driver_web_route.route('/register/submit',methods=['POST'])
def register_submit():
    #司机注册
    return g._driver.driver_register()

@driver_web_route.route('/in_come/detail/json',methods=['GET'])
def income_detail_json():
    #司机收入明细
    return g._driver.get_driver_account_detail()

############## new ui ################
@driver_web_route.route('/order_list.html',methods=['GET'])
def order_list_html():
    return render_template('/app/test/order_list.html')

@driver_web_route.route('/pay_checkout.html',methods=['GET'])
def pay_checkout_html():
    return render_template('/app/test/pay_checkout.html')

@driver_web_route.route('/reward_list.html',methods=['GET'])
def reward_list_html():
    return render_template('/app/test/reward_list.html')

@driver_web_route.route('/service_center.html',methods=['GET'])
def service_center():
    return render_template('/app/test/service_center.html')

@driver_web_route.route('/setup.html',methods=['GET'])
def setup_html():
    return render_template('/app/test/setup.html')

@driver_web_route.route('/qrscan.html',methods=['GET'])
def qrscan_html():
    return render_template('/app/test/qrscan.html')

@driver_web_route.route('/notice_list.html',methods=['GET'])
def notice_html():
    return render_template('/app/test/notice_list.html')

@driver_web_route.route('/score_list.html',methods=['GET'])
def score_list_html():
    return render_template('/app/test/score_list.html')

@driver_web_route.route('/money_record.html',methods=['GET'])
def money_record_html():
    return render_template('/app/test/money_record.html')

@driver_web_route.route('/today_complete_order.html',methods=['GET'])
def today_complete_order_html():
    return render_template('/app/test/today_complete_order.html')

@driver_web_route.route('/filter_order.html',methods=['GET'])
def filter_order_html():
    return render_template('/app/test/filter_order.html')

@driver_web_route.route('/grab_order.html',methods=['GET'])
def grab_order_html():
    return render_template('/app/test/grab_order.html')

@driver_web_route.route('/grab_order_ad.html',methods=['GET'])
def grab_order_ad_html():
    return render_template('/app/test/grab_order_ad.html')

@driver_web_route.route('/yxpd.html',methods=['GET'])
def gyxpd_html():
    # 优先派单，未使用
    return render_template('/app/test/yxpd.html')

@driver_web_route.route('/hot_map.html',methods=['GET'])
def hot_map_html():
    return render_template('/app/test/hot_map.html')

@driver_web_route.route('/sel_address.html',methods=['GET'])
def sel_address_html():
    return render_template('/app/test/sel_address.html')

@driver_web_route.route('/region.html',methods=['GET'])
def region_html():
    return render_template('/app/test/region.html')

@driver_web_route.route('/hot_order_time.html',methods=['GET'])
def hot_order_time_html():
    return render_template('/app/test/hot_order_time.html')

@driver_web_route.route('/reg.html',methods=['GET'])
def reg_html():
    # 带车加入或自带车加入，这里要在app中做判断
    return render_template('/app/test/reg.html')

@driver_web_route.route('/violation_list.html',methods=['GET'])
def violation_list_html():
    return render_template('/app/test/violation_list.html')

@driver_web_route.route('/my_task.html',methods=['GET'])
def my_task_html():
    return render_template('/app/test/my_task.html')

@driver_web_route.route('/bank_card_add.html',methods=['GET'])
def bank_card_add_html():
    return render_template('/app/test/bank_card_add.html')

@driver_web_route.route('/my_info.html',methods=['GET'])
def my_info_html():
    return render_template('/app/test/my_info.html')

@driver_web_route.route('/trip_over.html',methods=['GET'])
def trip_over_html():
    order_id = get_param_by_int('order_id')
    return render_template('/app/test/trip_over.html',order_id=order_id)

@driver_web_route.route('/zhaq.html',methods=['GET'])
def zhaq():
    # 帐号安全
    return render_template('/app/test/zhaq.html')

@driver_web_route.route('/law.html',methods=['GET'])
def law():
    # 法律条款
    return render_template('/app/test/law.html')

@driver_web_route.route('/aboutus.html',methods=['GET'])
def aboutus():
    return render_template('/app/test/aboutus.html')
@driver_web_route.route('/edit_pwd.html',methods=['GET','POST'])
def edit_pwd_html():
    if request.method == 'POST':
        return g._driver.pwd_setup()
    return render_template('/app/test/edit_pwd.html')

@driver_web_route.route('/edit_phone.html',methods=['GET','POST'])
def edit_phone_html():
    if request.method == 'POST':
        return g._driver.edit_phone()
    return render_template('/app/test/edit_phone.html')

@driver_web_route.route('/change_car.html',methods=['GET','POST'])
def change_car():
    if request.method == 'POST':
        return g._driver.change_car()
    return render_template('/app/test/change_car.html')

@driver_web_route.route('/change_car/upload_img',methods=['POST'])
def change_car_upload_img():
    from src.helper.upload_service import UploadService
    file  =request.files.get('file')
    return UploadService.UploadByFile(file)

# @driver_web_route.route('/agreement',methods=['GET'])
# def driver_agreement():
#     return render_template('/app/test/agreement.html')