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
@date     :   2025/02/13 23:41:05
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   司机控制器
'''
from flask import session,request,redirect,url_for
from src.helper.helper import *
from src.controller.admin.base_controller import *
from src.model.driving.driver_db import DriverDb
import struct
from src.common.const_defined import *
from src.controller.web.wechat.libs.driver_location_cache import DriverLocationCache
class DriverController(BaseController):
    def __init__(self):
        super().__init__()
        self.db = DriverDb()
        self.driver_cache = DriverLocationCache()

    def parse_point_binary(self,point_binary):
        # 解析司机位置坐标
        # 解析前 4 个字节（小端序），通常为 1，表示 WKBPoint 类型
        _, byte_order, wkb_type = struct.unpack('<BiI', point_binary[:9])
        if wkb_type == 1:
            # 解析经度和纬度（小端序，双精度浮点数）
            longitude, latitude = struct.unpack('<dd', point_binary[9:])
            return longitude, latitude
        return None, None
    
    def total_driver_data(self):
        # 统计司机数量
        sql = """
        SELECT 
                COUNT(*) AS total,
                COUNT(CASE WHEN work_status = 0 THEN 1 END) AS work_off,
                COUNT(CASE WHEN work_status = 1 THEN 1 END) AS work_on
            FROM ls_driver;
        """
        ret = self.db._query_sql_one(sql)
        _total = ret['total'] if ret else 0
        _work_on = ret['work_on'] if ret else 0
        _work_off = ret['work_off'] if ret else 0
        return {"total":_total,"online_total":_work_on,"offline_total":_work_off}
    def get_car_gps(self):
        """获取在线司机的GPS信息"""
        
        # 在线司机信息
        limit = get_page_param_ex(50)
        sql = f"select a.*,b.truename,b.phone,b.car_no from ls_driver_location as a, ls_driver as b where a.driver_id=b.id and b.work_status={DRIVER_WORK_STATUS.WORK_ON} {limit}"
        
        ret_num = self.db._query_sql_one(f"select count(*) as num from ls_driver_location as a, ls_driver as b where a.driver_id=b.id and b.work_status={DRIVER_WORK_STATUS.WORK_ON}")
        ret_num = ret_num['num'] if ret_num else 0
                        
        result = []
        data = self.db._query_sql(sql)
        for row in data:
            driver_id = row["id"]
            longitude, latitude = 0,0
            # 获取司机的位置信息
            latlng = row['latlng']
            if latlng is not None and latlng != '':
                longitude = round(float_ex(latlng.split(',')[1]),6)
                latitude = round(float_ex(latlng.split(',')[0]),6)
            
        
            result.append({"driver_id":driver_id,"longitude":longitude,"latitude":latitude,'truename': row['truename'],'phone': row['phone'],'car_no': row['car_no']})

        _total = self.total_driver_data()
        return echo_json(0,ret_num,result,_total)
    
    def get_driver_list(self):
        """司机获取"""

        pageindex,pagesize = get_page_param()
        if pageindex > 0:
            pageindex = pageindex - 1
        pageindex = pageindex * pagesize
        name = get_param_by_str('name')
        phone = get_param_by_str('phone')
        company = get_param_by_str('company')
        car_no = get_param_by_str('car_no')
        btime = get_param_by_str('btime')
        etime = get_param_by_str('etime')
        where = 'id > 0'
        if name != '':
            where += f" and truename like '%{name}%'"
        if phone != '':
            where += f" and phone='{phone}'"
        if car_no != '':
            where += f" and car_no='{car_no}'"
        if company != '':
            where += f" and company_id={company}"
        if btime != '' and etime != '':
            if ":" not in btime:
                btime += " 00:00:00"
            if ":" not in etime:
                etime += " 23:59:59"
            where += f" and created_at between '{btime}' and '{etime}'"

        sql = f"select count(id) as num from ls_driver where {where}"
        ret = self.db._query_sql_one(sql)
        num = ret['num']
        
        sql = f"select * from ls_driver where {where} order by created_at desc limit {pageindex},{pagesize}"
        result = self.db._query_sql(sql)
        # 接单数量,优惠券数量
        for row in result:
            sql = f"select count(id) as num,sum(driver_commission) as fee,sum(total_fee) as total_fee from ls_order where driver_id={row['id']} and status={ORDER_STATUS.COMPLETED}"
            ret = self.db._query_sql_one(sql)
            row['order_count'] = ret['num']
            row['total_fee'] = ret['total_fee']
            row['order_commission'] = ret['fee']
            
            sql = f"select count(id) as num from ls_coupons_list where uid={row['id']}"
            ret = self.db._query_sql_one(sql)
            if ret:
                row['coupons_num'] = ret['num']

        return echo_json(0,"",result,num)
    
    def get_car_list(self):
        sql = f"select * from ls_driver"
        ret = self.db._query_sql(sql)
        return echo_json(0,"",ret)
    
    def get_price_list(self):
        # 价格管理
        from datetime import timedelta
        sql = "select a.*,c.name,c.short_name from ls_taxi_fee_settings as a, ls_company as c where a.company_id = c.id"
        ret = self.db._query_sql(sql)
        # 手动转换数据
        for item in ret:
            if isinstance(item.get('start_time'), timedelta):
                item['start_time'] = str(item['start_time'])#.total_seconds()
            if isinstance(item.get('end_time'), timedelta):
                item['end_time'] = str(item['end_time'])#.total_seconds()            
        return echo_json(0,"",ret)
    
    def driver_update_status(self):
        # 更新状态
        status = get_param_by_json('status')
        id = get_param_by_json('id')
        if status not in [USER_STATUS.NORMAL,USER_STATUS.DISABLE]:
            return echo_json(-1,"状态不正确")
        
        self.db.update_driver_info(id,{'status': status})
        return echo_json(0,'success')
    
    def driver_delete(self):
        # 司机删除
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(-1,'id error')
        ret = self.db.delete_driver(id)
        if ret:
            return echo_json(0)
        
        return echo_json(-1,'删除错误')
    
    def get_driver_verify_list(self):
        # 司机注册审核列表
        pageindex,pagesize = get_page_param()
        pageindex = pageindex - 1 if pageindex > 1 else 0
        pageindex = pageindex * pagesize

        name = get_param_by_str('name')
        phone = get_param_by_str('phone')
        car_no = get_param_by_str('car_no')
        btime = get_param_by_str('btime')
        etime = get_param_by_str('etime')
        
        where = 'status <> 1'
        if name != '':
            where += f" and truename like '%{name}%'"
        if phone != '':
            where += f" and phone='{phone}'"
        if car_no != '':
            where += f" and car_no='{car_no}'"
        if btime != '' and etime != '':
            if ":" not in btime:
                btime += " 00:00:00"
            if ":" not in etime:
                etime += " 23:59:59"
            where += f" and created_at between '{btime}' and '{etime}'"

        sql = f"select count(id) as num from ls_driver_register where {where}"
        ret = self.db._query_sql_one(sql)
        num = ret['num']
        
        sql = f"select * from ls_driver_register where {where} order by created_at desc limit {pageindex},{pagesize}"
        result = self.db._query_sql(sql,use_cache=False)
        return echo_json(0,'success',result,num)
    
    def delete_register(self):
        # 删除注册审核
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(-1,'id error')
        
        sql = f"select * from ls_driver_register where id={id}"
        row = self.db._query_sql_one(sql)
        if row is None:
            return echo_json(-1,"记录不存在")
        delete_file(row['id_car_img'])
        delete_file(row['driving_licence'])
        delete_file(row['car_licence'])
        delete_file(row['insure_img'])
        delete_file(row['car_img'])
        
        ret = self.db._execute_sql("delete from ls_driver_register where id=%s",(id,))
        if ret:
            return echo_json(0)
        return echo_json(-1,'删除失败')
    
    def verify_driver_register(self):
        # 注册审核
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(-1,'id error')
        status = get_param_by_int('status')
        remark = get_param_by_str('remark')

        sql = f"select * from ls_driver_register where id={id}"
        row = self.db._query_sql_one(sql,use_cache=False)
        if row is None:
            return echo_json(-1,"记录不存在")
        # 拒绝审核
        if status == -1:
            sql = f"update ls_driver_register set status=-1,remark='{remark}' where id={id}"
            ret = self.db._execute_sql(sql)
            if ret:
                return echo_json(0)
            
            return echo_json(-1,"操作失败")
        elif status == 1:
            # 通过，加至司机表，并删除
            data = {
                'truename': row['truename'],
                'phone': row['phone'],
                'password': gen_md5('123456'),
                'phone': row['phone'],
                'driving_age': row['driving_age'],
                'id_card': row['id_card'],
                'id_card_img': row['id_card_img'],
                'id_card_img1': row['id_card_img1'],                
                'insure_img': row['insure_img'],
                'car_no': row['car_no'],
                'car_age': row['car_age'],
                'car_brand': row['car_brand'],
                'car_color': row['car_color'],
                'car_type': row['car_type'],
                'recommend_uid': row['recommend_uid'],
                'region_id': row['region_id'],
                'created_at': get_current_time(),
            }
            ret = self.db.insert_driver(data)
            if ret is None:
                return echo_json(-1,'审核失败')
            
            sql = f"update ls_driver_register set status=1 where id={id}"
            ret = self.db._execute_sql(sql)
            
            #ret = self.db._execute_sql("delete from ls_driver_register where id=%s",(id,))
            
            # 这里要发短信
            return echo_json(0,"审核成功,登录帐号为：手机号，默认密码123456")
        
    
