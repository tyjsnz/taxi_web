# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 


from flask import session,request,redirect,url_for
from src.helper.helper import *
from src.controller.admin.base_controller import *
from src.model.base_db import PublicDbConnection
from src.helper.sms_helper import SmsHelper
from src.common.const_defined import ORDER_STATUS,DRIVER_ACCEPT_ORDER_STATUS
from src.common.websocket_manager import send_message_to_target_client

class OrderController(BaseController):
    def __init__(self):
        super().__init__()
        self.db = PublicDbConnection()

    def get_one(self):
        id = get_param_by_int('id')
        sql = f"select * from v_order where id = {id}"
        return self.db._query_sql_one(sql)
    
    def get_order_list(self):
        """ 订单列表直接查看是没有flag标识
            司机查看时标识为：driver,且通过car_no来作为条件查询，
            佣金列表中查询订单是标识为：comission，以car_no为条件查询
            乘客订单查看时标识为：customer，以phone来作为标识查询
            Args:
                : 
            Return: 
                None
            @date:   2025/04/19 16:33:57
            @author: snz
        """
        
        # 订单列表，司机、乘客、佣金管理也需要取订单列表
        page ,pagesize = get_page_param()
        page = int(page) - 1 if page >=1 else 0
        limit = get_page_param_ex(50)

        flag = get_param_by_str('flag')

        sn = get_param_by_str('sn')
        phone = get_param_by_str('phone')
        car_no = get_param_by_str('car_no')
        status = get_param_by_str('status')
        company_id = get_param_by_str('company_id')
        driver_phone = get_param_by_str('driver_phone')
        
        where = "id > 1"
        if company_id != '':
            where += f" and company_id={company_id}"
        if sn != '':
            where += f" and sn like '{sn}%'"
        if phone != '':
            where += f" and customer_phone='{phone}'"
        if car_no != '':
            car_no = car_no.upper()
            where += f" and car_no like '{car_no}%'"

        # 如是司机或佣金页进入时只有car_no条件
        if flag == 'driver' or flag == 'comission':
            if car_no != '':
                car_no = car_no.upper()
                where = f"car_no like '{car_no}%'"
            else:
                return echo_json(-1,'car_no is null')
        elif flag == 'customer':
            # 乘客页查询，只有电话的条件
            if phone != '':
                where = f"customer_phone='{phone}'"
            else:
                return echo_json(-1,'phone is null')
        # 订单状态
        if status != '':
            where += f" and status={status}"
            
        # 司机电话
        if driver_phone != '':
            where += f" and driver_phone='{driver_phone}'"
            
        btime = get_param_by_str('btime')
        etime = get_param_by_str('etime')
        if btime != '' and etime != '':
            where += f" and order_time >= '{btime}' and order_time <= '{etime}'"

        sql =f"select * from v_order where {where} order by id desc {limit}"
        result = self.db._query_sql(sql)

        # total
        sql = f"select count(1) as total from v_order where {where}"
        ret = self.db._query_sql_one(sql)
        total = ret['total'] if ret is not None else 0
        return echo_json(0,'',result,{'total': total})
    
    def taxi_fee_setting(self):
        # 增加计价规则
        title = get_param_by_json('title')
        start_time = get_param_by_json('start_time')
        end_time = get_param_by_json('end_time')
        start_fee = get_param_by_json('start_fee')
        start_mileage = get_param_by_json('start_mileage')
        mileage_fee_per_km = get_param_by_json('mileage_fee_per_km')
        long_distance_trigger_mileage = get_param_by_json('long_distance_trigger_mileage')
        long_distance_fee_per_km = get_param_by_json('long_distance_fee_per_km')
        duration_fee_per_minute = get_param_by_json('duration_fee_per_minute')

        data = {
            'title': title,
            'start_time': start_time,
            'end_time': end_time,
            'start_fee': start_fee,
            'start_mileage': start_mileage,
            'start_mileage': start_mileage,
            'mileage_fee_per_km': mileage_fee_per_km,
            'long_distance_trigger_mileage': long_distance_trigger_mileage,
            'long_distance_fee_per_km': long_distance_fee_per_km,
            'duration_fee_per_minute': duration_fee_per_minute,
        }
        id = self.db.insert_data_by_dict('ls_taxi_fee_settings',data)
        if id > 0:
            return echo_json(0)
        
        return echo_json(-1,'添加失败')
    
    def taxi_fee_del(self):
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(-1,'id error')
        
        sql = f"delete from ls_taxi_fee_settings where id={id}"
        ret = self.db._execute_sql(sql)
        if ret:
            return echo_json(0)
        return echo_json(-1,'删除失败')
    
    def send_order_sms(self):
        """ 发送订单短信
            Args:
                : 
            Return: 
                None
            @date:   2025/04/19 16:33:57
            @author: snz
        """
        ids = get_param_by_str('ids')
        if ids == '':
            return echo_json(-1,'ids is null')
        ids = ids.replace('#',',')
        template_id = get_param_by_int('template_id')
        if template_id <= 0 or template_id > 4:
            return echo_json(-1,'template_id is null')
        
        content = get_param_by_str('content')
        
        sms_tpl =[
            '尊敬的乘客，您好！您于 {乘车日期} 乘坐的 {车牌号} 行程费用尚未支付。请您尽快完成支付，以免影响后续使用。如有疑问，可联系客服{电话}。感谢您的理解与支持',
            '尊敬的乘客，您好！您的订单 {订单号} 已逾期多日未支付，根据平台规定，可能影响您的信用评级及后续叫车服务。请尽快完成支付，如有特殊情况，请及时联系客服{电话}。',
            '尊敬的乘客，您好！很遗憾通知您，您的订单 {订单号} 欠款已逾期{逾期天数}天未处理。我们已多次提醒，但仍未收到支付。若继续拖欠，平台将按规定采取进一步措施（如法律途径），同时影响您在平台的所有权益。请立即处理，以免造成不必要的麻烦。'
        ]
        
        site_config = get_current_site_config()
        service_phone = site_config.get('service_phone', '')
        
        tpl = sms_tpl[0]
        if template_id == 4:
            tpl = content
        else:
            tpl = sms_tpl[template_id - 1]
            
        sql = f"select sn,order_time,total_fee,customer_phone,car_no from ls_order where id in ({ids})"
        result = self.db._query_sql(sql)
        if not result:
            return echo_json(-1,'没有找到订单')
        
        for row in result:
            # 替换模板中的占位符
            order_time = row['order_time']
            order_time = order_time.split(' ')[0]  # 只取日期部分
            order_time = order_time.replace('-', '年', 1).replace('-', '月') + '日'
            tpl = tpl.replace('{乘车日期}', order_time)
            tpl = tpl.replace('{车牌号}', row['car_no'])
            tpl = tpl.replace('{订单号}', row['sn'])
            tpl = tpl.replace('{电话}', service_phone)
        
            days = diff_days(row['order_time'], get_current_time())  # 计算逾期天数
            tpl = tpl.replace('{逾期天数}', str(days))  # 逾期天数可以根据实际情况计算
            tpl = tpl.replace(' ','')
            
            # 发送短信
            ret = SmsHelper.SendOrderSms(row['customer_phone'], tpl)
            if ret['code'] != 0:
                return echo_json(-1, ret['msg'])
            
        return echo_json(0, '短信发送成功')
    
    def cancel_order(self):
        """ 取消订单
            Args:
                : 
            Return: 
                None
            @date:   2025/04/19 16:33:57
            @author: snz
        """
       
        order_id = get_param_by_int('order_id')
        if order_id <= 0:
            return echo_json(-1,'order_id is null')
        
        sql = f"select driver_id,sn,start_location,end_location from ls_order where id={order_id}"
        result = self.db._query_sql_one(sql)
        if not result:
            return echo_json(-1,'订单不存在')
        # 取消订单
        self.db.update_data_by_id('ls_order', {'status': ORDER_STATUS.CANCELED, 'updated_at': get_current_time()},order_id)
        
        driver_id = result['driver_id']
        sql = f"select * from ls_driver where id={driver_id}"
        driver = self.db._query_sql_one(sql)
        if driver:
            self.db.update_data_by_id('ls_driver', {'accept_order_status': DRIVER_ACCEPT_ORDER_STATUS.NO_ACCEPT},driver_id)
            # 发送取消订单消息给司机            
            send_message_to_target_client(driver['token'],{'flag': 'cancel_order', 'target_token': driver['token'], 'order_id': order_id, 'msg': f"订单{result['sn']}已被取消"})            
            
        return echo_json(0, '订单已取消')