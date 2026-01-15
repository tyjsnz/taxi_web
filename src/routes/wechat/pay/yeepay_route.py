# -*- coding: utf-8 -*-
'''
@file    :   yeepay_route.py
@date    :   2025/04/10 13:01:05
@author  :   snz
@version :   1.0
@email   :   274043505@qq.com
@copyright:   Copyright (C) kmlskj All Rights Reserved.
@desc    :   易宝支付路由

'''

from flask import Blueprint, request, render_template,url_for,flash,g,Response
from src.helper.helper import *
from src.controller.web.wechat.wechat_controller import WechatController
from urllib.parse import urlparse
from settings import YEEPAYConfig,Config
from src.controller.web.wechat.order_controller import OrderController
from src.common.const_defined import ORDER_TYPE
import hashlib,time,requests
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64
import sys
import json

# 添加路径到sys.path
#sys.path.append(r'C:\ProgramData\anaconda3\envs\cxtravel\Lib\site-packages\yop_python_sdk')
#sys.path.append(r'C:\ProgramData\miniconda3\envs\cxtravel\Lib\site-packages\yop_python_sdk')
#sys.path.append('/www/server/pyporject_evn/cx_travel_venv/lib/python3.10/site-packages/yop_python_sdk')
sys.path.append(YEEPAYConfig.sdk_path)

from client.yopclient import YopClient  # Adjusted the import path to match the project structure
from client.yop_client_config import YopClientConfig

### test
import utils.yop_security_utils as yop_security_utils
from security.encryptor.rsaencryptor import RsaEncryptor
clientConfig = YopClientConfig(config_file='config/yop_sdk_config_rsa_prod.json')

# 私钥和公钥
isv_private_key = yop_security_utils.parse_rsa_pri_key(
    'MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCOdZ5mvQArWmmN72H90i836u01CSiVcyGtuOwZxvlZVvcx/Wmt83rsHIQSRQdGU/dO2xTtP4+sFn9+TKqqFT+B/fiwfLxKLAduKQC22XNekxbRx/8ygXrk1L0ZPDKXU5Oy/rJ//enHMg9NQ1zylOT++9tP9Wtfo5hMM6H85H9QarO9cOA1bdgip7EelibEeSXeri2SFWGQin8oIylN/hr/HGjNrz7wV47MR1JKNvZr88KKQj1RrF7uiM8Dgfkz5uPct2NDu/4TfqI4YqpICQpFnhc8n74umUltxPzhl+kIyZ0avpGAe2eKYPTB7XGOltIfosbIE2yPpVj5qjIiIBStAgMBAAECggEAGOr/WjKYbzzZBjPXNM25JyN/Or3fnKZ+/1M/bvHUBxm0Usjj3YKfX2HMgyKSV22T7jXZZvctcvkbc1THLElbqqnpADvNNn8VjKH85z7JVINPZEHChEvMGm8QpXOXWMtMZCxzPfqEk+xQa2ALR74eAPC+R3Hixl+H4dpNLP4tu7uvUttxLyPKZsGn3QI9AiSPNJk3nqLwx42T0De2aX6rqQ0N/MDjxW2Ax7Ya08jgNLlJGSff8JbnqP8cL4dW9pC62hZOTUWFcHMcDlVys6rDYMBloRWBDvO2m+BzNcAq9/ONsmrdyTKbIOsQZys+i/3jnS/95Rs6VYmnOg3oMBZdSQKBgQDIX9TBTHVbCBM5UUyoeAQHcQEHz7TJlVWh/n1elsf8zmG0oPIunSN4fLjVcvdHi96o2q3of1B+Dgt4o2P5dQlDIZr0coN9sIatgHU7rYsPvnHyON1l1Ccnz74BQOlX5Gm/sCJAEhKcdpB5dSAgfYDwEcShhfI1KFW4n+ig+y475QKBgQC2Aeb0hBuQ7Z+3FQs7Dxezb84jdO2DD8tgACul/FVaB7vTPNN5PvVwymXKuKvgnj9HW0l4t0uy3+zduPLb4GStpgrr2o3PwBwSls8FNDSmVF8jJ+xZUIeiyl9IW1OHwRoDDt5OKH6/7t3yRn7WHIEXlqIyyho3cqf2EXmP/bC5KQKBgDoJN7A9Gwig0CCb4Z4yFMiq/Gdsy6pPbJwc/+bzuT0J8dbFfx/tN6bgSRDZ2bGJW5aAsDpVFdVM8BmjCYPpWCNvilgfCuLOzFNYj5wXad3HhW1o9wdVaXnoe9oVGQDyEYcJ1wHDukxDMxlayVFfyIbAPrmh+ENZSWrONizaU8vZAoGATc+OX2bDKjiMmYbjoEIZjdr0s+/fQrLT7ZzlDDdOfgjkYbCVcDZcU/YTgpFk2ciNoQID7RnfwP8+kqPpH9tU73AXJzHugqzM052pr73b7GgRrEP7JUvqUMxX4+U3VshVSI1ouN1TItcKB/PfccYJ4n3BphkFEENyTx61a7u3e9ECgYEAuhjH6YjNCbQ9q5XlDLZ7jaXYIFKndvqWXcgyV02Pp4ypcvNKBBWULUdMxL6o+E3VAPSy+jxdug2TTVE+LUTUfHZR9e1bZhxIa8aMd9HZpCJjqEylNiqA/X149ErVvK4YGiwqT2SgfrZZ3C5IxeBjTZzBLsDXzDZG0caRIEbvPTE='
)
isv_public_key = yop_security_utils.parse_rsa_pub_key(
    'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA6p0XWjscY+gsyqKRhw9MeLsEmhFdBRhT2emOck/F1Omw38ZWhJxh9kDfs5HzFJMrVozgU+SJFDONxs8UB0wMILKRmqfLcfClG9MyCNuJkkfm0HFQv1hRGdOvZPXj3Bckuwa7FrEXBRYUhK7vJ40afumspthmse6bs6mZxNn/mALZ2X07uznOrrc2rk41Y2HftduxZw6T4EmtWuN2x4CZ8gwSyPAW5ZzZJLQ6tZDojBK4GZTAGhnn3bg5bBsBlw2+FLkCQBuDsJVsFPiGh/b6K/+zGTvWyUcu+LUj2MejYQELDO3i2vQXVDk7lVi2/TcUYefvIcssnzsfCfjaorxsuwIDAQAB'
)
## end test

client = YopClient(YopClientConfig('config/yop_sdk_config_rsa_prod.json'))
#client = YopClient()


yeepay_route = Blueprint('yeepay_route',__name__)

@yeepay_route.before_request
def create_controller():
    # 使用g变量来存储控制器实例
    g.wx_order = OrderController()
    g.wxapp = WechatController()
    
@yeepay_route.teardown_request
def teardown_request(exception=None):
    """ 执行完成均会调用，可以作些清理工作"""
    if exception is not None:
        write_logger(str(exception))
@yeepay_route.before_request
def before_request_func():
    """验证中间件"""
    if Config.APP_DEBUG:
        pass
    else:
        auth_response = g.wxapp.auth_token_middleware(['/wechat/pay/yeepay/notify','/wechat/pay/yeepay/success','/wechat/pay/yeepay/create_order'])
        if auth_response:
            return auth_response
   
    
# https://app.apifox.com/project/3155515/apis/api-272063193-run?branchId=1505116
@yeepay_route.route('/create_order', methods=['POST'])
def create_pay_order():
    """创建支付订单"""
    
    is_test = False
    if is_test:
        data = {'response': 'f60tHMtcfB8gXOVLq0qiuysEf4oUzO-Lqm1S7g9HEYjsP_RTBZdLGKUqlBBcO1E_dC6fMiwnfLICWfNDAngHYJIIheSQor2zwtioQsW34Vnc67dcnf2-NywWgdJk74RaFgvzF6wTJENh481xNKAueBJxPZy2ooWXYiVJUkO8liJY98clMJQXroezkWFhi1q-lFNym8P52TecpE_IVPGgDLUU9057fMQPjdjOPZEmInD-L6uU712bsOSyVMKQ2OFFMEK4PzYEGsDCOgM5eFvavV7BwLtIpyAEzSjPaO59ZufM_dOQVIgnvWJA4sNtR9oa6g8zB84PlUYBwAMjE5rMeg$1i1vfjcbl4WpLeQC1E8Q_awBLQjo9ZYTeSaMPJj61lHPb-4qtPLVuwKckywqjeWI51FLJJpSSJlMQVr3Qu9ZxV4svjfXAo69pFUkuEzW7U3tzsmKgqfTvjzqiAO7kDqdjLmwGfoxPn2XooNVbdkCuZwGr_PRbNotuxIuCPmjisTztJu_0MZBqeeCZEoU4R76QW5qmKpNKqHowWcTQ54ImYERB5oYbJkJqAxNQfIqDFybkfX_9j7e_KQlQB9qU_uqyQdKbIENSFDbtCyPCF0hzJe3GKO-wyYuSXwr4sVOSREVycM-ELWiHvGg4zlZZNAZI3s3mxOIPzQ-VxS6JJLLMokDw8Q_scOMWwp0coAITEWtxgoJ494-Aw0Q_HL4id5nmNMJW0xa2wkn3wexKOgrD6g3Fcf5jWv6Gv8ieFjmRoGvV-d31yMg-F-ZA1bHcreMjhhN9td8FtuUYE4qgksfaIXXvYSjY3reKNj5hTiW19mUuJ8qSMt60r76cR2fVDlYvILiliM1q1rz2NmFB6I7lEfmA-RR6l0shwPUmNYxsAMMIrJfs4naXeCzpVcJVyXoEtr3ngEOeaNMex_9pxd-fE7UPXI1ZizeclNWJFF9878RjETjnYmr21kxaxZnbjhS86G4MvIgsm_FPNvrHBM99Ar52pmwLLW7hbc2kokXRlNug6HIkSAlX69YtN0O2MxhhkPLx3RDGSdP2QIj-CAXlNz_rtLKwZ4BR_DEFGzxAj7jVN7Ql_wOdgryWbsuGKTjc_x_os9vfFiPFf8ExtmLVFNPdT1-r6POyn-n_HL2coidrUh45P3CdjhMIpkQl3L_j3rtkAeOqXF4h7-GegbZ4g1JXN0_Zha0UOjgUtRolXQR_zHxtjy02Q5MNw2z90iUC0uF-49biw1DnTcP0ZaA0dpyyw3vT8bKTW91H9w2jr5nCIUgoJxk4DbfTM5G_JJxkDyz67LVIC7MDI2__SpDoBWrAeAibmvB0Bqso8ZH-kDnlOh_10C53EGVYvavXV2g7gUf0byIUlk6QZyY_s9NnylGNtpFH2i0KuwJ2FSzcCPmQAZSe8Iy-UaUTIEK4YC7j9Ri_M8hHG6Q020s9mc0KPVz9F-t3SeVY_07C3jssiEG0quhe_XgnGqox1flMzm7SbabQcNOTNDGPkw8mwPZCy3HkPfd0wlEgP3O-j0d0hNrfFkCXUmRhffaF4B79DPTnJbGlGWyNBsgHclSoI-SF7MZVPyoG2Hus28-KYYuIvxLe_c3ADQhKA_voF1gH_Sz1C28_o6R2uafByJkjHGWKx3bVvk71Vi5AwGFU5nz5vD_loQCJJUTdBbv0RVFvzh1afTTmzKZVkovOb9flDJiXFUk6fd3emZi91J9KWIpS_SRXDaSZEcZD--veVkWGdiYtOnEFoUlSkMHE0VHViff9fuLliCKOnoWYXIjwyISOqHQntxLsZqgnLmi7LVQ4fLCnwkFgZzJnXrQ2H34olotFgdohhgQJB_zO44vlFVl7RUVuSkWzpXXnN3ZxffLB8bQFlggoYP9x6P_F3Dq_t7z1jZJxphRhngejw6RFkeXjBT9ZBXIRKRRPdJ8Rkl6UgmDe9X2uZDEGQ6Xvr-sCDCx9w$AES$SHA256', 'customerIdentification': 'app_10091171421'}
        response = data["response"]
        appKey = data["customerIdentification"]
        key = base64_decode(response)
        verify_sign(client,response)
        return response
        
    
    try:
        order_sn = ''
        pay_amount = 0
        openid = ''
        
        # flag = old_order_pay时为客户未付订单重新支付，这时直接用传入的参数支付即可，因为订单已经存在
        flag = get_param_by_json('flag')
        order_id = get_param_by_json('order_id')
        
        # 原来未付订单现在回来付时只有order_id,sn,pay_amount,flag
        if flag == 'old_order_pay':
            openid = get_param_by_json('openid')
            order_sn = get_param_by_json('sn')
            pay_amount = get_param_by_json('pay_amount')
            
            sn = g.wx_order.get_order_sn_by_id(order_id)
            if sn == '':        
                return jsonify({'status': -1, 'msg': '订单不存在'})
            order_sn = sn
        else:
            # 如果是先付后用，则这时订单还没有产生，所以要创建订单
            need_after_pay = int_ex(get_param_by_json('need_after_pay')) # 先付后用(1), 先用后付(0)
            
            if need_after_pay == ORDER_TYPE.PAY_AFTER_USE:
                # 查看之前此订单是否已经存在，不存在则创建
                sn = g.wx_order.get_order_sn_by_id(order_id)
                if sn == '':            
                    # 先付后用，创建订单
                    ret_json = g.wx_order.create_order()
                    
                    # 确保 response 是 Flask 的 Response 对象
                    if not isinstance(ret_json, Response):
                        return jsonify({'status': -1, 'msg': '创建订单失败1'})
                    
                    # 提取响应数据 (JSON 字符串)
                    json_data = ret_json.get_data(as_text=True)
                    ret_json = json.loads(json_data)
                    if ret_json['status'] == -1:
                        return jsonify({'status': -1, 'msg': '创建订单失败2'})
                    
                    order_id = ret_json['data']['order_id']
                
            # 后续参数一致        
            amount = get_param_by_json('amount')  # 总金额
            coupon_amount = get_param_by_json('coupon_amount') # 优惠券金额
            add_price = get_param_by_json('add_price') # 用户加价金额，非0则有值
            pay_amount = get_param_by_json('pay_amount') # 实际支付金额
            coupon_id = get_param_by_json('coupon_id')
            coupon_name = get_param_by_json('coupon_name')
            
            amount = float_ex(amount)
            pay_amount = float_ex(pay_amount)
            coupon_amount = float_ex(coupon_amount)
            add_price = float_ex(add_price)
            
            openid = get_param_by_json('openid')
            sn = g.wx_order.get_order_sn_by_id(order_id)
            if sn == '':        
                return jsonify({'status': -1, 'msg': '订单不存在'})
            
            # 更新订单状态
            g.wx_order.update_payment_order_by_id(order_id,amount,pay_amount,coupon_id,coupon_amount,coupon_name,add_price)
            order_sn = sn
            
        biz_params = {
            "merchantNo": YEEPAYConfig.merchant_id,
            "orderId": order_sn, # 商户收款请求号
            "orderAmount": pay_amount, # 转为分
            "goodsName": "网约车行程费用",
            'payWay': 'MINI_PROGRAM', # 支付方式
            'scene':'OFFLINE', # 场景类型
            'channel': 'WECHAT', #渠道类型
            'appId': YEEPAYConfig.WECHAT_APPID,
            'userId': openid,     # 用户openid小程序时要指定
            "returnUrl": YEEPAYConfig.return_url, # 支付结果通知地址",
            "notifyUrl": YEEPAYConfig.notify_url, # 支付结果通知地址,            
            'userIp': get_real_ip(),
            #'expiredTime': '2025-04-22 15:00:00',
        }

        result = client.post(api='/rest/v1.0/aggpay/pre-pay',post_params=biz_params)
        ret = result.get('code')
        if ret is None:
            ret = result.get('result')
        # 3. 返回小程序支付所需参数
        if ret['code'] == '00000':            
            return echo_json(0, 'success',{'paymentParams':json.loads(ret['prePayTn']),'order_id':order_id,'order_sn':order_sn})        
        else:
            logger.error(f"易宝支付创建订单失败: {ret['message']}")
            return jsonify({'status': -1, 'msg': ret['message']})
            
    except Exception as e:
        logger.error(f"易宝支付创建订单异常: {str(e)}")
        return jsonify({
            'status': -2,
            'msg': f'系统错误,支付失败',
            'data': None
        })

def verify_sign(client,response):
        """ 验证易宝回调签名
        Decrypts the response and verifies that it looks like an envelope with a public key.

        Args:
            self: write your description
            client: write your description
        """
        if 'sm' == client.cert_type:
            return - 1


        encryptor = RsaEncryptor(
            isv_private_key,
            list(
                clientConfig.get_yop_public_key().get(u'RSA2048').values())[0])

        try:
            # , isv_private_key, yop_public_key)
            plain = encryptor.envelope_decrypt(response)
          
            # 支付解码结果示例
            result_dec = {'orderId': 'ORDER8de5eebefd5386d72787', 
                  'bankOrderId': '5977373399250425', 
                  'channel': 'WECHAT', 
                  'payWay': 'MINI_PROGRAM', 
                  'uniqueOrderNo': '1013202504250000020999033269', 
                  'merchantName': '彝州出行', 
                  'orderAmount': '0.01', 
                  'payAmount': '0.01', 
                  'realPayAmount': '0.01', 
                  'basicsProductFirst': 'MINI_PROGRAM', 
                  'tradeType': 'REALTIME', 
                  'channelOrderId': '4200002616202504258136824949', 
                  'basicsProductThird': 'OFFLINE', 
                  'paySuccessDate': '2025-04-25 10:27:12', 
                  'basicsProductSecond': 'WECHAT', 
                  'outClearChannel': 'UP', 
                  'payerInfo': '{"appID":"wx1d4e91f3c9617487","bankCardNo":"","bankId":"CFT","cardType":"DEBIT","channelTrxId":"4200002616202504258136824949","mobilePhoneNo":"","userID":"oNN1h7A_05mB9sd5dFZ2p0kxmxO4"}', 'appID': 'wx1d4e91f3c9617487', 'parentMerchantNo': '10091171421', 'channelTrxId': '4200002616202504258136824949', 'merchantNo': '10091171421', 'status': 'SUCCESS'
                  }
            # 解析支付结果
            payerInfo = json.loads(plain)
                            
            # 更新订单并验证支付状态
            return g.wx_order.verify_order_pay_state(payerInfo['orderId'],payerInfo)
                        
            #print('plain:{}'.format(plain))

            #assert plain == content
        except Exception as e:
            #assert repr(e).find(u'isv private key is illegal!') > 0
            logger.error(f"易宝支付解密失败: {str(e)}")
            return - 1
            
@yeepay_route.route('/notify', methods=['POST'])
def yeepay_notify():
    """易宝支付异步通知处理"""
    """支付结果回调通知"""
    try:
        # 1. 验证签名
        data = request.form.to_dict()
        sign = data.pop('sign', '')
        logger.info(f"易宝支付异步通知: {data}")
                
        response = data["response"]
        appKey = data["customerIdentification"]
        
        if not verify_sign(client,response):
            return echo_json(-1, '验证失败',code=201)
     
        return echo_json(0, 'success',code=200)
    except Exception as e:
        logger.error(f"支付通知处理失败: {str(e)}")
        return echo_json(-1, '验证失败',code=201)
    
@yeepay_route.route('/return', methods=['POST'])
def yeepay_return():
    """易宝支付成功回调处理，其实在上面notify就已经处理了"""
    try:
        # 获取通知参数
        params = request.get_json()
        logger.info(f"易宝支付成功回调: {params}")
        
    except Exception as e:
        return jsonify({'status': -1, 'message': f'处理失败: {str(e)}'})