# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   wechat_controller.py
@date     :   2025/03/09 00:37:59
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   小程序端控制器基类
'''
from flask import request
import pytz,jwt,datetime
from settings import Config
from src.helper.helper import *
from src.model.wechat.wechat_user_db import WechatUserDb
from src.helper.wechat_api import WeChatMiniProgramAPI

class WechatBaseController():
    def __init__(self):
        self.wechat_db = WechatUserDb()
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

        # 解码 token
        uid = self.decode_wechat_token()
        if uid is None:
            return echo_json(-1, 'Token has expired!',code=401)
        row = self.wechat_db.get_user_by_id(uid,'id,phone,token,status')
        if row:
            if row['status'] == -1:
                return echo_json(-2, '用户已被禁用',code=401)
        else:
            return echo_json(-1, '用户不存在',code=401)            
        
        token = generate_token(row['id'])
        self._db.update_user_info(row['id'], {'token': token})
        
        return None
    
    def __get_user_by_openid(self,openid):
        '''
        根据openid获取用户信息
            Args:
                openid: openid
            Return: 
                id: 用户id
                None: 用户不存在
        '''
        if openid is None or openid == '':
            return None
        row = self.wechat_db.get_user_by_openid(openid,'id')
        if row is None:
            return None
        return row['id']
    
    def __get_user_by_phone(self,phone):
        '''
        根据phone获取用户信息
            Args:
                phone: phone
            Return: 
                id: 用户id
                None: 用户不存在
        '''
        if phone is None or phone == '':
            return None
        row = self.wechat_db.get_user_by_phone(phone,'id')
        if row is None:
            return None
        return row['id']
    def decode_wechat_token(self):
        ''' 解码token，如生成成功则返回解码后的id, 否则返回None
            注意：如果token过期返回小程序时，可在echo_json的data插入'token':token值，小程序端会自动刷新token
            Args:
                None
            Return: 
                uid: 用户ID,过期时返回None
                False: 解码失败
        '''
        import jwt
        from settings import Config
        token = get_user_token()
        phone = get_param_by_json("phone")
        if phone is None or phone == '':
            phone = get_param_by_str('phone')
            
        openid = get_param_by_json("openid")
        # get时是字符串格式
        if openid is None or openid == '':
            openid = get_param_by_str('openid')
        try:
            # 解码 token
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            # app端为无状态方式，不需要存储用户信息
            uid = data['uid']
        except jwt.ExpiredSignatureError:
            uid = self.__get_user_by_openid(openid)
            if uid is None:
                uid = self.__get_user_by_phone(phone)
                
            if uid is not None:
                return uid
            # 如果解码失败，返回 None
            uid = None
        except jwt.InvalidTokenError:
            uid = self.__get_user_by_openid(openid)
            if uid is None:
                uid = self.__get_user_by_phone(phone)
                
            if uid is not None:
                return uid            
            
            # 如果解码失败，返回 False
            uid = False
            
        return uid
    
    def is_wechat_mini_program(self):
        # 如果从小程序访问
        _from = get_param_by_str('from')
        if _from == '':
            _from = get_param_by_json('from')
            if _from == 'mini':
                return True
            
        return False
    