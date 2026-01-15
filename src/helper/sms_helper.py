# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
# see: https://api.aliyun.com/api-tools/demo/Dysmsapi/db7e1211-14e0-4b7b-9011-037dfb85d42e
# pip install alibabacloud_dysmsapi20170525==3.1.0
import sys

from typing import List

from alibabacloud_dysmsapi20170525.client import Client as DysmsapiClient
from alibabacloud_tea_openapi import models as open_api_models

from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
from alibabacloud_tea_util.client import Client as UtilClient
from settings import Config
import json
import secrets

"""
短信发送
"""
class SmsHelper:    
    def __init__(self):
        pass

    @staticmethod
    def __create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> DysmsapiClient:
        """
        使用AK&SK初始化账号Client
        """
        config = open_api_models.Config()
        config.access_key_id = access_key_id
        config.access_key_secret = access_key_secret
        return DysmsapiClient(config)

    @staticmethod    
    def generate_sms_code():
        """
        安全地生成一个5位数的手机验证码
        """
        return secrets.randbelow(90000) + 10000
    @staticmethod
    def SendSms(phone,code):
        """ 短信验证码发送
            Args:
                phone: 手机号码
                code: 验证码
            Returns:
                {'code': 0,'msg': 'ok','bizId': biz_id}
        """
        client = SmsHelper.__create_client(Config.SMS_ACCESS_KEY_ID, Config.SMS_ACCESS_KEY_SECRET)
        # EnvClient.get_env('ACCESS_KEY_ID'), EnvClient.get_env('ACCESS_KEY_SECRET'))
        # 1.发送短信
        # param = json.dumps({'no': code}) #模板:SMS_119415008
        param = json.dumps({'code': code}) #模板:SMS_120406557
        send_req = dysmsapi_models.SendSmsRequest(
            phone_numbers = phone,
            sign_name = '昆明霖尚科技', # 申请的短信签名
            template_code = 'SMS_120406557', 
            template_param = param
        )
        send_resp = client.send_sms(send_req)
        code = send_resp.body.code
        if not UtilClient.equal_string(code, 'OK'):
            print(f'错误信息: {send_resp.body.message}')
            return {'code': -1,'msg': send_resp.body.message}
        biz_id = send_resp.body.biz_id
        return {'code': 0,'msg': 'ok','bizId': biz_id}
    
    @staticmethod
    def SendOrderSms(phone,code):
        """ 订单催收短信发送
            Args:
                phone: 手机号码
                msg: 短信内容
            Returns:
                {'code': 0,'msg': 'ok','bizId': biz_id}
        """
        
        return {'code': -1,'msg': '需要申请短信模板','bizId': 0}
        

if __name__ == '__main__':
    SmsHelper.SendSms('13888888888',9876)
    