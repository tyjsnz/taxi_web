# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 
'''
@file     :   dispatch_controller.py
@date     :   2025/03/09 00:47:27
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   调度员控制器，调度员端也通过小程序进入，只是小程序进入后跳转调度页，可通过webview方式来处理
'''
from flask import request
import pytz,jwt,datetime
from settings import Config
from src.helper.helper import *
from src.model.admin.user_db import UserDb

# 调度端待重新完善，目前先留空，后续完善
class DisPatchController():
    def __init__(self) -> None:
        self._db = UserDb()

    def auth_token_middleware(self,not_auth_path = []):
        ''' app端、微信小程序身份验证中间件，验证用户 token 是否有效，不同端需要放行的路由通过参数传入放行
            注意：token有效期设置为1天，过期后需要重新登录
            Args:
                not_auth_path: 白名单路径,如['/wechat/','/wehcat']
            Return: 
                验证通过返回None，验证失败返回错误信息
            @date:   2025/03/08 15:56:57
            @author: snz
        '''
        
        if request.path in not_auth_path:
            return None  # 白名单路径跳过验证

        # 前端请求时需要在header中携带Authorization头，值为token
        token = request.headers.get('Authorization')
        if not token:
            return echo_json(-1,'Token is missing!',code=401)

        try:
            # 解码 token
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            # app端为无状态方式，不需要存储用户信息
            uid = data['uid']
            row = self._db.get_user_info_by_id(uid)
            if row is None:
                return echo_json(-1,'用户不存在',code=401)
            if row['status'] == -1:
                return echo_json(-1, '用户已被禁用',code=401)
            
        except jwt.ExpiredSignatureError:
            return echo_json(-1, 'Token has expired!',code=401)
        except jwt.InvalidTokenError:
            return echo_json(-1, 'Invalid token!',code=401)

        return None

    def _generate_token(self,uid):
        ''' 生成用户token，app端应先验证用户名和密码，成功后使用用户uid换取token，
            微信小程序端应先验证openid，成功后使用用户uid换取token
            注意：token有效期设置为1天，过期后需要重新登录
            Args:
                uid: 用户ID
            Return: 
                token
            @date:   2025/03/08 16:11:09
            @author: snz
        '''
        
        # 获取当前的中国时间
        china_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.datetime.now(china_tz)
        exp_time = current_time + datetime.timedelta(days=1)  # token 有效期为 1 天

        payload = {
            'uid': uid,
            'exp': exp_time
        }
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
        return token
    
    def login(self):
        if request.method != 'POST':
            return echo_json(-1, '无效请求',code=404)
        
        username = get_param_by_str('username')
        password = get_param_by_str('password')
        if username == '' or password == '':
            return echo_json(-1, '用户名或密码为空',)
        
        password = gen_md5(password)

        row = self._db.get_user_info(username, password)
        if row is None:
            return echo_json(-1, '用户名或密码错误')
        
        if row['status'] == -1:
            return echo_json(-1, '用户已被禁用')
        
        token = self._generate_token(row['id'])
        return echo_json(0, '登录成功', {'token': token})
        