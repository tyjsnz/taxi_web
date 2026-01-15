# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   driver_controller.py
@date     :   2025/03/09 00:43:57
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   司机端控制器
'''
from flask import request,session
import pytz,jwt,datetime
from settings import Config
from src.helper.helper import *
from src.model.driving.driver_db import DriverDb
from src.model.driving.driver_location_db import DriverLocationDb
from src.controller.web.wechat.libs.order_libs import OrderLibs
from src.controller.web.wechat.libs.driver_location_cache import DriverLocationCache
from src.model.driving.driver_order_accept_db import DriverOrderAcceptDb
from src.model.driving.driver_account_db import DriverAccountDb
from src.controller.admin.base_controller import BaseController
from datetime import datetime
from src.common.const_defined import *
from src.helper.sms_helper import SmsHelper
from src.common.app_total_controller import AppTotalController

import json
class DriverController(BaseController):
    def __init__(self) -> None:
        self._db = DriverDb()
        self._order_lib = OrderLibs()
        self._location_db = DriverLocationDb()
        self.driver_cache = DriverLocationCache()

        self.driver_accept = DriverOrderAcceptDb()
        self.account_db = DriverAccountDb()
        self.app_total_controller = AppTotalController()

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
        return None
        if request.path in not_auth_path:
            return None  # 白名单路径跳过验证

        # 前端请求时需要在header中携带Authorization头，值为token
        token = request.headers.get('Authorization')
        if not token:
            return echo_json(-1,'Token is missing!',code=401)

        uid = decode_token(token)
        if uid:
            # 有效时看用户状态
            row = self._db.get_user_info_by_id(uid)
            if row is None:
                return echo_json(-1,'用户不存在',code=401)
            if row['status'] == -1:
                return echo_json(-1, '用户已被禁用',code=401)
            return None
        
        elif uid is None:
            # 过期时看数据库中token是否过期，如过期则更新
            row = self._db.get_user_info_by_id(token,'id,token')
            if row:
                uid = decode_token(row['token'])
                if uid is None:
                    token = generate_token(row['id'])
                    self._db.update_driver_info(row['id'], {'token': token})
                    return None
            else:
                return echo_json(-9, 'Invalid Token!',code=401)
        else:
            return echo_json(-1, 'Token has expired!',code=401)            

    def app_login(self):
        ''' app端登录验证,后续接口的访问均通过换取的token进行验证
            Args:
                None
            Return: 
                None
            @date:   2025/03/08 16:11:09
        '''
        if request.method != 'POST':
            return echo_json(-1, '无效请求',code=404)
        
        username = get_param_by_str('username')
        password = get_param_by_str('password')
        if username == '' or password == '':
            return echo_json(-1, '用户名或密码为空',)
        
        password = gen_md5(password)
        
        row = self._db.get_user_info(username, password)
        if row is None:
            return echo_json(-1, '用户名或密码错误')
        
        if row['status'] == -1:
            return echo_json(-1, '用户已被禁用')
        
        token = generate_token(row['id'])
        # 登录，设置司机状态为未上班状态
        self._db.update_driver_info(row['id'], {'token': token,'work_status':DRIVER_WORK_STATUS.WORK_OFF})

        data = {
            'token': token,
            'id': row['id'],
            'truename': row['truename'],
            'phone':row['phone'],
            'score': row['score'],
            'car_no': row['car_no'],
            'car_brand': row['car_brand'],
            'car_type': row['car_type'],
            'car_color': row['car_color'],
            'level': row['level'],
            'order_total': row['order_total'],
            'driving_age': row['driving_age'],
            'company_id': row['company_id'],
            'region_id': row['region_id'],
            'accept_order_model': row['accept_order_model'], # 1=抢单模式,0=系统派单模式
            }
        
        # 合并配置文件至data中
        driver_config = get_current_driver_config()
        data.update(driver_config)
            
        return echo_json(0, '登录成功', data)
    
    def app_logout(self):
        if request.method != 'POST':
            return echo_json(-1, '无效请求',code=404)
        driver_id = int_ex(get_param_by_str('driver_id'))
        if driver_id <= 0:
            # 前端请求时需要在header中携带Authorization头，值为token
            token = request.headers.get('Authorization')
            if not token:
                return echo_json(-1,'Token is missing!')
            uid = decode_token(token)
            if uid is None or uid is False:
                return echo_json(-1,'Token is invalid!')
            
            
        # app端从登录到退出的在线时长，这里不区分上班和下班
        online_total_time = get_param_by_str('online_total_time')
        if online_total_time == '':
            online_total_time = 0
            
        online_total_time = int(online_total_time)
        
        row = self._db.get_user_info_by_id(driver_id,"online_total_time")
        if row and row['online_total_time'] != None and row['online_total_time'] != '':
            online_total_time = int(row['online_total_time']) + online_total_time
            
        
        data = {
            'work_status': DRIVER_WORK_STATUS.WORK_OFF,
            'accept_order_status': DRIVER_ACCEPT_ORDER_STATUS.NO_ACCEPT,
            'online_total_time': online_total_time
        }
        self._db.update_driver_info(driver_id, data)
        
        # 更新司机在线时长
        self._db.update_driver_online_time(driver_id, DRIVER_WORK_STATUS.WORK_OFF)
        
        # 清空所有session
        session.clear()
        return echo_json(0, '退出成功')
    
    def verify_phone(self):
        ''' 验证手机号是否已经注册
            Args:
                : 
            Return: 
                None
            @date:   2025/05/04 16:34:01
            @author: snz
        '''
        phone = get_param_by_str('phone')
        ret_id = self._db.verify_phone(phone)
        if ret_id:
            return echo_json(0, '手机号已经注册',ret_id)
        else:
            return echo_json(-1, '手机号未注册',0)
        
    def pwd_setup(self):
        ''' 设置密码
            Args:
                : 
            Return: 
                None
            @date:   2025/05/04 16:40:35
            @author: snz
        '''
        phone = get_param_by_str('phone')
        if phone == '' or phone == None:
            return echo_json(-1,'手机号不能为空')
        
        pwd = get_param_by_str('pwd')
        if pwd == '' or pwd == None:
            return echo_json(-1,'密码不能为空')
        if len(pwd) < 6 or len(pwd) > 16:
            return echo_json(-1,'密码长度必须在6-16位之间')
        
        pwd = gen_md5(pwd)
        ret_id = self._db.verify_phone(phone)
        if ret_id <= 0:
            return echo_json(-1,'手机号未注册')
        else:
            self._db.update_driver_info(ret_id,{'password':pwd})
            return echo_json(0,'设置成功')
        
    def get_sms_code(self):
        """获取短信验证码
        """
        phone = get_param_by_str('phone')
        if not phone:
            return echo_json(-1,'手机号不能为空')
        
        # 验证手机号是否已经注册
        ret_id = self._db.verify_phone(phone)
        #if ret_id <= 0:
        #    return echo_json(-1,'手机号未注册')

        # 验证手机号是否已经发送过验证码
        code = SmsHelper.generate_sms_code()
        ret = SmsHelper.SendSms(phone,code)
        if ret['code'] == 0:
             # insert vcode to db
            sql = f"insert into ls_sms_code(phone,code,created_at,is_user) values('{phone}',{code},'{get_current_time()}',0)"
            ret = self._db._query_sql(sql)

            return echo_json(0,"短信验证码发送成功",ret_id)
        else:
            return echo_json(-1,"短信验证码发送失败")

    def verify_phone_code(self):
        """手机验证码验证,超时时间60秒
            Args:
                None
            Returns: 
                dict: {'code':0,'msg':'验证码正确'}
        """
        vcode = get_param_by_str('vcode')
        if vcode == '' or vcode == None:
            return echo_json(-1,'验证码不能为空')
        
        phone = get_param_by_str('phone')
        if not phone:
            return echo_json(-1,'手机号不能为空')
        
        # 非0则存在的用户，这时登录
        user_id = get_param_by_int("user_id")
        if user_id <= 0 or user_id == '':
            ret = self._db._query_sql_one(f"select id from ls_driver where phone='{phone}' limit 1")
            if ret:
                user_id = ret['id']

        sql = f"select * from ls_sms_code where phone='{phone}' and code={vcode} and is_user=0 order by id desc limit 1"
        row = self._db._query_sql_one(sql)
        if row is None or row is False:
            return echo_json(-1,'验证码错误')
        
        from datetime import datetime
        created_at = row['created_at']
        current_time = datetime.now()
        time_difference = current_time - created_at
        seconds = time_difference.total_seconds()
        if seconds > Config.SMS_VERIFICATION_EXPIRE_TIME:
            # 过期
            sql = f"update ls_sms_code set is_user=-1 where id={row['id']}"
            self._db._execute_sql(sql)
            return echo_json(-1,'验证码已过期')                
        
        # 验证成功就删除验证码，目前保留以作统计
        sql = f"update ls_sms_code set is_user=9 where id={row['id']}"
        self._db._execute_sql(sql)
        
        # 用户存在，则登录
        if user_id > 0:
            row = self._db.get_user_info_by_id(user_id)
            if row is None:
                return echo_json(-1, '用户不存在')
            
            if row['status'] == -1:
                return echo_json(-1, '用户已被禁用')
            
            token = generate_token(row['id'])
            self._db.update_driver_info(row['id'], {'token': token})

            data = {
                'token': token,
                'id': row['id'],
                'truename': row['truename'],
                'phone':row['phone'],
                'score': row['score'],
                'car_no': row['car_no'],
                'car_brand': row['car_brand'],
                'car_type': row['car_type'],
                'car_color': row['car_color'],
                'level': row['level'],
                'order_total': row['order_total'],
                'driving_age': row['driving_age'],
                'company_id': row['company_id'],
                'region_id': row['region_id']
                }
            
            # 合并配置文件至data中
            driver_config = get_current_driver_config()
            data.update(driver_config)
            return echo_json(0,user_id,data)

        # 用户不存在，返回信息
        return echo_json(0,0)
    
    def update_driver_latlng(self):
        """更新司机位置
        """
        lng = round(float_ex(get_param_by_str('lng')),6)
        lat = round(float_ex(get_param_by_str('lat')),6)
        driver_id = int_ex(get_param_by_str('driver_id'))
        address = get_param_by_str('address')
        company_id = get_param_by_str('company_id')
        
       
        # 写入司机最后位置到数据库
        ret = self._location_db.insert_driver_location(driver_id,lng,lat,address)
        print(ret)
        
        # 写入绑存redis中
        self.driver_cache.update_driver_location(driver_id,lng,lat,company_id=company_id)
        
        return echo_json(0,'success')
    
    def order_accept(self):
        """司机端接单
        """
        company_id = get_param_by_json('company_id')
        order_id = get_param_by_json('order_id')
        driver_id = get_param_by_json('driver_id')
        accept_id = get_param_by_json('accept_id')
        lat = get_param_by_json('lat')
        lng = get_param_by_json('lng')
        if not order_id:
            return echo_json(-1,'订单ID不能为空')
        # 现在没有使用后台任务，所以没有此参数
        #task_id = get_param_by_json('task_id')       
        
        return self._order_lib.confirm_accept_order(order_id,driver_id,accept_id,lat,lng,company_id)
    
    def order_reject(self):
        """司机端拒绝接单
        """
        order_id = int_ex(get_param_by_json('order_id'))
        driver_id = int_ex(get_param_by_json('driver_id'))
        accept_id = int_ex(get_param_by_json('accept_id'))
        if driver_id <= 0:
            driver_id = session.get('driver_id')

        if not order_id:
            return echo_json(-1,'订单ID不能为空')
        
        b,e = get_day_time_range()
        num = self.driver_accept.total_driver_reject_by_date(driver_id,b,e)
        if num == None:
            num = 0
        _max = 0
        row = get_current_driver_config()
        if row and 'order_dispatch_reject_num' in row:
            _max = int_ex(row['order_dispatch_reject_num'])            
                
        # '已超过当天最大拒绝次数'，这时记录并进行相应扣分，但是可以取消
        if num >= _max:
            tip = f"当天已经拒绝订单：{num}次，已超过当天最大拒绝次数({_max})，扣分惩罚~"
            # 减分转为负数
            score = 0 - abs(float_ex(row['order_reject_score']))
            self._db.add_score_rewards_log(driver_id,score,tip)
        
        return self._order_lib.reject_accept_order(accept_id)
    
    def update_navi_latlng(self):
        """导航位置
        """
        lng = get_param_by_json('lng')
        lat = get_param_by_json('lat')
        if lat == '' or lng == '':
            return echo_json(-1,'经纬度不能为空')
        lat = str(round(lat,6))
        lng = str(round(lng,6))
        driver_id = get_param_by_json('driver_id')
        order_id = get_param_by_json('order_id')
        address = get_param_by_json('address')
        speed = get_param_by_json('speed')
        accuracy = get_param_by_json('accuracy')

        data = {
            'order_id': order_id,
            'driver_id': driver_id,
            'latlng': lng+','+lat,
            'address': address,
            'speed': speed,
            'accuracy': accuracy,
            'put_time': get_current_time()
        }
        sql = f"insert ls_navi(order_id,driver_id,latlng,address,speed,accuracy,put_time) values({order_id},{driver_id},'{lng},{lat}','{address}',{speed},{accuracy},'{get_current_time()}')"
        self._location_db._query_sql(sql)
        
        return echo_json(0,'success')
    
    def order_trip(self):
        """ 司机端订单行程数据推送
        Args:
            : 
        Return:
            None
        @date:   2025/04/28 20:37:01
        @author: snz
            
        """
        # navi_over 第一段行程结束到达乘客上车点
        # driver_begin_trip 接到乘客，开始行程
        # navi_over_travel_over 行程结束，乘客到达目的地
        trip_type = get_param_by_json('flag')
        if trip_type not in ['to_picked_up','driver_begin_trip','navi_over','navi_over_travel_over']:
            return echo_json(-1,'trip_type error')
        
        driver_id = get_param_by_json('driver_id')
        order_id = get_param_by_json('order_id')
        
        status = 0
        if trip_type == 'to_picked_up' or trip_type == 'navi_over':
            status = ORDER_STATUS.TO_PICKED_UP
        elif trip_type == 'driver_begin_trip':
            status = ORDER_STATUS.IN_PROGRESS                    
        elif trip_type == 'navi_over_travel_over':
            status = ORDER_STATUS.ARRIVED_NO_PAY
        
        # 如果是先乘后付订单，则状态为已完成
        row = self._order_lib._db.get_order_by_id(order_id,"order_type,accept_time")
        if row['order_type'] == ORDER_TYPE.PAY_AFTER_USE:
            status = ORDER_STATUS.COMPLETED
            
        # 更新订单状态
        self._order_lib._db.update_order_status(order_id, status)
        
        # 改变司机状态为可接单状态
        if status == ORDER_STATUS.COMPLETED or status == ORDER_STATUS.ARRIVED_NO_PAY:
            self._db.update_driver_info(driver_id,{'accept_order_status':DRIVER_ACCEPT_ORDER_STATUS.NO_ACCEPT})
            
            # 行程结束，更新订单从接单时间到行程结束时间seconds
            start_time = row['accept_time']
            end_time = get_current_time()
            _seconds = diff_seconds(start_time,end_time)
            self._order_lib._db.update_order(order_id,{'trip_time': _seconds,'updated_at': end_time,'down_time': end_time})
            
        
        return echo_json(0,'success')
        
    def get_accept_order_list(self,driver_id):
        """ 待接单订单列表
        Args:
            driver_id: 司机ID
        Return:
            None
        @date:   2025/04/09 09:10:08
        @author: snz            
        """
        driver_config = get_current_driver_config()
        # 拉取下单后多少秒内的数据
        _order_max_seconds = 0
        if 'odrder_max_seconds' in driver_config:
            _order_max_seconds = int_ex(driver_config['odrder_max_seconds'])
        result = self.driver_accept.get_list_by_driver_id(driver_id,0,20,_order_max_seconds)
        return echo_json(0,'success',result)
        
    
    def update_work_status(self):
        """更新司机的工作状态及在线时长"""
        driver_id = int_ex(get_param_by_json('driver_id'))
        if driver_id <= 0:
            return echo_json(-1,'driver_id error')
        
        work_status = get_param_by_json('work_status')
        ret = self._db.update_driver_info(driver_id,{'work_status': work_status})
        # 更新司机在线时长        
        self._db.update_driver_online_time(driver_id,work_status)
                
        return echo_json(0,'success')
        
    def update_order_bill(self):
        """更新订单状态为到达侍支付
        """
        order_id = get_param_by_json('order_id')
        driver_id = get_param_by_json('driver_id')

        row = self._order_lib._db.get_order_by_id(order_id,"order_type")
        if row is None:
            return echo_json(-1,'订单不存在')
        
        # 默认为到达未支付
        state = ORDER_STATUS.ARRIVED_NO_PAY
        
        # 如果是先付后用，则直接完成
        if row['order_type'] == ORDER_TYPE.PAY_AFTER_USE:
            state = ORDER_STATUS.COMPLETED
        
        ret = self._order_lib._db.update_order_status(order_id,state)
        if ret:
            return echo_json(0,'success')
        return echo_json(-1,'error')
    
    def get_my_order_list(self,driver_id):
        """我的接单记录
        """
        if driver_id <= 0:
            return echo_json(-1,'error')
        # 格式为2025-01-23
        sdate = get_param_by_str('date')
        where = f'driver_id={driver_id}'
        if sdate != '':
            where += f" and order_time >= '{sdate} 00:00:00' and order_time <= '{sdate} 23:59:59"
        order_list = self._db._query_sql(f"select * from ls_order where {where} order by order_time desc")
        return echo_json(0,'success',order_list)
    
    def driver_suggest_submit(self):
        """司机端建议提交
        """     
        driver_id = get_param_by_json('driver_id')
        _type = get_param_by_json('type')
        content = get_param_by_json('content')
        if not content:
            return echo_json(-1,'内容不能为空')
        contact = get_param_by_json('contact')
        
        data = {
            'type': _type,
            'content': content,
            'contact': contact,
            'created_at': get_current_time(),
            'uid': driver_id,
            'utype': 0,
            'recontent': '',
        }
        self._db.insert_data_by_dict('ls_suggest',data)
        
        return echo_json(0,'success')
    
    def apply_take_cash(self):
        """ 司机申请提现
            Args:
                : 
            Return: 
                None
            @date:   2025/04/20 06:10:45
            @author: snz
        """
        driver_id = get_param_by_json('driver_id')
        amount = get_param_by_json('amount')
        status = DRIVER_CASH_VERIFY_STATUS.NO_VERIFY
        row = self._db.get_user_info_by_id(driver_id,"bank_name,bank_card")
        if row is None:
            return echo_json(-1,'司机不存在')
        bank_name = row['bank_name']
        bank_card = row['bank_card']
        if bank_name == '' or bank_card == '' or bank_card is None or bank_name is None:
            return echo_json(-1,'银行卡信息不完整')
        
        # 检测帐户里金额有多少
        _account = DriverAccountDb()
        in_pay,out_pay = _account.total_account_by_id(driver_id)
        if in_pay < amount:
            return echo_json(-1,'帐户余额不足')
        
        sql = f"select id from ls_driver_take_cash where driver_id = {driver_id} and status = {status} and amount={amount}"
        ret = _account._query_sql_one(sql)
        if ret:
            return echo_json(-1,'申请已提交，请勿重复提交')
        data = {
            'driver_id': driver_id,
            'amount': amount,
            'status': status,
            'bank_name': bank_name,
            'bank_card': bank_card,
            'created_at': get_current_time(),
        }
        ret = self._db.insert_data_by_dict("ls_driver_take_cash",data)
        if ret is None:
            return echo_json(-1,'申请失败')
        
        return echo_json(0,'申请已提交')
    
    def image_to_base64(self,image_path):
        import base64
        with open(image_path, "rb") as image_file:
            # 读取图片二进制数据
            image_data = image_file.read()
            # 将二进制数据编码为base64字符串
            base64_str = base64.b64encode(image_data).decode('utf-8')
        return base64_str
        
    def driver_license_upload(self):
        """ 司机端注册时相关证件上传,上传图片为单张上传，故先存临时目录，以更定期清理
        Args:
            : 
        Return:
            None
        @date:   2025/04/20 19:56:06
        @author: snz
            
        """
        _type = get_param_by_int('type')
        if _type not in [1,2,3,4,5,6]:
            return echo_json(-1,'参数错误')
        
        from src.helper.upload_service import UploadService
        filer_tager = request.files
        imgs = []
        for _file in filer_tager:
            ret = UploadService.UploadByFile(filer_tager[_file],"driver_reg_temp")
            if ret["code"] != 200:
                continue
            if _type in [3,4,5,6]:
                return echo_json(0,'success',{'img': ret['data']['file_key']})
            
            imgs.append(ret['data']['file_key'])
        
        full_path = os.path.abspath('') + imgs[0]
        b64 = self.image_to_base64(full_path)
        #return echo_json(0,'success',{'img': imgs[0],'id': 1})
        from src.helper.ocr.qq_ocr import QQOCR

        ocr_result = QQOCR.get_ocr_result(b64,_type,True)
        if _type == 1:
            if ocr_result != None:
                ocr_result['pic_front'] = imgs[0]
            # 可以直接存入数据库
            ret_id = self._db.insert_data_by_dict("ls_driver_license",ocr_result)
            if ret_id:
                return echo_json(0,'success',{'id': ret_id,'img': imgs[0]})
        elif _type == 2:
            # 行驶证
            if ocr_result != None:
                ocr_result['file_front'] = imgs[0]
            ret_id = self._db.insert_data_by_dict("ls_device_vehicle_license",ocr_result)
            if ret_id:
                return echo_json(0,'success',{'id': ret_id,'img': imgs[0]})
        
        return echo_json(-1,'识别失败,请重试重试')

        
    def driver_register(self):
        #注册 
        phone = get_param_by_json('phone')
        pic1_id = get_param_by_json('pic1_id')
        pic2_id = get_param_by_json('pic2_id')
        id_card1 = get_param_by_json('id_card1')
        id_card2 = get_param_by_json('id_card2')
        car_img1 = get_param_by_json('car_img1')
        car_img2 = get_param_by_json('car_img2')
        
        recommend_uid = 0
        recommend_name = ''
        recommend_phone = get_param_by_json('recommend_phone')
        if recommend_phone != '':
            sql = f"select id,truename from ls_driver where phone = '{recommend_phone}'"
            if recommend_phone != '':
                ret = self._db._query_sql_one(sql)
                if ret is None:
                    return echo_json(-1,'推荐人手机号不存在')
                recommend_uid = ret['id']
                recommend_name = ret['truename']
                

        ret1 = self._db._query_sql_one(f"select * from ls_driver_license where id = {pic1_id}")
        ret2 = self._db._query_sql_one(f"select * from ls_device_vehicle_license where id = {pic2_id}")
        if ret1 is None or ret2 is None:
            return echo_json(0,'注册信息不完整')
        data = {
            'truename': ret1['name'],
            'phone': phone,
            'car_no': ret2['car_no'],
            'id_card_img': id_card1,
            'id_card_img1': id_card2,
            'car_type': ret2['car_type'],
            'car_brand': ret2['model'],
            'car_img': car_img1,
            'car_img1': car_img2,
            'region_id': 0,
            'recommend_uid': recommend_uid,
            'recommend_name': recommend_name,
            'recommend_phone': recommend_phone,
            'created_at': get_current_time()
        }
        sql = f"select id from ls_driver where phone = '{phone}'"
        ret = self._db._query_sql_one(sql)
        if ret is not None:
            return echo_json(-1,'手机号已被注册')
  
        ret = self._db.insert_data_by_dict('ls_driver_register',data)
        if ret is None:
            return echo_json(-1,'注册失败')
        return echo_json(0,'注册成功，请留意审核结果')
    
    def get_my_profile(self):
        """ 司机个人资料
        Args:
            : 
        Return:
            None
        @date:   2025/04/20 23:38:57
        @author: snz
            
        """
        driver_id = get_param_by_str('driver_id')
        if driver_id == '':
            driver_id = session.get('driver_id')
            if driver_id == None or driver_id == '':
                return echo_json(-1,'参数错误')
        
        result = self._db.get_user_info_by_id(driver_id)
        
        driver_config = get_current_driver_config()
            
        result['driver_config'] = driver_config
        return echo_json(0,'success',result)
    
    def update_my_profile(self):
        """ 更新司机个人资料
        Args:
            : 
        Return:
            None
        @date:   2025/04/20 23:38:57
        @author: snz
            
        """
        driver_id = get_param_by_json('id')
        truename = get_param_by_json('truename')
        sex = get_param_by_json('sex')
        birthday = get_param_by_json('birthday')
        bank_name = get_param_by_json('bank_name')
        bank_card = get_param_by_json('bank_card')
        
        data = {
            'truename': truename,
            'sex': sex,
            'birthday': birthday,
            'bank_name': bank_name,
            'bank_card': bank_card,
            'updated_at': get_current_time()
        }
        ret = self._db.update_driver_info(driver_id,data)
        if ret is None:
            return echo_json(-1,'更新失败')
        
        return echo_json(0,'更新成功')
    
    def driver_take_cash_list(self):
        """ 提现记录
        Args:
            : 
        Return:
            None
        @date:   2025/04/20 23:38:57
        @author: snz
            
        """
        driver_id = get_param_by_int('driver_id')
        if driver_id <= 0:
            return echo_json(-1,'参数错误')        
        # 当前的我帐户余额
        balance = self.account_db.get_driver_balance_by_id(driver_id)
        
        sql = f"select * from ls_driver_take_cash where driver_id = {driver_id} order by id desc"
        result = self._db._query_sql(sql)
        
        return echo_json(0,'success',result,{'balance':balance})
    
    def get_driver_account_detail(self):
        """ 获取司机帐户明细(收入明细)
        Args:
            : 
        Return:
            None
        @date:   2025/04/20 23:38:57
        @author: snz
            
        """
        btime = get_param_by_str('btime')
        etime = get_param_by_str('etime')
        driver_id = get_param_by_int('driver_id')
        if driver_id <= 0:
            return echo_json(-1,'参数错误')        
        result,num,fee = self.account_db.get_driver_account_detail(driver_id,btime,etime)
        return echo_json(0,'success',result,{'num':num,'fee':fee})
    
    def get_my_order_total_data(self,driver_id,work_status=None):
        """ 获取司机的订单总数据,这里每20秒会接一次更新
        Args:
            driver_id: 司机ID
            work_status: 工作状态
        Return:
            None
        @date:   2025/04/09 15:36:31
        @author: snz
            
        """

        # 更新司机在线时长
        if work_status is not None:
            self._db.update_driver_online_time(driver_id,work_status)
                        
        # 当天收入，支出
        _account = DriverAccountDb()
        bgime,etime = get_day_time_range()
        in_pay,out_pay = _account.total_account_by_id(driver_id,bgime,etime)
        total_inpay,total_out_pay = _account.total_account_by_id(driver_id)
        
        today_commission = 0
        today_total_fee = 0
        today_distance = 0
        today_distance = 0
        # 当日订单数据
        sql = f"select count(id) as num,sum(total_fee) as total_fee,sum(driver_commission) as commission,sum(distance) as distance from ls_order where driver_id = {driver_id} and status in ({ORDER_STATUS.COMPLETED},{ORDER_STATUS.ARRIVED_NO_PAY}) and order_time >= '{bgime}' and order_time <= '{etime}'"
        ret = _account._query_sql_one(sql)
        if ret:
            order_num = ret['num']
            # 当天佣金，订单总额
            today_commission = ret['commission'] if ret['commission'] else 0
            today_total_fee = ret['total_fee'] if ret['total_fee'] else 0
            # 里程
            today_distance = ret['distance'] if ret['distance'] else 0
            today_distance = round(float(today_distance) / 1000,1)
        else:
            order_num = 0
        
            
        # 当订单数据
        total_commission = 0
        total_total_fee = 0
        # 里程
        total_distance = 0
        total_distance = 0
        # 完成及未支付的都算今天完单记录
        sql = f"select count(id) as num,sum(total_fee) as total_fee,sum(driver_commission) as commission ,sum(distance) as distance from ls_order where driver_id = {driver_id} and status in ({ORDER_STATUS.COMPLETED},{ORDER_STATUS.ARRIVED_NO_PAY}) and order_time >= '{bgime}' and order_time <= '{etime}'"
        ret = _account._query_sql_one(sql)
        if ret:
            # 当天佣金，订单总额
            total_order_num = ret['num']
            total_commission = ret['commission'] if ret['commission'] else 0
            total_total_fee = ret['total_fee'] if ret['total_fee'] else 0
            # 里程
            total_distance = ret['distance'] if ret['distance'] else 0
            total_distance = round(float(total_distance) / 1000,1)
        else:
            total_order_num = 0
      
        # 当天投诉
        sql = f"select count(id) as num from ls_order_complaint where driver_id = {driver_id} and created_at >= '{bgime}' and created_at <= '{etime}'"
        ret = _account._query_sql_one(sql)
        if ret:
            complaint_num = ret['num']
        else:
            complaint_num = 0
            
        # 总投诉
        sql = f"select count(id) as num from ls_order_complaint where driver_id = {driver_id}"
        ret = _account._query_sql_one(sql)
        if ret:
            total_complaint_num = ret['num']
        else:
            total_complaint_num = 0
            
        # 总在线时长，服务分
        score = 0
        online_total_time = 0
        work_status = 0
        today_online_total_time = 0
        total_online_time = 0
        row = self._db.get_user_info_by_id(driver_id,"score,online_total_time,work_status")
        if row:        
            score = self._db.get_driver_service_score(driver_id)
            online_total_time = row['online_total_time'] # app端在线时长
            online_total_time = online_total_time if online_total_time else 0
            work_status = row['work_status']
            today_online_total_time = int_ex(row['today_online_total_time']) # 当天在线时长
            total_online_time = int_ex(row['total_online_time']) # 总在线时长
            
        data = {
            'in_pay': in_pay,
            'total_in_pay': total_inpay,
            'out_pay': out_pay,
            'total_out_pay': total_out_pay,
            'order_num': order_num,
            'total_order_num': total_order_num,
            'score': score,
            'online_total_time': online_total_time,
            'today_online_total_time': today_online_total_time,
            'total_online_time': total_online_time,
            'work_status': work_status,
            'commission': today_commission,
            'total_fee': today_total_fee,
            'complaint_num': complaint_num,
            'distance': today_distance,
            'total_distance': total_distance,
            
            'total_commission': total_commission,
            'total_total_fee': total_total_fee,
            'total_complaint_num': total_complaint_num,
            
            }
        
        return echo_json(status=0,data=data)
    
    def get_today_order(self,driver_id):
        #当天完单
        # 当天收入，支出
        _account = DriverAccountDb()
        bgime,etime = get_day_time_range()
        in_pay,out_pay = _account.total_account_by_id(driver_id,bgime,etime)
        
        # 当日订单数据
        #sql = f"select * from ls_order where driver_id = {driver_id} and status = {ORDER_STATUS.COMPLETED} and order_time >= '{bgime}' and order_time <= '{etime}'"
        sql = f"select * from ls_order where driver_id = {driver_id} and status in ({ORDER_STATUS.COMPLETED},{ORDER_STATUS.ARRIVED_NO_PAY}) and order_time >= '{bgime}' and order_time <= '{etime}'"
        ret = _account._query_sql(sql)
        return echo_json(0,in_pay,ret)
    
    def get_today_incom_data(self):
        # 今天赚了
        bgime,etime = get_day_time_range()
        driver_id = get_param_by_int('driver_id')
        if driver_id <= 0:
            return echo_json(-1,'参数错误')
        

    def get_heatmap_data(self):
        # 获取热力图数据
        return self.app_total_controller.get_heatmap_data()
    
    def get_order_total_by_day(self):
        # 获取当天及指定前后天数据的订单统计数据
        return self.app_total_controller.get_order_total_by_day()
    
    def get_score_list(self):
        # 获取司机的服务分列表
        driver_id = get_param_by_int('driver_id')
        if driver_id <= 0:
            return echo_json(-1,'参数错误')
                
        result = self._db.get_driver_service_score_list(driver_id)
        
        return echo_json(0,'success',result)
    
    def set_driver_accept_order_model(self):
        # 设置司机的接单模式
        driver_id = int_ex(get_param_by_json('driver_id'))
        if driver_id <= 0:
            return echo_json(-1,'参数错误')
        
        air = int_ex(get_param_by_json('air'))
        train = int_ex(get_param_by_json('train'))
        
        destination = get_param_by_json('destination')
        latlng = get_param_by_json('latlng')
        match_ratio = get_param_by_json('match_ratio')
        # 构造存储顺路单格式，在driver_find查找司机时使用
        if destination != '' and latlng != '':
            destination = destination + "#" + latlng + "#" + str(match_ratio)
        else:
            destination = ''
        
        accept_order_model = int_ex(get_param_by_json('accept_order_model'))
        if accept_order_model not in [0,1]:
            return echo_json(-1,'参数错误')
        
        # 0=系统接单，1=手动接单
        self._db.update_driver_info(driver_id,{'accept_order_model': accept_order_model,'no_air': air, 'no_train': train,'on_way_address': destination})
        
        return echo_json(0,'success')
    
    def get_order_by_id(self):
        # 获取订单详情
        order_id = get_param_by_int('order_id')
        if order_id <= 0:
            return echo_json(-1,'参数错误')
        
        row = self._order_lib._db.get_order_by_id(order_id)
        return echo_json(0,'success',row)
    
    def reward_list(self):
        # 司机奖励列表，目前暂无
        driver_id = int_ex(get_param_by_json('driver_id'))
        if driver_id <= 0:
            return echo_json(-1,'参数错误')
        
        return echo_json(0,'success',[])
    
    def pwd_setup(self):
        #  修改密码
        driver_id = int_ex(get_param_by_int('driver_id'))
        if driver_id <= 0:
            return echo_json(-1,'参数错误')
        
        old_pwd = get_param_by_str('old_pwd')
        new_pwd = get_param_by_str('new_pwd')
        confirm_pwd = get_param_by_str('confirm_pwd')
        if new_pwd != confirm_pwd:
            return echo_json(-1,'密码不一致')

        password = gen_md5(old_pwd)
        sql = f"select id from ls_driver where id = {driver_id} and password = '{password}'"
        ret = self._db._query_sql_one(sql)
        if ret is None:
            return echo_json(-1,'原密码错误')
        
        new_pwd = gen_md5(new_pwd)
        sql = f"update ls_driver set password = '{new_pwd}' where id = {driver_id}"
        ret = self._db._execute_sql(sql)
        return echo_json(0,'success',ret)
    
    def edit_phone(self):
        driver_id = int_ex(get_param_by_int('driver_id'))
        if driver_id <= 0:
            return echo_json(-1,'参数错误')
        
        old_phone = get_param_by_str('old_phone')
        new_phone = get_param_by_str('new_phone')

        sql = f"select id from ls_driver where phone = '{old_phone}' and id = {driver_id}"
        ret = self._db._query_sql_one(sql)
        if ret is None:
            return echo_json(-1,'原手机号不存在')
        
        sql = f"update ls_driver set phone = '{new_phone}', username='{new_phone}' where id = {driver_id}"
        ret = self._db._execute_sql(sql)
        if ret is not None:
            return echo_json(0,'success',ret)
        
        return echo_json(-1,'修改失败')
    
    def change_car(self):
        driver_id = int_ex(get_param_by_int('driver_id'))
        if driver_id <= 0:
            return echo_json(-1,'参数错误')
        car_no = get_param_by_str('plateNumber')
        brand = get_param_by_str('brand')
        model = request.form.get('model')
        color = request.form.get('color')
        register_date = request.form.get('registerDate')
        licenseImage = get_param_by_str('licenseImage')

        # 获取数组字段
        car_images = request.form.getlist('carImages[]')  # 获取所有 carImages 参数值为列表
        car_images = "#".join(car_images)
        
        sql = f"insert into ls_driver_car_change(driver_id,car_no,brand,model,color,register_date,licenseImage,car_img) values(%s,%s,%s,%s,%s,%s,%s,%s)"
        ret = self._db._execute_sql(sql, (driver_id, car_no, brand, model, color, register_date, licenseImage, car_images))
        if ret:
            return echo_json(0, 'success', ret)
        
        return echo_json(-1,'申请更换失败')

