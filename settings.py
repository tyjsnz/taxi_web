import os
class Config:
    # 项目路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 当前路径
    # root_path = path.abspath('')
    # 静态文件夹的路径
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
    # 相册的上传目录
    UPLOAD_DIR = os.path.join(STATIC_DIR, 'upload')
    VIDEO_DIR = os.path.join(os.path.abspath(''), 'video')

    NO_EXISTS_FILE_EXT={
            "exe",
            "bat",
            "sh",
            "o",
            "js",
            "php",
            "py"
    }

    # 排除的验证后缀
    EXCLUDE = [".css",".js",".ico",".png",".jpg",".jpeg",".woff2",".woff"]
    LOGIN_CLOSE = True # 登录验证关闭

    SECRET_KEY = '6km12e18f34eea0a529c36640d0acdf3'

    # 微信小程序信息
    WECHAT_APPID = 'xxxx'
    WECHAT_SECRET_KEY = 'xxx'
    WECHAT_TOKEN = "xxxx"

    # 阿里云短信服务
    SMS_ACCESS_KEY_ID = 'xxx'
    SMS_ACCESS_KEY_SECRET = 'xxx'
    # 手机验证码过期时间
    SMS_VERIFICATION_EXPIRE_TIME = 120

    # flask-session的配置
    # PERMANENT_SESSION_LIFETIME = timedelta(days=14)	#过期时间
    SESSION_COOKIE_NAME = 'session_id'					#cookie名字    
    SESSION_TYPE = 'redis'  # 使用 Redis 存储 Session
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True  # 对 Session 数据进行签名
    SESSION_KEY_PREFIX = 'session:'  # Redis 中的键前缀

    # 后台调试模式，不验证登录
    APP_DEBUG = True

    # WEBSOCKET
    WEBSOCKET_URL = 'ws://127.0.0.1:19001/websocket'
    WEBSOCKET_TOKEN = "kmlskj68505986"
    
    WEB_URL = 'https://127.0.0.1:8002'

    LOCAL_DB = True

class YEEPAYConfig(Config):
    # 易宝支付配置
    merchant_id ='10091171421'
    merchant_key = 'MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCOdZ5mvQArWmmN72H90i836u01CSiVcyGtuOwZxvlZVvcx/Wmt83rsHIQSRQdGU/dO2xTtP4+sFn9+TKqqFT+B/fiwfLxKLAduKQC22XNekxbRx/8ygXrk1L0ZPDKXU5Oy/rJ//enHMg9NQ1zylOT++9tP9Wtfo5hMM6H85H9QarO9cOA1bdgip7EelibEeSXeri2SFWGQin8oIylN/hr/HGjNrz7wV47MR1JKNvZr88KKQj1RrF7uiM8Dgfkz5uPct2NDu/4TfqI4YqpICQpFnhc8n74umUltxPzhl+kIyZ0avpGAe2eKYPTB7XGOltIfosbIE2yPpVj5qjIiIBStAgMBAAECggEAGOr/WjKYbzzZBjPXNM25JyN/Or3fnKZ+/1M/bvHUBxm0Usjj3YKfX2HMgyKSV22T7jXZZvctcvkbc1THLElbqqnpADvNNn8VjKH85z7JVINPZEHChEvMGm8QpXOXWMtMZCxzPfqEk+xQa2ALR74eAPC+R3Hixl+H4dpNLP4tu7uvUttxLyPKZsGn3QI9AiSPNJk3nqLwx42T0De2aX6rqQ0N/MDjxW2Ax7Ya08jgNLlJGSff8JbnqP8cL4dW9pC62hZOTUWFcHMcDlVys6rDYMBloRWBDvO2m+BzNcAq9/ONsmrdyTKbIOsQZys+i/3jnS/95Rs6VYmnOg3oMBZdSQKBgQDIX9TBTHVbCBM5UUyoeAQHcQEHz7TJlVWh/n1elsf8zmG0oPIunSN4fLjVcvdHi96o2q3of1B+Dgt4o2P5dQlDIZr0coN9sIatgHU7rYsPvnHyON1l1Ccnz74BQOlX5Gm/sCJAEhKcdpB5dSAgfYDwEcShhfI1KFW4n+ig+y475QKBgQC2Aeb0hBuQ7Z+3FQs7Dxezb84jdO2DD8tgACul/FVaB7vTPNN5PvVwymXKuKvgnj9HW0l4t0uy3+zduPLb4GStpgrr2o3PwBwSls8FNDSmVF8jJ+xZUIeiyl9IW1OHwRoDDt5OKH6/7t3yRn7WHIEXlqIyyho3cqf2EXmP/bC5KQKBgDoJN7A9Gwig0CCb4Z4yFMiq/Gdsy6pPbJwc/+bzuT0J8dbFfx/tN6bgSRDZ2bGJW5aAsDpVFdVM8BmjCYPpWCNvilgfCuLOzFNYj5wXad3HhW1o9wdVaXnoe9oVGQDyEYcJ1wHDukxDMxlayVFfyIbAPrmh+ENZSWrONizaU8vZAoGATc+OX2bDKjiMmYbjoEIZjdr0s+/fQrLT7ZzlDDdOfgjkYbCVcDZcU/YTgpFk2ciNoQID7RnfwP8+kqPpH9tU73AXJzHugqzM052pr73b7GgRrEP7JUvqUMxX4+U3VshVSI1ouN1TItcKB/PfccYJ4n3BphkFEENyTx61a7u3e9ECgYEAuhjH6YjNCbQ9q5XlDLZ7jaXYIFKndvqWXcgyV02Pp4ypcvNKBBWULUdMxL6o+E3VAPSy+jxdug2TTVE+LUTUfHZR9e1bZhxIa8aMd9HZpCJjqEylNiqA/X149ErVvK4YGiwqT2SgfrZZ3C5IxeBjTZzBLsDXzDZG0caRIEbvPTE='
    #pay_url = 'https://openapi.yeepay.com/yop-center/rest/v1.0/aggpay/pre-pay'
    pay_url = 'https://sandbox.yeepay.com/yop-center/rest/v1.0/aggpay/pre-pay'
    notify_url = 'https://wxapp.flacn.net/wechat/pay/yeepay/notify'  # 支付结果异步通知地址
    return_url = 'https://wxapp.flacn.net/wechat/pay/yeepay/return'  # 支付成功跳转地址,小程序支付完成跳转地址
    
    private_key = "易宝支付私钥 BEGIN RSA PRIVATE KEY部分"
    
    public_key = """易宝支付公钥 BEGIN RSA PUBLIC KEY部分"""
    # 易宝支付SDK路径
    sdk_path = r'C:\ProgramData\anaconda3\envs\taxi_web\Lib\site-packages\yop_python_sdk'
    
class OCRConfig():
    # 腾讯云OCR服务
    secret_id = ''
    secret_key = ''
    
class MQTTConfig():
    """MQTT配置,目前不使用"""
    MQTT_BROKER_URL = '127.0.0.1'
    MQTT_BROKER_PORT = 1883
    MQTT_USERNAME = 'admin'
    MQTT_PASSWORD = 'admin'
    MQTT_KEEPALIVE = 60

class DatabaseConfig(Config):
    if Config.LOCAL_DB:
        CHARSET = 'utf8'
        USER = 'root'
        PASSWORD = 'root'
        DB = "ls_taxi"
        HOST = "127.0.0.1"
        PORT = 3306
    else:
        CHARSET = 'utf8'
        USER = 'root'
        PASSWORD = ''
        DB = "ls_taxi"
        HOST = "127.0.0.1"
        PORT = 3306

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    
class DriverFindConfig(Config):
    """司机查找配置"""
    # 查找等待时间
    SEARCH_TIMEOUT = 60
    
    # 订单查找范围
    SEARCH_RADIUS = 150000
    
    # 多少分钟内司机的有效定位
    DRIVER_GPS_EXPIRE_TIME = 600
    
    # 司机查找间隔时间（秒）
    DRIVER_FIND_INTERVAL = 5