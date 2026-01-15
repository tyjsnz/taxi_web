# -*- coding: utf8 -*-
'''
@file     :   face_client.py
@date     :   2025/05/08 19:09:09
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   人脸识别接口
    https://cloud.tencent.com/document/product/1007/102203?from=console_document_search
'''


import json

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.faceid.v20180301 import faceid_client, models
import base64
from loguru import logger
from src.helper.helper import float_ex
from settings import OCRConfig
def face_verification(_idcard,_name, _img_path):
    try:
        # 配置凭证
        cred = credential.Credential(OCRConfig.secret_id, OCRConfig.secret_key)
        
        # 配置HTTP和客户端
        http_profile = HttpProfile()
        http_profile.endpoint = "faceid.tencentcloudapi.com"
        
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        
        # 创建 FaceidClient 实例
        client = faceid_client.FaceidClient(cred, "ap-guangzhou", client_profile)
        
        # 读取图片并转换为Base64
        with open(_img_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        
        # 创建请求对象
        req = models.ImageRecognitionV2Request()
        
        # 设置请求参数
        params = {
            "IdCard": _idcard,
            "Name": _name,
            "ImageBase64": image_base64,
            "Extra": "face_id"
        }
        
        # 对于V2版本，建议使用from_json_string方式
        req.from_json_string(json.dumps(params))
        
        # 发送请求
        # {"Sim": 98.76, "Result": "Success", "Description": "成功", "Extra": "121", "RequestId": "f4c5f5fb-394c-4be0-8025-4ffcf9f3fb79"}
        resp = client.ImageRecognitionV2(req)
        resp = resp.to_json_string()
        ret = json.loads(resp)
        sim = float_ex(ret['Sim'])
        result = ret['Result']
        desc = ret['Description']
        extra = ret['Extra']
        requestId = ret['RequestId']        
        print(ret)
        if sim >= 70:
            return True
        
        return False
    except TencentCloudSDKException as err:
        print(err)
        logger.error(err)
        return False