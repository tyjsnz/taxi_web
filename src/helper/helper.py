# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

from flask import jsonify,make_response,request
import os
import platform
import secrets
import pytz,datetime
import inspect
import os
from loguru import logger
import cProfile
from pytz import timezone
import math

def gen_md5(_pwd):
    import hashlib
    '''md5密码生成
        如需要：可使用_pwd.update(b'#$%')对密码进行附加加密
    '''
    _pwd = hashlib.md5(_pwd.encode('utf-8'))
    _pwd.update(b'!@#')
    return _pwd.hexdigest()

def base64_encode(_str):
    import base64
    try:
        data_bytes = _str.encode('utf-8')
        return base64.b64encode(data_bytes)
    except Exception as e:
        print(e)
        return False
    
def base64_decode(_str):
    import base64
    try:
        decoded_bytes = base64.b64decode(_str)
        # 将字节解码回原始字符串
        decoded_data = decoded_bytes.decode('utf-8')

        # 输出解码后的字符串
        return decoded_data
    except Exception as e:
        print(e)
        return False
    
def echo_json(status, message='success', data = None, other = None,code=200):
    '''输出json结果
        Args:
            status: 状态码0=success, 非0为失败
            msg: 输出消息
            data: 返回的数据

        Returns:

            {'status': status, 'msg': message, 'data': data, 'other': other}
    '''
    response = make_response(jsonify({'status': status, 'msg': message, 'data': data, 'other': other}),code)
    response.autocorrect_headers = False  # 防止Flask修改非标准状态码
    return response

def get_page_param():
    '''获取分页数据
        如无分分页数据，则返回默认值[pageindex=0,pagesize=50] 

        Retures:
            [pageindex, pagesize]
    '''
    pageindex = 0
    pagesize = 20
    try:
            #print(request.values)
        if request.values.get("page") is not None:
            pageindex = int(request.values.get("page"))
        elif request.headers['page'] is not None:
            pageindex = int(request.headers["page"])

        if request.values.get("pagesize") is not None:
            pagesize = int(request.values.get("pagesize"))
        elif request.headers['pagesize'] is not None:
            pagesize = int(request.headers["pagesize"])

        return [pageindex, pagesize]
    except Exception as e:
        return [pageindex, pagesize]

def get_page_param_ex(pagesize = 20):
    '''获取分页数据，此数据计算了开始位置，使用时直接带入到sql中即可
        如无分分页数据，则返回默认值[pageindex=0,pagesize=50] 

        Retures:
             success: " limit 0,50"
             failed: ''
    '''
    pageindex = 0
    #pagesize = 20
    try:
            #print(request.values)
        if request.values.get("page") is not None:
            pageindex = int(request.values.get("page"))
        elif request.headers['page'] is not None:
            pageindex = int(request.headers["page"])

        if request.values.get("pagesize") is not None:
            pagesize = int(request.values.get("pagesize"))
        elif request.headers['pagesize'] is not None:
            pagesize = int(request.headers["pagesize"])

        pageindex = pageindex - 1 if pageindex > 0 else 0
        pageindex = pageindex * pagesize
        
        return f" limit {pageindex}, {pagesize}"
    except Exception as e:
        return ""
    
def get_param_by_int(_name):
    '''获取页面数值类型数据
        Retures:
            页面参数
    '''

    value = 0
    try:
        if request.values.get(_name) is not None:
            value = int(request.values.get(_name))
       
        return value
    except Exception as e:
        return 0

def get_param_by_str(_name):
    '''获取页面类型数据
        Retures:
            页面参数
    '''
    value = ''
    try:
        if request.values.get(_name) is not None:
            value = request.values.get(_name)
       
        return value
    except Exception as e:
        return ''
    
def get_param_by_json(_name):
    '''获取页面类型数据
        Retures:
            页面参数
    '''
    value = ''
    try:
        json_data = request.get_json()
        value = json_data[_name]
        
        return value
    except Exception as e:
        return ''
    
def get_openid():
    '''获取openid
        Retures:
            openid
    '''    
    openid = get_param_by_str('openid')
    if openid == '' or openid is None:
        openid = get_param_by_json('openid')
        
    return openid

def get_user_token():
    """获取用户token
        Retures:
            token
    """
    token = request.headers.get('Authorization','')
    return token
def get_header_token_by_bearer():
    """获取header中的Authorization验证，基于Bearer 认证
        Retures:
            token
    """
    from flask import abort,request
    token = request.headers.get('Authorization', '').replace('Bearer ', '')  # 提取并清理token
    # 验证token
    #if token != "kmlskj":
    #    abort(401, description="Unauthorized Access")
    return token
def Is_Chinese(word):
    '''判断是否为中文，只要带中文均返回True
    '''
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def find_file(search_path, include_str=None, filter_strs=None):
    """
    查找指定目录下所有的文件（不包含以__开头和结尾的文件）或指定格式的文件，若不同目录存在相同文件名，只返回第1个文件的路径
    :param search_path: 查找的目录路径
    :param include_str: 获取包含字符串的名称
    :param filter_strs: 过滤包含字符串的名称
    """
    if filter_strs is None:
        filter_strs = []

    files = []
    # 获取路径下所有文件
    names = os.listdir(search_path)
    for name in names:
        path = os.path.abspath(os.path.join(search_path, name))
        if os.path.isfile(path):
            # 如果不包含指定字符串则
            if include_str is not None and include_str not in name:
                continue

            # 如果未break，说明不包含filter_strs中的字符
            for filter_str in filter_strs:
                if filter_str in name:
                    break
            else:
                files.append(path)
        else:
            files += find_file(path, include_str=include_str, filter_strs=filter_strs)
    return files

def create_dir(_path):
    '''创建目录,注不递归创建目录
    '''
    import stat
    if not os.path.exists(_path):
        os.mkdir(_path)
        os.chmod(_path,stat.S_IRWXU | stat.S_IRGRP |stat.S_IRWXO)

def delete_file(_fname):
    ''' 删除指定文件
        Args:
            fname: 文件相对路径
    '''
    full_path = os.path.abspath('') + _fname
    if os.path.isfile(full_path) and os.path.exists(full_path):
        os.remove(full_path)

def diff_seconds(start_time, end_time):
    ''' 计算两个字符串时间相差多少秒
        Args:
            start_time: 开始时间如：2023-08-07 12:23:55
            end_time: 结束时间如：2023-08-07 13:19:45 
        Return: 
            int: 查差多少秒
        @date:   2023/08/07 23:42:46
        @author: snz
    '''
    
    from datetime import datetime
    _s = datetime.strptime(str(start_time),"%Y-%m-%d %H:%M:%S")
    _e = datetime.strptime(str(end_time),"%Y-%m-%d %H:%M:%S")
    return (_e - _s).seconds

def diff_days(start_time, end_time):
    ''' 计算两个字符串时间相差多少天
        Args:
            start_time: 开始时间如：2023-08-07 12:23:55
            end_time: 结束时间如：2023-08-07 13:19:45 
        Return: 
            int: 查差多少天
        @date:   2023/08/07 23:42:46
        @author: snz
    '''
    
    from datetime import datetime
    _s = datetime.strptime(str(start_time),"%Y-%m-%d %H:%M:%S")
    _e = datetime.strptime(str(end_time),"%Y-%m-%d %H:%M:%S")
    return (_e - _s).days

def calculate_time_difference(send_time):
    """计算与当前时间相差的秒数
    :"""
    from datetime import datetime
    # 获取当前时间
    current_time = datetime.now()
    
    # 假设 send_time 是从数据库中读取出来的 datetime 对象
    # 如果是从字符串读取，需要先转换为 datetime 对象
    # send_time = datetime.strptime(send_time_str, '%Y-%m-%d %H:%M:%S')
    
    # 计算时间差
    time_difference = current_time - send_time
    
    # 将时间差转换为秒
    time_difference_in_seconds = time_difference.total_seconds()
    
    return time_difference_in_seconds

    # 示例使用
    # 假设 send_time 是从数据库中读取出来的 datetime 对象
    send_time = datetime(2023, 10, 1, 12, 0, 0)  # 示例时间
    seconds_difference = calculate_time_difference(send_time)
    print(f"时间差为 {seconds_difference} 秒")
def generate_float(min_value, max_value):
    """
    生成指定范围内的浮点数，并保留两位小数点。
    
    :param min_value: 浮点数的最小值
    :param max_value: 浮点数的最大值
    :return: 保留两位小数的浮点数
    """
    import random
    # 生成随机浮点数
    float_number = random.uniform(min_value, max_value)
    
    # 保留两位小数
    formatted_number = round(float_number, 2)
    
    return formatted_number

def pdf2img(pdf_path, img_dir):
    '''
    """
        pdf转换img
        pip install PyMuPDF==1.18.17 -i https://pypi.tuna.tsinghua.edu.cn/simple
        Args:
            pdf_path: pdf文件路径
            img_dir: 图片保存路径
        Returns:
            img_list: 图片路径列表

        Remarks:
        base_path = os.path.join(os.path.abspath(''), 'static/upload')
        pdf2img(base_path+"/1.pdf",base_path)
    """
    _sp = '/'
    if platform.system().lower() == 'windows':
        _sp = '\\'

    import fitz
    if img_dir != "" and img_dir[-1] != _sp:
        img_dir += _sp
        

    _base_path = os.path.abspath('')
    ret_img_list = []
    doc = fitz.open(pdf_path)  # 打开pdf

    for page in doc:  # 遍历pdf的每一页
        zoom_x = 2.0  # 设置每页的水平缩放因子
        zoom_y = 2.0  # 设置每页的垂直缩放因子
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat)
        _img_path = r"{}page-{}.png".format(img_dir, page.number)
        pix.save(_img_path)     # 保存

        _img_path = _img_path.replace(_base_path,'')
        ret_img_list.append(_img_path)

    return ret_img_list
    '''
    pass

def pinyin(cn_str):
    '''
    """文字转拼音
        Args:
            cn_str: 中文字符串
        Returns:
            str: 拼音字符串
    """
    from pypinyin import lazy_pinyin, Style
    try:
        return "_".join(lazy_pinyin(cn_str))
    except:
        return cn_str
    '''
    pass

def get_current_time():
        '''
        获取当前时间
        '''
        china_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.datetime.now(china_tz)
        return current_time.strftime("%Y-%m-%d %H:%M:%S")

def get_current_begin_end_time():
        '''
        获取当前开始、结束时间
        '''
        china_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.datetime.now(china_tz)
        return [current_time.strftime("%Y-%m-%d 00:00:00"), current_time.strftime("%Y-%m-%d 23:59:59")]
    
def get_n_days_ago(n=1, tz_name="Asia/Shanghai"):
    """
    获取指定天数前的开始时间和结束时间
    
    Args:
        n (int): 想要获取的天数前的时间范围，默认为1（即前一天）
        tz_name (str): 时区名称，默认为'Asia/Shanghai'
    
    Returns:
        list: 包含两个元素的列表，格式为 [开始时间, 结束时间]
              示例：['2025-04-08 00:00:00', '2025-04-08 23:59:59']
    """
    # 获取指定时区的当前时间
    tz = timezone(tz_name)
    today = datetime.datetime.now(tz)

    # 计算n天前的日期
    n_days_ago = today + datetime.timedelta(days=n)

    # 设置开始时间为n天前的00:00:00
    start_time = n_days_ago.replace(hour=0, minute=0, second=0, microsecond=0)

    # 设置结束时间为n天前的23:59:59
    end_time = n_days_ago.replace(hour=23, minute=59, second=59, microsecond=999999)

    return [
        start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_time.strftime("%Y-%m-%d %H:%M:%S")
    ]
    
def get_real_ip():
    """
    获取客户端的真实IP地址。

    此函数会尝试从请求头中获取 'X-Forwarded-For' 字段，如果存在则取第一个IP地址作为真实IP；
    如果不存在，则使用请求的远程地址作为真实IP。

    Returns:
        str: 客户端的真实IP地址。
    """
    # 尝试从请求头中获取 'X-Forwarded-For' 字段
    real_ip = request.headers.get('X-Forwarded-For')
    if real_ip:
        # 如果 'X-Forwarded-For' 字段存在，取第一个IP地址作为真实IP
        real_ip = real_ip.split(',')[0]
    else:
        # 如果 'X-Forwarded-For' 字段不存在，使用请求的远程地址作为真实IP
        real_ip = request.remote_addr

    return real_ip

def generate_auth_token(length=16):
    return secrets.token_hex(length)  # 生成随机 Token

def generate_token(uid,expire_day = 30):
    ''' 生成用户token，有效期设置为30天，过期后需要重新生成，
        可以通过以下方式解码出对应ID：
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        uid = data['uid']
        Args:
            uid: 用户ID
            expire_day: 过期天数，默认30天
        Return: 
            token
        @date:   2025/03/08 16:11:09
        @author: snz
    '''
    
    import pytz,jwt,datetime
    from settings import Config
    
    # 获取当前的中国时间
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.datetime.now(china_tz)
    exp_time = current_time + datetime.timedelta(days = expire_day)  # token 有效期为 30 天

    payload = {
        'uid': uid,
        'exp': exp_time
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    return token

def decode_token(token):
    '''
    解码generate_token生成的token，如生成成功则返回解码后的id, 否则返回None
        Args:
            token: token
        Return: 
            uid: 用户ID,过期时返回None
            False: 解码失败
    '''
    import jwt
    from settings import Config
    try:
        # 解码 token
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        # app端为无状态方式，不需要存储用户信息
        uid = data['uid']
    except jwt.ExpiredSignatureError:
        # 如果解码失败，返回 None
        uid = None
    except jwt.InvalidTokenError:
        return False
        
    return uid

def write_exception(fname,_exception):
    with open('./run_exception.txt', 'w') as f:
        # 使用str()将异常转换为字符串
        msg = f"file:{fname},exception:{str(_exception)}"
        f.write(msg)
        # 可能还需要记录堆栈跟踪，使用traceback模块
        import traceback
        f.write("\n" + traceback.format_exc())
        
def write_logger(m):
    current_frame = inspect.currentframe()
    caller_frame = inspect.getouterframes(current_frame, 2)
    file_name = os.path.basename(caller_frame[1].filename)
    line_number = caller_frame[1].lineno
    logger.warning(f"{file_name}:{line_number} {m}")
    
def profile_function(func, *args, **kwargs):
    """ 函数性能分析装饰器
    Args:
        func: 函数名称
        *args: 函数参数
        **kwargs: 函数参数
    Return:
        None
    @date:   2025/04/09 12:28:02
    @author: snz
    @version: 1.0
    使用方法：
        # 使用 profile_function 分析 some_other_function函数 的性能
        profile_function(some_other_function, 2, 3)
    """
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    profiler.print_stats(sort='cumtime')
    return result

def get_day_time_range(tz_name="Asia/Shanghai"):
    """
    获取当天的开始时间和结束时间（包含时区处理）
    
    Args:
        tz_name (str): 时区名称，默认为'Asia/Shanghai'
    
    Returns:
        list: 包含两个元素的列表，格式为 [开始时间, 结束时间]
              示例：['2025-04-09 00:00:00', '2025-04-09 23:59:59']
    """
    # 获取指定时区的当前时间
    tz = timezone(tz_name)
    now = datetime.datetime.now(tz)
    
    # 计算当天开始时间（00:00:00）
    start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 计算当天结束时间（23:59:59）
    end_time = start_time + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
    
    # 格式化为字符串
    return start_time.strftime("%Y-%m-%d %H:%M:%S"),end_time.strftime("%Y-%m-%d %H:%M:%S")

# 本周提现总金额
def get_week_time_range(tz_name="Asia/Shanghai"):
    """获取本周的开始和结束时间"""
    # 获取指定时区的当前时间
    tz = timezone(tz_name)
    today = datetime.datetime.now(tz)
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59)
    return start_of_week.strftime('%Y-%m-%d %H:%M:%S'), end_of_week.strftime('%Y-%m-%d %H:%M:%S')

# 本月开始和结束时间
def get_month_time_range(tz_name="Asia/Shanghai"):
    """获取本月的开始和结束时间"""
    tz = timezone(tz_name)
    today = datetime.datetime.now(tz)
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(seconds=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(seconds=1)
    return start_of_month.strftime('%Y-%m-%d %H:%M:%S'), end_of_month.strftime('%Y-%m-%d %H:%M:%S')

def generate_random_filename(extension=".png"):
    """生成随机文件名"""
    import random
    import string

    letters = string.ascii_lowercase + string.digits
    random_string = ''.join(random.choice(letters) for i in range(16))
    return f"{random_string}{extension}"

def resize_and_crop_image(input_path, size, crop_box=None):
    """
    根据输入的图片路径对图片进行指定尺寸的裁剪和缩放，并将处理后的图片生成新文件名（原文件名后加_thumb)存在同一目录

    Args:
        input_path (str): 输入图片的路径
        size (tuple): 裁剪和缩放后的图片尺寸，例如 (width, height)
        crop_box (tuple, optional): 裁剪区域，格式为 (left, upper, right, lower)。如果为None，则不进行裁剪。默认为None。

    Returns:
        str: 处理后的图片路径
    """
    from PIL import Image
    import requests
    import os
    from datetime import datetime
    
    try:
        # 检查路径是否为HTTP URL
        if input_path.startswith(('http://', 'https://')):
            # 下载图片
            response = requests.get(input_path)
            response.raise_for_status()  # 检查请求是否成功
            # 检查响应内容类型是否为图片
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                print(f"Invalid content type: {content_type}")
                return input_path

            img = Image.open(response.content)
        else:
            input_path = os.path.abspath('') + input_path
            img = Image.open(input_path)
        
        # 如果指定了裁剪区域，则进行裁剪
        if crop_box:
            img = img.crop(crop_box)

        # 调整图片大小
        img = img.resize(size,Image.Resampling.LANCZOS)

        # 生成保存路径
        today = datetime.now().strftime("%Y-%m-%d")
        upload_dir = os.path.join(os.path.abspath(''), 'static', 'upload', today)
        create_dir(upload_dir)  # 确保目录存在

        # 生成随机文件名
        output_filename = generate_random_filename()
        output_path = os.path.join(upload_dir, output_filename)

        # 保存处理后的图片
        img.save(output_path)        
        ret = output_path.replace(os.path.abspath(''),'')
        import platform
        if platform.system().lower() == "windows":
            ret = ret.replace("\\","/")
        return ret
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return ""
    
def get_current_customer_config():
    from flask import current_app
    if hasattr(current_app, 'customer_config'):
        return current_app.customer_config
    else:
        return None
    
def get_current_driver_config():
    from flask import current_app
    if hasattr(current_app, 'driver_config'):
        return current_app.driver_config
    else:
        return None
    
def get_current_site_config():
    from flask import current_app
    if hasattr(current_app, 'site_config'):
        return current_app.site_config
    else:
        return None
    
def is_wechat():
    """判断是否为微信浏览器"""
    user_agent = request.headers.get('User-Agent', '')
    if 'MicroMessenger' in user_agent:
        return True
    
    return False

def int_ex(v):
    try:
        v = int(v)
        if math.isnan(v) or math.isinf(v):
            return 0
        return v
    except:
        return 0

def float_ex(v):
    try:
        v = float(v)
        if math.isnan(v) or math.isinf(v):
            return 0
        return v
    except:
        return 0