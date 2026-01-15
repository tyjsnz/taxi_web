# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

from flask import request,jsonify
import requests
import json
import base64
import os,time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from settings import Config
from src.common.const_defined import WECHAT_TEMPLATE_ID
from loguru import logger
class WeChatMiniProgramAPI:
    def __init__(self):
        self.app_id = Config.WECHAT_APPID
        self.app_secret = Config.WECHAT_SECRET_KEY
        self.token_file = 'access_token.json'
        self.access_token = self.get_access_token()

    # 解密函数
    def decrypt(self, session_key, encrypted_data, iv):
        _session_key = base64.b64decode(session_key)
        encrypted_data = base64.b64decode(encrypted_data)
        iv = base64.b64decode(iv)

        backend = default_backend()
        cipher = Cipher(algorithms.AES(_session_key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
        decrypted = self._unpad(decrypted_padded)
        return json.loads(decrypted)

    # 去除 PKCS7 填充
    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]
    
    def get_access_token(self):
        """获取access_token"""
        if self._is_token_valid():
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
                return token_data['access_token']
        
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        response = requests.get(url)
        if response.status_code == 200:
            token_data = response.json()
            token_data['expires_at'] = int(time.time()) + token_data['expires_in']
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f)
            return token_data['access_token']
        else:
            raise Exception("Failed to get access token")

    def _is_token_valid(self):
        """检查access_token是否有效"""
        if not os.path.exists(self.token_file):
            return False
        with open(self.token_file, 'r') as f:
            token_data = json.load(f)
            return token_data['expires_at'] > int(time.time())


    def get_access_token(self):
        """获取access_token"""
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            raise Exception("Failed to get access token")

    def user_auth(self, code):
        """用户认证接口"""
        url = f"https://api.weixin.qq.com/sns/jscode2session?appid={self.app_id}&secret={self.app_secret}&js_code={code}&grant_type=authorization_code"
        response = requests.get(url)
        return response.json()

    def send_template_message(self, user_openid, template_id, form_id, page, data, emphasis_keyword=None):
        """模板通知接口"""
        url = f"https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token={self.access_token}"
        payload = {
            "touser": user_openid,
            "template_id": template_id,
            "page": page,
            "form_id": form_id,
            "data": data,
            "emphasis_keyword": emphasis_keyword
        }
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), headers=headers)
        return response.json()

    def get_invoice_url(self, order_id, check_code, app_remark):
        """发票接口"""
        url = f"https://api.weixin.qq.com/card/invoice/reimburse/geturl?access_token={self.access_token}"
        payload = {
            "order_id": order_id,
            "check_code": check_code,
            "app_remark": app_remark
        }
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), headers=headers)
        return response.json()
    
    def get_user_phone_number(self):
        """获取用户手机号码"""
        data = request.get_json()
        if not data:
            return {'error': '请求数据为空'}

        session_key = data.get('session_key')
        encrypted_data = data.get('encryptedData')
        iv = data.get('iv')

        if not session_key or not encrypted_data or not iv:
            return {'error': '缺少必要参数'}

        try:
            logger.info(f"session_key: {session_key}, encrypted_data: {encrypted_data}, iv: {iv}")
            decrypted_data = self.decrypt(session_key, encrypted_data, iv)
            logger.info(f"解密后的数据：{decrypted_data}")
            phone_number = decrypted_data.get('phoneNumber')
            if not phone_number:
                return {'error': '解密后未找到手机号码'}
            return {'phoneNumber': phone_number}
        except Exception as e:
            logger.error(f"解密失败，错误信息：{str(e)}")
            return {'error': f'解密失败，错误信息：{str(e)}'}
    
    def wx_login(self):
        code = request.args.get('code')
        if not code:
            return {"error": "Missing code parameter"}

        params = {
            'appid': self.app_id,
            'secret': self.app_secret,
            'js_code': code,
            'grant_type': 'authorization_code'
        }

        try:
            response = requests.get('https://api.weixin.qq.com/sns/jscode2session', params=params)
            response.raise_for_status()
            data = response.json()

            if 'errcode' in data:
                return {"error": f"WeChat API error: {data['errmsg']}"}

            openid = data.get('openid')
            session_key = data.get('session_key')

            if not openid or not session_key:
                return {"error": "Failed to get openid or session_key"}

            return {
                "openid": openid,
                "session_key": session_key
            }
        except requests.RequestException as e:
            return {"error": f"Request error: {str(e)}"}
        
    def send_accept_order_subscribe_message(self,openid,order_info):
        """ 发送订阅消息
        Args:
            
        Return:
            None
        @date:   2025/04/10 16:25:27
        @author: snz
            
        """
        try:
            #data = request.get_json()
            
            # 这里应该从数据库获取订单详细信息
            #order_info = get_order_info_from_db(order_id)  # 实现这个函数
            
            access_token = self.get_wx_access_token()
            if not access_token:
                return jsonify({'code': -1, 'msg': '获取access_token失败'})
            
            url = f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}'
            
            # 构建消息内容
            msg_data = {
                "touser": openid,
                "template_id": WECHAT_TEMPLATE_ID.DRIVER_ACCEPT_ORDER,
                "page": f"pages/order/detail?order_id",  # 点击消息跳转的页面
                "data": {
                    "thing5": {  # 车牌号
                        "value": order_info.get('plate_number', '')
                    },
                    "thing3": {  # 车辆信息
                        "value": order_info.get('car_info', '')
                    },
                    "thing4": {  # 上车地点
                        "value": order_info.get('pickup_location', '')
                    },
                    "date10": {  # 预约出发时间
                        "value": order_info.get('departure_time', '')
                    }
                }
            }
            
            response = requests.post(url, json=msg_data)
            result = response.json()
            
            if result.get('errcode') == 0:
                return jsonify({'code': 0, 'msg': '发送成功'})
            else:
                return jsonify({'code': -1, 'msg': f"发送失败: {result.get('errmsg')}"})
        
        except Exception as e:
            return jsonify({'code': -1, 'msg': f'服务器错误: {str(e)}'})

    def send_payok_subscribe_message(self,openid,order_info):
        """ 发送订阅消息
        Args:
            
        Return:
            None
        @date:   2025/04/10 16:25:27
        @author: snz
            
        """
        try:
            #data = request.get_json()
            
            # 这里应该从数据库获取订单详细信息
            #order_info = get_order_info_from_db(order_id)  # 实现这个函数
            
            access_token = self.get_wx_access_token()
            if not access_token:
                return jsonify({'code': -1, 'msg': '获取access_token失败'})
            
            url = f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}'
            
            # 构建消息内容
            msg_data = {
                "touser": openid,
                "template_id": WECHAT_TEMPLATE_ID.ORDER_PAY,
                "page": f"pages/order/detail?order_id",  # 点击消息跳转的页面
                "data": {
                    "data1": {  # 支付时间
                        "value": order_info.get('plate_number', '')
                    },
                    "amount2": {  # 支付金额
                        "value": order_info.get('car_info', '')
                    },
                    "thing3": {  # 上车地点
                        "value": order_info.get('pickup_location', '')
                    },
                    "thing4": {  # 下车地点
                        "value": order_info.get('pickup_location', '')
                    },
                    "car_number8": {  # 车牌信息
                        "value": order_info.get('departure_time', '')
                    }
                }
            }
            
            response = requests.post(url, json=msg_data)
            result = response.json()
            
            if result.get('errcode') == 0:
                return jsonify({'code': 0, 'msg': '发送成功'})
            else:
                return jsonify({'code': -1, 'msg': f"发送失败: {result.get('errmsg')}"})
        
        except Exception as e:
            return jsonify({'code': -1, 'msg': f'服务器错误: {str(e)}'})