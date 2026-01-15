#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   auth_middleware.py
@date     :   2025/03/02 16:17:13
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   用户身份验证中间件
              在蓝图中使用 before_request 注册中间件：
'''

from flask import session, redirect, url_for, request, jsonify
import jwt
import datetime
from settings import Config
import pytz
from src.helper.helper import *
from src.model.driving.driver_db import DriverDb
from src.model.wechat.wechat_user_db import WechatUserDb

__SECRET_KEY = Config.SECRET_KEY  # 安全密钥