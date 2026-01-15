# -*- encoding: utf-8 -*-
'''
@file     :   app.py
@date     :   2025/04/21 17:47:54
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   易宝支付接口测试
'''

import base64
import hashlib
import hmac
from urllib.parse import urlencode, quote_plus
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from flask import Flask, request, jsonify
import requests
import uuid
from config import YEEPAYConfig

app = Flask(__name__)

class YopSigner:
    @staticmethod
    def urlsafe_base64_encode(data: bytes) -> str:
        """URL安全的Base64编码"""
        return base64.urlsafe_b64encode(data).decode('utf-8').replace("=", "")

    @staticmethod
    def urlsafe_base64_decode(data: str) -> bytes:
        """URL安全的Base64解码"""
        return base64.urlsafe_b64decode(data + "=" * (4 - len(data) % 4)) if data else b""

    @staticmethod
    def generate_signature(private_key: str, data: str) -> str:
        """生成RSA-SHA256签名"""
        key = RSA.import_key(private_key)
        h = SHA256.new(data.encode('utf-8'))
        signature = pkcs1_15.new(key).sign(h)
        return YopSigner.urlsafe_base64_encode(signature)

    @staticmethod
    def verify_signature(public_key: str, data: str, signature: str) -> bool:
        """验证响应签名"""
        key = RSA.import_key(public_key)
        h = SHA256.new(data.encode('utf-8'))
        try:
            pkcs1_15.new(key).verify(h, YopSigner.urlsafe_base64_decode(signature))
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def build_auth_string(app_key: str, expired_seconds: int = 1800) -> str:
        """构建认证字符串"""
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"yop-auth-v3/{app_key}/{timestamp}/{expired_seconds}"

    @staticmethod
    def sort_and_encode_params(params: dict) -> str:
        """参数排序并编码"""
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        encoded_pairs = []
        for k, v in sorted_params:
            if isinstance(v, list):
                v = ",".join(map(str, v))
            encoded_k = quote_plus(str(k), safe='')
            encoded_v = quote_plus(str(v), safe='')
            encoded_pairs.append(f"{encoded_k}={encoded_v}")
        return "&".join(encoded_pairs)
    
class YopClient:
    def __init__(self, app_key: str, private_key: str, public_key: str, sandbox: bool = True):
        self.app_key = app_key
        self.private_key = private_key
        self.public_key = public_key
        self.base_url = "https://sandbox.yeepay.com/yop-center" if sandbox else "https://openapi.yeepay.com/yop-center"

    def _build_headers(self, method: str, path: str, params: dict, is_json: bool) -> dict:
        """构建请求头"""
        headers = {
            "x-yop-request-id": str(uuid.uuid4()),
            "x-yop-appkey": self.app_key,
            #"x-yop-sdk-langs": "python",
            #"x-yop-sdk-version": "4.0",
        }

        # 计算请求体摘要
        if method == "GET":
            content_sha256 = hashlib.sha256(b"").hexdigest()
        else:
            if is_json:
                import json
                body = json.dumps(params, ensure_ascii=False).encode('utf-8')  # 先转JSON字符串再编码
            else:
                body = YopSigner.sort_and_encode_params(params).encode('utf-8')
            content_sha256 = hashlib.sha256(body).hexdigest()
        headers["x-yop-content-sha256"] = content_sha256

        # 构建规范请求
        auth_string = YopSigner.build_auth_string(self.app_key)
        canonical_uri = path
        canonical_query = YopSigner.sort_and_encode_params(params) if method == "GET" else ""
        canonical_headers = "\n".join([
            f"x-yop-appkey:{headers['x-yop-appkey']}",
            f"x-yop-content-sha256:{content_sha256}",
            f"x-yop-request-id:{headers['x-yop-request-id']}"
        ])
        canonical_request = f"{auth_string}\n{method}\n{canonical_uri}\n{canonical_query}\n{canonical_headers}"

        # 生成签名
        signature = YopSigner.generate_signature(self.private_key, canonical_request)
        signed_headers = "x-yop-appkey;x-yop-content-sha256;x-yop-request-id"
        auth_header = f"YOP-RSA2048-SHA256 {auth_string}/{signed_headers}/{signature}$SHA256"
        headers["Authorization"] = auth_header

        if is_json:
            headers["Content-Type"] = "application/json"
        else:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        
        # headers = {
        #     "Content-Type": "application/x-www-form-urlencoded",
        #     "Authorization": "YOP-RSA2048-SHA256 yop-auth-v3/app_1234/2025-02-28T04:15:29Z/1800/x-yop-appkey;x-yop-content-sha256;x-yop-request-id/aBcDeFgHiJkLmNoPqRsTuVwXyZ$SHA256",
        #     "x-yop-request-id": "550e8400-e29b-41d4-a716-446655440000",
        #     "x-yop-appkey": self.app_key,# "app_1234567890",
        #     "x-yop-content-sha256": "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
        # }
        return headers

    def send_request(self, method: str, path: str, params: dict = None, is_json: bool = False):
        """发送HTTP请求"""
        url = f"{self.base_url}{path}"
        headers = self._build_headers(method, path, params or {}, is_json)
        payload = params if is_json else YopSigner.sort_and_encode_params(params) if params else ""

        try:
            response = requests.request(
                method, url, headers=headers, json=payload if is_json else params, timeout=30
            )
            return self._handle_response(response)
        except Exception as e:
            raise Exception(f"请求失败: {str(e)}")

    def _handle_response(self, response):
        """处理响应（验证签名）"""
        try:
            content = response.text.strip()
            signature = response.headers.get("x-yop-sign")
            if signature and self.public_key:
                if not YopSigner.verify_signature(self.public_key, content, signature):
                    raise Exception("响应签名验证失败")
            return {
                "status_code": response.status_code,
                "data": response.json(),
                "headers": dict(response.headers)
            }
        except Exception as e:
            raise Exception(f"响应处理失败: {str(e)}")
        
@app.route('/yop/payment', methods=['POST','GET'])
def create_payment():
    """创建支付请求"""
    app_key = 'app_10091171421'
    
    private_key = """-----BEGIN PRIVATE KEY-----
    MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCOdZ5mvQArWmmN72H90i836u01CSiVcyGtuOwZxvlZVvcx/Wmt83rsHIQSRQdGU/dO2xTtP4+sFn9+TKqqFT+B/fiwfLxKLAduKQC22XNekxbRx/8ygXrk1L0ZPDKXU5Oy/rJ//enHMg9NQ1zylOT++9tP9Wtfo5hMM6H85H9QarO9cOA1bdgip7EelibEeSXeri2SFWGQin8oIylN/hr/HGjNrz7wV47MR1JKNvZr88KKQj1RrF7uiM8Dgfkz5uPct2NDu/4TfqI4YqpICQpFnhc8n74umUltxPzhl+kIyZ0avpGAe2eKYPTB7XGOltIfosbIE2yPpVj5qjIiIBStAgMBAAECggEAGOr/WjKYbzzZBjPXNM25JyN/Or3fnKZ+/1M/bvHUBxm0Usjj3YKfX2HMgyKSV22T7jXZZvctcvkbc1THLElbqqnpADvNNn8VjKH85z7JVINPZEHChEvMGm8QpXOXWMtMZCxzPfqEk+xQa2ALR74eAPC+R3Hixl+H4dpNLP4tu7uvUttxLyPKZsGn3QI9AiSPNJk3nqLwx42T0De2aX6rqQ0N/MDjxW2Ax7Ya08jgNLlJGSff8JbnqP8cL4dW9pC62hZOTUWFcHMcDlVys6rDYMBloRWBDvO2m+BzNcAq9/ONsmrdyTKbIOsQZys+i/3jnS/95Rs6VYmnOg3oMBZdSQKBgQDIX9TBTHVbCBM5UUyoeAQHcQEHz7TJlVWh/n1elsf8zmG0oPIunSN4fLjVcvdHi96o2q3of1B+Dgt4o2P5dQlDIZr0coN9sIatgHU7rYsPvnHyON1l1Ccnz74BQOlX5Gm/sCJAEhKcdpB5dSAgfYDwEcShhfI1KFW4n+ig+y475QKBgQC2Aeb0hBuQ7Z+3FQs7Dxezb84jdO2DD8tgACul/FVaB7vTPNN5PvVwymXKuKvgnj9HW0l4t0uy3+zduPLb4GStpgrr2o3PwBwSls8FNDSmVF8jJ+xZUIeiyl9IW1OHwRoDDt5OKH6/7t3yRn7WHIEXlqIyyho3cqf2EXmP/bC5KQKBgDoJN7A9Gwig0CCb4Z4yFMiq/Gdsy6pPbJwc/+bzuT0J8dbFfx/tN6bgSRDZ2bGJW5aAsDpVFdVM8BmjCYPpWCNvilgfCuLOzFNYj5wXad3HhW1o9wdVaXnoe9oVGQDyEYcJ1wHDukxDMxlayVFfyIbAPrmh+ENZSWrONizaU8vZAoGATc+OX2bDKjiMmYbjoEIZjdr0s+/fQrLT7ZzlDDdOfgjkYbCVcDZcU/YTgpFk2ciNoQID7RnfwP8+kqPpH9tU73AXJzHugqzM052pr73b7GgRrEP7JUvqUMxX4+U3VshVSI1ouN1TItcKB/PfccYJ4n3BphkFEENyTx61a7u3e9ECgYEAuhjH6YjNCbQ9q5XlDLZ7jaXYIFKndvqWXcgyV02Pp4ypcvNKBBWULUdMxL6o+E3VAPSy+jxdug2TTVE+LUTUfHZR9e1bZhxIa8aMd9HZpCJjqEylNiqA/X149ErVvK4YGiwqT2SgfrZZ3C5IxeBjTZzBLsDXzDZG0caRIEbvPTE=
    -----END PRIVATE KEY-----"""
    
    # 注意：公钥需要使用base64编码
    public_key = f"""-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAjnWeZr0AK1ppje9h/dIvN+rtNQkolXMhrbjsGcb5WVb3Mf1prfN67ByEEkUHRlP3TtsU7T+PrBZ/fkyqqhU/gf34sHy8SiwHbikAttlzXpMW0cf/MoF65NS9GTwyl1OTsv6yf/3pxzIPTUNc8pTk/vvbT/VrX6OYTDOh/OR/UGqzvXDgNW3YIqexHpYmxHkl3q4tkhVhkIp/KCMpTf4a/xxoza8+8FeOzEdSSjb2a/PCikI9Uaxe7ojPA4H5M+bj3LdjQ7v+E36iOGKqSAkKRZ4XPJ++LplJbcT84ZfpCMmdGr6RgHtnimD0we1xjpbSH6LGyBNsj6VY+aoyIiAUrQIDAQAB
    -----END PUBLIC KEY-----"""

    client = YopClient(app_key, private_key, public_key,sandbox=False)
   
    biz_params = {
        'parentMerchantNo': '10091171421',
        "merchantNo": "10091171421",
        "orderId": "20231012143528001",
        "orderAmount": "100.00",
        "currency": "CNY",
        "goodsName": "testgood",
        'payWay': 'WECHAT',
        'scene':'OFFLINE',
        'appId': 'wx1d4e91f3c9617487',
        'userId': '2088176118911271',
        'token': '83BCDF29CFACB4411533080B67864EF8C907CCDC5E10A707C285FEA10CDB8221',
        "returnUrl": "https://your-domain.com/return",
        "notifyUrl": "https://your-domain.com/notify",
        'bankCode': 'BOC',  # 银行代码
        'userIp': '127.12.1.60',
        'expiredTime': '2025-04-22 15:00:00',
    }

    try:
        response = client.send_request(
            method="POST",
            path="/rest/v1.0/aggpay/pre-pay", 
            params=biz_params,
            is_json=False
        )
        return jsonify({
            "code": "SUCCESS",
            "message": "请求成功",
            "data": response["data"]
        })
    except Exception as e:
        return jsonify({
            "code": "ERROR",
            "message": str(e),
            "data": {}
        })
    
if __name__ == "__main__":
    app.run(debug=True, port=8002, host='0.0.0.0')