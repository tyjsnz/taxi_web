# -*- encoding: utf-8 -*-
'''
@file     :   qq_ocr.py
@date     :   2025/05/05 14:50:28
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   腾讯云OCR接口
https://cloud.tencent.com/document/product/866/36209
'''

from tencentcloud.common import credential
from tencentcloud.ocr.v20181119 import ocr_client, models
from settings import OCRConfig
import json

class QQOCR():
    OCR_TYPE_DRIVERLICENSE = 1
    OCR_TYPE_VEHICLELICENSE = 2

    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_ocr_result(image_url,_type,is_base64 = False):
        """ 获取OCR识别结果
            Args:
                image_url: 图片url地址
                _type: OCR类型，0：驾驶证，1：行驶证
            Return: 
                None
            @date:   2025/05/06 20:44:31
            @author: snz
        """
        
        try:            
            cred = credential.Credential(OCRConfig.secret_id,OCRConfig.secret_key)
            
            # 实例化要请求产品的client对象,clientProfile是可选的
            client = ocr_client.OcrClient(cred,"")
            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.DriverLicenseOCRRequest()
            params = {
                "ImageUrl": image_url# "https://e0.ifengimg.com/07/2018/1220/83CAB7613F6BB087D2F531C802071D3B3BA1DB61_size229_w1200_h1199.jpeg"
            }
            if is_base64:
                params = {}
                params = {
                    "ImageBase64": image_url
                }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个DriverLicenseOCRResponse的实例，与请求对象对应
            if _type == QQOCR.OCR_TYPE_DRIVERLICENSE:
                # 驾驶证
                resp = client.DriverLicenseOCR(req)
            elif _type == QQOCR.OCR_TYPE_VEHICLELICENSE:
                # 行驶证
                resp = client.VehicleLicenseOCR(req)
            elif _type == 3:
                # 身份证正面
                resp = client.IDCardOCR(req)
            elif _type == 4:
                # 身份证反面
                resp = client.IDCardOCR(req)
            else:
                return None
            
            # 输出json格式的字符串回包
            ret = resp.to_json_string()
            try:
                rets = json.loads(ret)
                if _type == QQOCR.OCR_TYPE_DRIVERLICENSE:
                    print(rets['Name'])
                    print(rets['Address'])
                    sex = 0
                    if  rets['Sex'] == '男':
                        sex = 0
                    else:
                        sex = 1
                    # 驾驶证
                    data = {
                        'no': rets['CardCode'],
                        'name': rets['Name'],
                        'sex': rets['Sex'] == '男' ,
                        'nationality': rets['Nationality'],
                        'address': rets['Address'],
                        'birth_date': rets['DateOfBirth'],
                        'issue_date': rets['DateOfFirstIssue'],
                        'license_type': rets['Class'],
                        'start_date': rets['StartDate'],
                        'end_date': rets['EndDate'],
                        'issuing_authority': rets['IssuingAuthority'],
                        'pic_front': '',
                    }
                    return data
                elif _type == QQOCR.OCR_TYPE_VEHICLELICENSE:
                    # 行驶证
                    rets = rets["FrontInfo"]
                    print(rets)
                    data = {
                        'car_no': rets['PlateNo'],
                        'car_type': rets['VehicleType'],
                        'owner': rets['Owner'],
                        'address': rets['Address'],
                        'use_character': rets['UseCharacter'],
                        'model': rets['Model'],
                        'vin': rets['Vin'],
                        'engine_number': rets['EngineNo'],
                        'file_front': '',
                    }
                    return data
            except Exception as err:
                print(err)
                return None
            
        except Exception as err:
            print(err)
            return None