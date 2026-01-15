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
from src.controller.admin.customer.customer_controller import CustomerController
from src.controller.admin.admin_controller import AdminController
from src.controller.admin.coupon.coupon_controller import CouponController
from src.model.base_db import PublicDbConnection

admin_route = Blueprint('admin_route',__name__)

@admin_route.before_request
def create_controller():
    # 使用g变量来存储控制器实例
    if not hasattr(g,'_login'):
        g._login = LoginController()
    if not hasattr(g,'_driver'):
        g._driver = DriverController()
    if not hasattr(g,'_captcha'):
        g._captcha = Captcha()
    if not hasattr(g,'_order'):
        g._order = OrderController()
    if not hasattr(g,'_customer'):
        g._customer = CustomerController()            
    if not hasattr(g,'_admin'):
        g._admin = AdminController()    
    if not hasattr(g, '_coupon'):
        g._coupon = CouponController()
    
@admin_route.teardown_request
def teardown_request(exception=None):
    """ 执行完成均会调用，可以作些清理工作"""
    if exception is not None:
        write_logger(str(exception))
        
@admin_route.before_request
def before():
    if Config.APP_DEBUG:
        return
    # 解析URL
    #parsed_url = urlparse(request.path)
    # 获取路径部分
    #url = parsed_url.path
    # 获取路径最后一部分
    #last_part = url.split("/")[-1]

    # admin/login部份不作验证，因还未登录
    if request.path in ["/admin/login",'/admin/captcha']:
        return None

    # if not _login.IsLogin():
    #     flash("未登录")
    #     return render_template("/admin/login.html", title='登录')
        
@admin_route.route('/upload_file',methods=['POST'])
def upload_file():
    # 上传系统文件图片
    return g._admin.upload_sys_setup_img()
@admin_route.route('/remove_file',methods=['POST'])
def remove_upload_file():
    # 移除系统文件图片
    f = get_param_by_str('file_path')
    delete_file(f)
    return echo_json(0,'success')
    
def gotoLogin():
    flash("未登录")
    return redirect(url_for('admin_route.login'))

@admin_route.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        if g._login.IsLogin():
            return redirect("/admin/")
        else:
            return render_template("/admin/login.html", title='登录')
    else:
        vcode = get_param_by_str('vcode')
        if vcode == '':
            return echo_json(-1,"验证码错误")
        if not g._captcha.verify_captcha(vcode):
            return echo_json(-1,"验证码不正确")
        
        return g._login.login()

@admin_route.route('/captcha',methods=['GET'])
def get_captcha():
    w = get_param_by_int('w')
    h = get_param_by_int('h')
    return g._captcha.get_captcha(w,h)

@admin_route.route('/logout',methods=['GET'])
def logout():
    return g._login.logout()

@admin_route.route('/region')
def get_region():
    # 通用获取地区
    sql = f"select * from ls_region order by id asc"
    result = g._login.db._query_sql(sql)
    return echo_json(0,'success',result)

@admin_route.route('/sys/system_setup',methods=['POST','GET'])
def site_setup():
    # 站点设置
    if request.method == "GET":
        row = g._admin.get_system_setup()        
        return render_template('/admin/sys/site_setup.html',row=row)
    else:
        return g._admin.system_setup()
        

@admin_route.route('/main')
def adminindex():
    data = {'truename':'','username':''}
    data['truename'] = session.get('truename')
    data['username'] = session.get('username')
    return render_template("/admin/index.html",data=data,is_admin=session.get('is_admin'))

@admin_route.route('/index')
def adminIndex():
    return render_template("/admin/main.html",is_admin=session.get('is_admin'))

@admin_route.route('/monitor',methods=['GET'])
def monitor():
    return render_template("/admin/monitor/index.html")

@admin_route.route('/monitor/car/list',methods=['GET'])
def monitor_car_list():
    return g._driver.get_car_gps()

@admin_route.route('/monitor/map/region',methods=['GET','POST'])
def monitor_map_region():
    if request.method == 'POST':
        cid = int_ex(get_param_by_json('company_id'))
        id = int_ex(get_param_by_json('id'))
        _path = get_param_by_json('path')

        import json
        dd = json.dumps(_path)
        
        # 确保 Polygon 是闭合的（MySQL 要求）
        if _path and _path[0] != _path[-1]:
            _path.append(_path[0])
        # 将_path转成WKT格式字符串
        points = ", ".join([f"{lon} {lat}" for lon, lat in _path])
        wkt_polygon = f"POLYGON(({points}))"
        
        # 添加
        if id <= 0:
            sql = f"insert into ls_company_map(company_id,center_lng, center_lat, radius, path_data,latlng) values({cid},'','',0,'{dd}',ST_GeomFromText('{wkt_polygon}'))"
        else:
            sql = f"update ls_company_map set path_data='{dd}',latlng = ST_GeomFromText('{wkt_polygon}') where id={id}"

        db = PublicDbConnection()
        ret = db._execute_sql(sql)
        return echo_json(0,'success',ret)
    
    else:
        return render_template("/admin/monitor/map_region.html")
    
@admin_route.route('/monitor/map/region/delete',methods=['POST'])
def monitor_map_region_delete():
    if request.method == 'POST':
        cid = get_param_by_int('cid')
        id = get_param_by_int('id')
        if id <= 0 or cid <= 0:
            return echo_json(-1,'参数错误')
        else:
            sql = f"delete from ls_company_map where id={id} and company_id={cid}"
            db = PublicDbConnection()
            ret = db._execute_sql(sql)
            return echo_json(0,'success',ret)

@admin_route.route('/monitor/map/region/json',methods=['GET'])
def monitor_map_region_json():
    db = PublicDbConnection()
    id = get_param_by_int('company_id')
    sql = f"select id,path_data from ls_company_map where company_id = {id}"
    result = db._query_sql(sql,use_cache=False)
    import json
    for row in result:
        row['path_data'] = json.loads(row['path_data'])
    return echo_json(0,'success',result)

@admin_route.route('/order/list')
def order_list():
    return render_template("/admin/order/list.html")

@admin_route.route('/order/list/json',methods=['GET'])
def order_list_json():
    return g._order.get_order_list()

@admin_route.route('/order/detail',methods=['GET'])
def order_detail():
    row = g._order.get_one()
    return render_template("/admin/order/detail.html",row=row)

@admin_route.route('/order/dispatch',methods=['GET'])
def order_dispatch():
    return render_template("/admin/order/dispatch.html")

@admin_route.route('/coupons/list')
def coupons_list():
    # 优惠券
    return render_template("/admin/coupons/coupon_list.html")

@admin_route.route('/coupons/list/json',methods=['GET'])
def coupons_list_json():
    # 优惠券
    return g._coupon.get_list()

@admin_route.route('/coupons/add',methods=['GET','POST'])
def coupons_add():
    # 优惠券
    if request.method == 'GET':
        return render_template("/admin/coupons/add_coupon.html")
    else:
        return g._coupon.add()

@admin_route.route('/coupons/take/list')
def coupons_take_list():
    # 优惠券领用记录
    id = get_param_by_int('id')
    return render_template("/admin/coupons/coupon_take_list.html",id=id)

@admin_route.route('/coupons/take/list/json',methods=['GET'])
def coupons_take_list_json():
    # 优惠券领用记录
    return g._coupon.get_take_list()

@admin_route.route('/coupons/delete',methods=['POST'])
def coupons_delete():
    # 优惠券删除
    return g._coupon.delete_coupons()

@admin_route.route('/coupons/total')
def coupons_total():
    # 优惠券统计
    if request.method == 'GET':
        return render_template("/admin/coupons/index.html")

@admin_route.route('/coupons/total/json',methods=['GET'])
def coupons_total_json():
    # 优惠券统计
    return g._coupon.total_coupons()
    

@admin_route.route('/price/list')
def price_list():
    return render_template("/admin/business/index.html")

@admin_route.route('/price/list/json')
def price_list_json():
    return g._driver.get_price_list()

@admin_route.route('/price/add',methods=['GET','POST'])
def price_add():
    if request.method == 'GET':
        return render_template("/admin/business/add.html")
    else:
        return g._order.taxi_fee_setting()
    
@admin_route.route('/price/delete',methods=['POST'])
def price_delete():
    return g._order.taxi_fee_del()


@admin_route.route('/suggest')
def suggest():
    # 意见建议
    return render_template("/admin/sys/suggest.html")

@admin_route.route('/notice', methods=['GET','POST'])
def notice():
    # 通知
    if request.method == 'GET':
        return render_template("/admin/business/notice/index.html")
    else:
        import redis,json
        from settings import DatabaseConfig
        REDIS_HOST = DatabaseConfig.REDIS_HOST
        REDIS_PORT = DatabaseConfig.REDIS_PORT
        CHANNEL_NAME = 'websocket_messages'
        pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
        redis_conn = redis.Redis(connection_pool=pool)
        channel = CHANNEL_NAME

        try:
            # passenger=乘客，driver=司机，system=系统
            _type = get_param_by_str('type')            
            if _type not in ['passenger','driver','system']:
                return echo_json(-1,'参数错误')

            title = get_param_by_str('title')

            target_token = 'all'
            if _type == 'system':
                target_token = 'all'
            elif _type == 'passenger':
                target_token = 'passenger'
            elif _type == 'driver':
                target_token = 'driver'
                
            # 目前只发给司机
            target_token = 'driver'
            message = get_param_by_str('content')
            msg = {'target_token': target_token, 'data': {'flag': 'system', 'msg': message}}
            redis_conn.publish(channel, json.dumps(msg))

            db = PublicDbConnection()
            _time = get_current_time()
            sql = f"insert into ls_notice (title,content,status,created_at) values ('{title}','{message}','已发布','{_time}')"
            ret = db._execute_sql(sql)

            return echo_json(0,'success',msg)
        except Exception as e:            
            return echo_json(-1,'Redis publish failed')

@admin_route.route('/notice/json', methods=['GET'])
def notice_json():
    db = PublicDbConnection()
    sql = f"select * from ls_notice order by id desc"
    result = db._query_sql(sql)
    return echo_json(0,'success',result)

@admin_route.route('/complaint')
def complaint():
    # 投诉
    return render_template("/admin/business/complaint/index.html")

@admin_route.route('/evaluation',methods=['GET'])
def evaluation():
    # 评价
    return render_template("/admin/business/evaluation/index.html")

@admin_route.route('/evaluation/json',methods=['GET'])
def evaluation_json():
    db = PublicDbConnection()
    sql = f"select * from v_ls_driver_comment order by id desc"
    result = db._query_sql(sql)
    return echo_json(0,'success',result)

@admin_route.route('/customer',methods=['GET'])
def customer():
    # 客户
    return render_template("/admin/customer/index.html")

@admin_route.route('/customer/list/json',methods=['GET'])
def customer_list_json():
    return g._customer.get_customer_list()

@admin_route.route('/customer/update/status',methods=['POST'])
def cusomer_update_status():
    return g._customer.update_user_status()

# 用户管理
@admin_route.route('/user/list',methods=['GET','POST'])
def user_list():
    return render_template("/admin/user/list.html")

@admin_route.route('/user/add',methods=['GET','POST'])
def user_add():
    if request.method == 'GET':
        return render_template("/admin/user/add.html")
    else:
        return g._admin.add()
    
@admin_route.route('/user/myinfo',methods=['GET','POST'])
def myinfo():
    if request.method == 'GET':
        row = g._admin.get_one()
        return render_template("/admin/user/myinfo.html",row=row)
    else:
        return g._admin.update()

@admin_route.route('/user/list/json',methods=['GET'])
def user_list_json():
    return g._admin.get_user_list()

@admin_route.route('/user/reset_pwd',methods=['POST'])
def user_reset_pwd():
    return g._admin.reset_pwd()

@admin_route.route('/user/update_status',methods=['POST'])
def user_update_status():
    return g._admin.update_status()

@admin_route.route('/user/delete',methods=['POST'])
def user_delete():
    return g._admin.delete()

@admin_route.route('/user/log',methods=['GET','POST'])
def user_log():
    if request.method == 'GET':
        return render_template("/admin/sys/log.html")
    else:
        return g._admin.clear_user_log()
    
@admin_route.route('/user/log/json',methods=['GET'])
def user_log_json():
    return g._admin.user_log()

@admin_route.route('/premission',methods=['GET','POST'])
def premission_list():
    # 权限管理
    if request.method == 'GET':
        return render_template("/admin/user/premission.html")

@admin_route.route('/ad',methods=['GET','POST'])
def ad():
    # 广告管理
    if request.method == 'GET':
        row = g._admin.get_system_setup()                
        return render_template("/admin/ad/index.html",row=row)
    else:
        pass
    
################## total ######################
@admin_route.route('/total',methods=['GET'])
def admin_total():
    db = PublicDbConnection()
    # 当日订单数量
    btime,etime = get_day_time_range()
    sql = f"select count(*) as num,sum(total_fee) as fee from ls_order where status in (0,1,2,3,4,5) and order_time between '{btime}' and '{etime}'"
    ret = db._query_sql_one(sql)
    num = ret['num'] if ret else 0
    fee = ret['fee'] if ret else 0
    
    # 总订单数量
    sql = f"select count(*) as num,sum(total_fee) as fee from ls_order where status in (0,1,2,3,4,5)"
    ret = db._query_sql_one(sql)
    total_num = ret['num'] if ret else 0
    total_fee = ret['fee'] if ret else 0
    
    data = {
        'num':num,
        'fee':fee,
        'total_num':total_num,
        'total_fee':total_fee
    }
    
    # 7条订单数据
    sql = f"select sn,car_no,driver_name,driver_phone,order_time,(distance / 1000) as distance, (duration/60) as duration, status from v_order where status in (0,1,2,3,4,5) order by id desc limit 7"
    result = db._query_sql(sql)
    
    # 近7日订单量
    sql = """
    SELECT 
            DATE(created_at) AS register_date,
            COUNT(*) AS register_count
        FROM 
            v_order
        WHERE 
            created_at >= CURDATE() - INTERVAL 60 DAY
        GROUP BY 
            DATE(created_at)
        ORDER BY 
            register_date;
    """
    ret = db._query_sql(sql)
    data['day7'] = ret
    
    # 近30日司机量
    sql = """
    SELECT 
            DATE(created_at) AS register_date,
            COUNT(*) AS register_count
        FROM 
            ls_driver
        WHERE 
            created_at >= CURDATE() - INTERVAL 60 DAY
        GROUP BY 
            DATE(created_at)
        ORDER BY 
            register_date;
    """
    ret = db._query_sql(sql)
    data['day7driver'] = ret
    
    return echo_json(0,'success',result,data)

@admin_route.route('/order/send_sms',methods=['POST'])
def send_order_sms():
    """ 发送订单短信
    """
    return g._order.send_order_sms()    
@admin_route.route('/order/cancel',methods=['POST'])
def cancel_order():
    """ 取消订单
    """
    return g._order.cancel_order()