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
@desc     :   小程序端控制器
'''
from flask import request
import pytz,jwt,datetime
from settings import Config
from src.helper.helper import *
from src.controller.web.wechat.wechat_base_controller import WechatBaseController
from src.model.wechat.wechat_user_db import WechatUserDb
from src.model.wechat.order_db import OrderDb
from src.helper.wechat_api import WeChatMiniProgramAPI
import json

class WechatController(WechatBaseController):
    
    def __init__(self):
        super().__init__()
        self._user = WechatUserDb()
        self._db = self.wechat_db        
        self.wechat_api = WeChatMiniProgramAPI()
        self.order = OrderDb()
    def wx_login(self,is_wx_login=True):
        """微信登录，换取openid,session_key,unionid，及用户的token,
            Args:
                is_wx_login: 是否是微信登录，默认是,false为微信每次登录后获取用户信息，这时不处理微信登录请求
        """    
        openid = ''
        session_key = ''
        token = get_user_token()
        
        if is_wx_login:
            # 微信登录
            _response = self.wechat_api.wx_login()
            
            # 有错误信息，直接返回
            if 'error' in _response:
                return echo_json(-1,_response['error'])

            # 保存用户信息
            openid = _response['openid']
            session_key = _response['session_key']
        else:
            openid = get_param_by_str('openid')            
            
        if openid == '' or openid == None:
            return echo_json(-1, 'openid不能为空')

        # 取配置  # 全局取到的配置参数,app中，用于乘客订单参数，如先付后乘
        customer_config = get_current_customer_config()
        site_config = get_current_site_config()
                                
        row = self._db.get_user_info(openid,"id,phone,status")
        if row is None:
            # 插入用户信息
            data = {
                'openid': openid,
                'token': '',
                'created_at': get_current_time(),
                'last_time': get_current_time(),
                'last_ip': get_real_ip(),
            }
            user_id = self._db.insert_user(data)
            if user_id is None:
                return echo_json(-1, '用户信息插入失败',data)
            
            # 用户信息
            row = self._db.get_user_by_id(user_id,'id,phone,status')
            
            # 生成token,是微信登录且token为空才生成,否则认定为参数获取模式，此时token有值
            if is_wx_login and token == '':
                token = generate_token(user_id)

            self._db.update_user_info(user_id, {'token': token})
            
            phone = ''
            if row['phone']:
                phone = row['phone']
          
                      
            if site_config and "ad_img" in site_config:
                if "http" not in site_config['ad_img']:
                    site_config['ad_img'] = Config.WEB_URL + site_config['ad_img']
                    
            return echo_json(0, '登录成功', {'token': token,'openid': openid, 'session_key': session_key, 'user_info': row,'phone': phone,'config_params': customer_config,'site_config': site_config,'is_new_user': 1,'no_pay_order': None})
        else:
            # 这里不返回401，因为客户端要提示
            if row['status'] == -1:
                return echo_json(-2, '用户已被禁用',code=200)
            
            # 生成token,是微信登录且token为空才生成,否则认定为参数获取模式，此时token有值
            if is_wx_login and token == '':
                token = generate_token(row['id'])
                data = {'token': token,'last_time': get_current_time(),'last_ip': get_real_ip()}
                self._db.update_user_info(row['id'], data)

            phone = ''
            if row['phone']:
                phone = row['phone']
                
            # 查看是否用户有未支付的订单
            no_pay_order = self.order.get_nopay_order_list(row['id'],"id")

            # web配置中并不加url，回到小程序时要加上url
            if site_config and "ad_img" in site_config:
                if "http" not in site_config['ad_img']:
                    site_config['ad_img'] = "https://xxx.net" + site_config['ad_img']
            return echo_json(0, '登录成功', {'token': token,'openid': openid, 'session_key': session_key, 'phone': phone, 'user_info': row,'config_params': customer_config,'site_config': site_config,'is_new_user': 0, 'no_pay_order':no_pay_order})

    def get_params(self):
        ''' 获取参数
            Args:
                : 
            Return: 
                None
            @date:   2025/03/18 15:21:58
            @author: snz
        '''
        return self.wx_login(False)
                
    def refresh_token(self):
        ''' 刷新token
            Args:
                : 
            Return: 
                None
            @date:   2025/03/18 15:21:58
            @author: snz
        '''
        openid = get_param_by_json('openid')
        if openid is None:
            return echo_json(-1, 'openid不能为空')
        
        row = self._db.get_user_info(openid)
        if row is None:
            return echo_json(-1, '用户不存在')
        
        # 生成token
        token = generate_token(row['id'])
        # 更新用户token
        self._db.update_user_info(row['id'], {'token': token})

        return echo_json(0, '刷新成功', {'token': token})

    def get_phone(self):
        ''' 获取用户手机号
            Args:
                : 
            Return: 
                None
            @date:   2025/03/18 15:21:58
            @author: snz
        '''
        result = self.wechat_api.get_user_phone_number()
        if 'error' in result:
            return echo_json(-1,result['error'])
        
        phone_number = result['phoneNumber']
        if phone_number is None:
            return echo_json(-1, '获取失败')
        
        uid = self.decode_wechat_token()

        self._db.update_user_info(uid,{'phone':phone_number})

        return echo_json(0, '获取成功',{'phone':phone_number})
    
    def subscribe_tpl(self):
        ''' 小程序端用户订阅的模板消息
            Args:
                : 
            Return: 
                None
            @date:   2025/04/26 16:01:55
            @author: snz
            'UcERJiF-4ifrFHFxuptqQKiK4K0MmXUYi-A5uPN3a5I', // 司机接单提醒
				'Fs4vSXVa-3W2da_fim93QrfbUtH-WholPeYmO_JPTm0', // 支付成功通知
				'2HAdShuPMoiF3uVh7lxzZ7CSWv2fBcHE4MDwz1Saics', // 打车服务动态
        '''
        uid = 0
        uid = self.decode_wechat_token()
        if uid is None:
            return echo_json(-1, "token过期或无效")
                
        tpl_ids = get_param_by_json('tpl_id')
        if tpl_ids is None:
            return echo_json(-1, '模板ID不能为空')
        ids = tpl_ids.split(',')
        if len(ids) == 0:
            return echo_json(-1, '模板ID不能为空')
        
        self.wechat_db.update_user_info(uid,{'tpls':tpl_ids})
        return echo_json(0, '订阅成功')
    
    def member_emergency(self):
        """小程序紧急联系人列表
        """
        flag = get_param_by_str('type')
        uid = get_param_by_str('uid')
        name = get_param_by_str('name')
        phone = get_param_by_str('phone')
        openid = get_param_by_str('openid')
        id = get_param_by_int('id')
        
        if flag == 'add':
            sql = f"insert into ls_wechat_emergency(uid,name,phone,openid) values({uid},'{name}','{phone}','{openid}')"
            ret = self._db._execute_sql(sql)
            return echo_json(0,'success',ret)
        elif flag == 'edit':
            sql = f"update ls_wechat_emergency set name='{name}',phone='{phone}' where id={id}"
            ret = self._db._execute_sql(sql)
            return echo_json(0,'success',ret)

    def get_member_emergency(self,uid):
        """小程序获取紧急联系人列表
        """
        sql = f"select * from ls_wechat_emergency where uid = {uid}"
        result = self._db._query_sql(sql)
        return result
    
    def delete_account(self):
        # 注销用户
        uid = self.decode_wechat_token()
        if uid is None:
            return echo_json(-1, "token过期或无效")
        
        sql = f"delete from ls_wechat_user where id = {uid}"
        self._db._execute_sql(sql)
        return echo_json(0, "success")