# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   wechat_route.py
@date     :   2025/03/08 15:33:40
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   微信端公共路由
'''

from flask import Blueprint, request, render_template,url_for,flash,g,session,abort
from src.helper.helper import *
from src.controller.web.wechat.wechat_controller import WechatController
from urllib.parse import urlparse
from settings import Config
from src.controller.web.wechat.order_controller import OrderController
from src.controller.web.wechat.coupon_controller import CouponController
wechat_route = Blueprint('wechat_route',__name__)

@wechat_route.before_request
def create_controller():
    # 只可微信访问
    if not is_wechat:
        return abort(404)
    
    # 使用g变量来存储控制器实例
    if not hasattr(g, 'wx_order'):
        g.wx_order = OrderController()
    if not hasattr(g, 'wxapp'):
        g.wxapp = WechatController()
    if not hasattr(g, 'wx_coupon'):
        g.wx_coupon = CouponController()
    
@wechat_route.teardown_request
def teardown_request(exception=None):
    """ 执行完成均会调用，可以作些清理工作"""
    if exception is not None:
        write_logger(str(exception))
@wechat_route.before_request
def before_request_func():
    """验证中间件"""
    if Config.APP_DEBUG:
        return
    
    # wechat 端打开的页面，不验证，自行去验证带的token
    if '/wechat/api/v1/web' in request.path:
        return
        
    auth_response = g.wxapp.auth_token_middleware(['/wechat/api/v1/wx_login',
                                                   '/wechat/api/v1/refresh_token',
                                                   '/wechat/api/v1/submit_order',
                                                   '/wechat/api/v1/order_payment',
                                                   '/wechat/api/v1/getPhone',
                                                   '/wechat/api/v1/price_calculate'])
    if auth_response:
        return auth_response

@wechat_route.route('/wx_login')
def wx_login():
    """微信登录，换取openid
    """
    return g.wxapp.wx_login()

@wechat_route.route('/get_params')
def get_params():
    """微信获取参数配置
    """
    return g.wxapp.get_params()

@wechat_route.route('/refresh_token',methods=['POST'])
def wx_refresh_token():
    """根据openid刷新token
    """
    return g.wxapp.refresh_token()

@wechat_route.route('/getPhone',methods=['POST'])
def getPhone():
    """获取小程序用户手机号
    """
    return g.wxapp.get_phone()

@wechat_route.route('/submit_order',methods=['POST'])
def submit_order():
    """小程序打车订单提交
    """
    return g.wx_order.create_order()

@wechat_route.route('/again_order',methods=['POST'])
def again_order():
    """小程序打车订单再次叫车
    """
    return g.wx_order.update_order()

@wechat_route.route('/cancel_order',methods=['POST'])
def cancel_order():
    """小程序打车订单取消
    """
    return g.wx_order.cancel_order()

@wechat_route.route('/order_payment',methods=['POST'])
def order_payment():
    """小程序打车订单支付
    """
    return g.wx_order.order_payment()

@wechat_route.route('/price_calculate',methods=['POST'])
def price_calculate():
    """小程序用户选择目的地后计算预估价格
    """
    return g.wx_order.price_calculate()

@wechat_route.route('/get_my_coupon',methods=['GET'])
def get_my_coupon():
    """小程序用户获取自己的优惠券
    """
    # 这里为适配小程序web端页面，所以要解码用户ID传入
    uid = 0
    uid = g.wx_coupon.decode_wechat_token()
    if uid is None:
        return echo_json(-1, "token过期或无效")
    return g.wx_coupon.get_coupon_my_list(uid)

@wechat_route.route('/subscribe_tpl',methods=['POST'])
def subscribe_tpl():
    """提交小程序用户订阅消息模板
    """        
    return g.wxapp.subscribe_tpl()

@wechat_route.route('/get_order_info',methods=['POST'])
def get_order_info():
    """小程序订单获取
    """        
    return g.wx_order.get_order_detail()

@wechat_route.route('/delete_account',methods=['POST'])
def delete_account():
    """注销帐号
    """        
    return g.wxapp.delete_account()

######### 小程序端web页面路由 ##########

def verify_wechat_web_token():
    """验证小程序端token及openid，以确认是否可访问
    """
    openid = get_param_by_str('op')
    token = get_param_by_str('tk')
    uid = decode_token(token)
    if uid is None or uid is False:
        if session.get('uid') is not None:
            uid = session['uid']
            return uid
        else:
            row = g.wxapp._db.get_user_by_openid(openid,"openid,token,id")
            if row is None:
                return None
            uid = row['id']
        
    session['uid'] = uid
    session['token'] = token
    session['openid'] = openid
    session['is_wechat'] = True

    return uid
@wechat_route.route('/web/member/trip',methods=['POST','GET'])
def member_trip():
    """小程序我的行程列表
    """    
    if request.method == 'POST':
        pass
    else:
        uid = verify_wechat_web_token()
        if uid is None:
            return echo_json(-1,"token error")
        
        return render_template('/wechat/trip.html',uid=session['uid'],token=session['token'],openid=session['openid'])
    
@wechat_route.route('/web/member/trip/json',methods=['POST','GET'])
def get_my_trip():
    # 我的行程列表
    uid = verify_wechat_web_token()
    if uid is None:
        return echo_json(-1,"token error")
        
    return g.wx_order.get_my_trip(uid)

@wechat_route.route('/web/member/trip/comment',methods=['POST','GET'])
def trip_comment():
    """小程序评价行程
    """
    uid = verify_wechat_web_token()
    if uid is None:
        return echo_json(-1,"token error")
        
    return g.wx_order.trip_comment()

@wechat_route.route('/web/member/order/detail',methods=['POST'])
def get_order_detail():
    """小程序订单详情
    """
    if request.method == 'POST':
        return g.wx_order.get_order_detail()

@wechat_route.route('/web/member/emergency',methods=['POST','GET'])
def member_emergency():
    """小程序紧急联系人列表
    """
    if request.method == 'POST':
        return g.wxapp.member_emergency()
    else:
        uid = verify_wechat_web_token()
        if uid is None:
            return echo_json(-1,"token error")
        
        return render_template('/wechat/emergency_contact.html',uid=session['uid'],token=session['token'],openid=session['openid'])

@wechat_route.route('/web/member/emergency/json',methods=['GET'])
def member_emergency_json():
    uid = get_param_by_int("uid")
    result = g.wxapp.get_member_emergency(uid)
    return echo_json(0,"success",result)


@wechat_route.route('/web/member/agreement',methods=['GET'])
def member_agreement():
    """小程序用户协议
    """
    return render_template('/wechat/agreement.html')

@wechat_route.route('/web/member/coupon_list',methods=['GET'])
def member_coupon_list():
    """小程序优惠券列表
    """
    uid = verify_wechat_web_token()
    if uid is None:
        return echo_json(-1,"token error")
    
    # 1.获取用户的优惠券列表
    return render_template('/wechat/coupon_list.html')

@wechat_route.route('/web/member/coupon_list/json',methods=['GET'])
def member_coupon_list_json():
    """小程序优惠券列表
    """
    uid = verify_wechat_web_token()
    if uid is None:
        return echo_json(-1,"token error")
    
    return g.wx_coupon.get_coupon_my_list(uid)

@wechat_route.route('/web/member/coupon_center',methods=['GET'])
def member_coupon_center():
    """小程序优惠券中心
    """
    if request.method == 'GET':
        uid = verify_wechat_web_token()
        if uid is None:
            return echo_json(-1,"token error")
        
        return render_template('/wechat/coupon_center.html')

@wechat_route.route('/web/member/coupon_center/json',methods=['GET','POST'])
def coupon_center_json():
    """优惠券中心json数据
    """
    uid = verify_wechat_web_token()
    if uid is None:
        return echo_json(-1,"token error")
    
    if request.method == 'GET':
        return g.wx_coupon.get_coupon_list(uid)
    else:
        coupon_id = get_param_by_int('coupon_id')
        return g.wx_coupon.take_coupon(uid,coupon_id)

@wechat_route.route('/web/member/contact_us',methods=['GET'])
def member_contact_us():
    """联系我们页面
    """
    uid = verify_wechat_web_token()
    if uid is None:
        return echo_json(-1,"token error")
    
    service_phone = ''
    site_config = get_current_site_config()
    if site_config and 'service_phone' in site_config:
        service_phone = site_config['service_phone']
    return render_template('/wechat/contact_us.html',service_phone = service_phone)

@wechat_route.route('/web/pay_success',methods=['GET'])
def pay_success():
    """小程序端支付成功后打开的页面
    """
    uid = verify_wechat_web_token()
    if uid is None:
        return echo_json(-1,"token error")
    # 小程序支付后带来的订单id，暂时没有使用
    order_id = get_param_by_str('order_id')

    return render_template('/wechat/pay_success.html',order_id=order_id,uid=session['uid'],token=session['token'],openid=session['openid'])

@wechat_route.route('/web/public',methods=['GET'])
def public_oage():
    """公共页面，http://192.168.3.198:8002/wechat/api/v1/web/ 为公共页面
        可以传入public即可调用本页
    """
    uid = verify_wechat_web_token()
    if uid is None:
        return echo_json(-1,"token error")
    
    return echo_json(0,"this pulic page")

@wechat_route.route('/web/invoice',methods=['GET'])
def invoice():
    return render_template('/wechat/invoice.html')