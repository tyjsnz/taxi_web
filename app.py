# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

from flask import Flask, request, abort, jsonify, session, g, current_app
from flask_cors import CORS
from settings import Config
from flask_session import Session
from flask_sock import Sock, Server

from urllib import parse
from os import urandom
from src.helper.helper import *
from src.routes.admin.admin_route import admin_route

from src.routes.app.driver.driver_route import driver_route as app_driver_route
from src.routes.app.dispatch.dispatch_route import dispatch_route
from src.routes.wechat.wechat_route import wechat_route
from src.routes.app.driver.driver_web_route import driver_web_route
from src.routes.wechat.pay.yeepay_route import yeepay_route
from src.routes.admin.company.company_route import company_route
from src.routes.admin.finance.finance_route import finance_route
from src.routes.admin.driver.driver_route import admin_driver_route
from src.routes.admin.route.route_route import route_route
from datetime import datetime, timedelta
import time
import json
from loguru import logger
from src.common.websocket_manager import send_message_to_target_client,send_test

from src.model.base_db import PublicDbConnection
from src.service.SchedulerTaskController import start_scheduler


app = Flask(__name__)
sock = Sock(app)
# 加载配置
app.config.from_object(Config)


if not Config.APP_DEBUG:
    Session(app)

CORS(app, supports_credentials=True)

log_file_name = time.strftime("%Y-%m-%d_%H", time.localtime())
# 日志文件保存10天日志，最大存储500M
logger.add(f"./log/runtime_{log_file_name}.log",
           retention="7 days", rotation="100 MB")

# 开启设置有效期，默认为31天后过期
# session.permanent = True

# 设置session 1小时后过期
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=12)

# 注册 login_controller中蓝图
app.register_blueprint(admin_route, url_prefix="/admin")
app.register_blueprint(admin_driver_route, url_prefix="/admin/driver")
app.register_blueprint(company_route, url_prefix="/admin/company")
app.register_blueprint(finance_route, url_prefix="/admin/finance")
app.register_blueprint(route_route, url_prefix="/admin/route")

app.register_blueprint(app_driver_route, url_prefix="/app/api/driver/v1")
app.register_blueprint(dispatch_route, url_prefix="/app/api/dispatch/v1")
app.register_blueprint(wechat_route, url_prefix="/wechat/api/v1")
app.register_blueprint(yeepay_route, url_prefix="/wechat/pay/yeepay")

app.register_blueprint(driver_web_route, url_prefix="/app/driver")

@app.before_request
def initialize_app_context():
    # 使用应用上下文来存储信息，current_app为flask的全局上下文，故整个生命周期均有效，其它地方引入current_app即可访问
    # 不同于g变量在每个请求结束后其实就已经被销毁,只能web用
    if not hasattr(current_app, "last_settings_load_time"):
        current_app.last_settings_load_time = None
    if not hasattr(current_app, "driver_config"):
        current_app.driver_config = None
    if not hasattr(current_app, "customer_config"):
        current_app.customer_config = None
    if not hasattr(current_app, "site_config"):
        current_app.site_config = None

@app.before_request
def load_settings():
    # 加载系统配置，司机端，乘客端，在其余地方可引用current_app后可直接访问
    current_time = datetime.now()
    if (
        current_app.last_settings_load_time is None
        or current_time - current_app.last_settings_load_time > timedelta(minutes=10)
    ):
        db = PublicDbConnection()
        row = db._query_sql_one(
            f"select * from ls_sys_config limit 1", use_cache=False)
        if row:
            if row["driver_config"]:
                row["driver_config"] = json.loads(row["driver_config"])
            if row["customer_config"]:
                row["customer_config"] = json.loads(row["customer_config"])
            if row["site_config"]:
                row["site_config"] = json.loads(row["site_config"])

            current_app.customer_config = row["customer_config"]
            current_app.driver_config = row["driver_config"]
            current_app.site_config = row["site_config"]

            current_app.last_settings_load_time = current_time


@app.before_request
def log_admin_post_requests():
    # 检查是否为 POST 请求且 URL 包含 /admin
    if request.method == "POST" and "/admin" in request.path:
        # 获取用户ID
        uid = session.get("uid")
        if uid is None:
            uid = 0  # 如果没有用户ID，默认为0或其他适当的值

        # 获取请求的来路链接
        referer = request.headers.get("Referer", "")

        # 获取客户端IP
        client_ip = request.remote_addr

        # 获取当前时间
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 记录内容
        content = f"POST request to {request.path} with Referer: {referer}"

        # 创建数据库连接
        db = PublicDbConnection()

        # 插入记录到 ls_user_log 表
        sql = f"""
            INSERT INTO ls_user_log (uid, content, ip, created_at)
            VALUES ({uid}, '{content}', '{client_ip}', '{created_at}')
        """
        try:
            db._execute_sql(sql)
        except Exception as e:
            logger.error(f"Failed to log admin POST request: {e}")

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

@app.route("/api/get_region", methods=['GET'])
def get_region():
    # 通用获取地区
    db = PublicDbConnection()
    result = db._query_sql("select * from ls_region order by letter asc")
    return echo_json(0, 'success', result)

@app.route("/api/region_is_allow", methods=['GET'])
def region_is_allow():
    # 检查地区是否允许
    region_id = get_param_by_str('region_id')
    sarr = region_id.split('#')
    province = ''
    city = ''
    district = ''
    street = ''
    if len(sarr) >= 3:
        province = sarr[0]
        city = sarr[1]
        district = sarr[2]
        if len(sarr) >= 4:
            street = sarr[3]

    db = PublicDbConnection()
    result = db._query_sql_one(f"select id from ls_company where region like '%{city}%' or address like '%{district}%'")
    if result:
        return echo_json(0, 'success')
    else:
        return echo_json(-1, '当前地区未开通')

@app.route("/check_update", methods=["POST", "GET"])
def check_update():
    data = {
        "versionCode": 200,
        "versionName": "2.0.0",
        "downloadUrl": "http://192.168.3.198:8002/static/app-release.apk",
        "description": "1. 新增订单自动接单功能\n2. 优化导航性能\n3. 修复已知问题",
        "forceUpdate": False,
    }
    return jsonify(data)


@app.route("/app/app_error_report", methods=["POST"])
def app_error_report():
    _time = get_param_by_json('timestamp')
    _tag = get_param_by_json('tag')
    _msg = get_param_by_json('message')
    logger.error(f"app_report：{_time} {_tag} {_msg}")
    return echo_json(0, 'ok')

if __name__ == "__main__":
    logger.info("启动 app，port=8002")
    # 启动优惠券检测线程，现已经放到定时任务中，service/SchedulerTaskController.py 进行启动
    #start_scheduler()

    app.run(debug=True, port=8002, host="0.0.0.0")