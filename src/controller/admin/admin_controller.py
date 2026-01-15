# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 
from src.helper.helper import *
from src.controller.admin.base_controller import *
from src.common.const_defined import ORDER_STATUS,USER_STATUS
from src.model.base_db import PublicDbConnection
import json
class AdminController(BaseController):
    def __init__(self):
        super().__init__()
        self.db = PublicDbConnection()
        
    def upload_sys_setup_img(self):
        # 上传系统设置图片
        imgs = self.img_post('sys_setup_img')
        if len(imgs) <= 0:
            return echo_json(1,'upload failed')
        
        return echo_json(0,'success',imgs[0])
    def get_system_setup(self):
        row = self.db._query_sql_one(f"select * from ls_sys_config limit 1",use_cache=False)
        if row is None:
            return None
        
        if row['driver_config']:
            row['driver_config'] = json.loads(row['driver_config'])
        if row['customer_config']:
            row['customer_config'] = json.loads(row['customer_config'])
        if row['site_config']:
            row['site_config'] = json.loads(row['site_config'])
        return row
    def system_setup(self):
        # 系统乘客订单及司机订单设置
        _type = get_param_by_json('type')
        if _type == '' or _type is None:
            return echo_json(1,'type is required')
        
        if _type not in ['customer','driver','system']:
            return echo_json(1,'type is required')
        
        row = self.db._query_sql_one(f"select * from ls_sys_config limit 1")
        if _type == 'customer':
            data = {
                'timeout': get_param_by_json('timeout'), # 下单超时时长
                'pay_flag': get_param_by_json('pay_flag'), # 1=先付后乘,0=先乘后付
                'pay_limit': get_param_by_json('pay_limit'), # 先乘后付金额上限
                'add_price_limit': get_param_by_json('add_price_limit'), # 加价上限
                'auto_debit': get_param_by_json('auto_debit'), # 委托代扣，暂不用
            }
            data_json = json.dumps(data)
            if row:
                self.db.update_data_by_id('ls_sys_config',{'customer_config': data_json},row['id'])
                return echo_json(0,'success')
            else:
                self.db.insert_data_by_dict('ls_sys_config',{'customer_config': data_json})
        elif _type == 'driver':
            data = {
                "order_dispatch_range": get_param_by_json('order_dispatch_range'),
                "order_dispatch_flag": get_param_by_json('order_dispatch_flag'),
                "order_dispatch_bonus": get_param_by_json('order_dispatch_bonus'),
                "order_reject_score": get_param_by_json('order_reject_score'),
                "order_dispatch_reject_num": get_param_by_json('order_dispatch_reject_num'),
                "cash_limit_up": get_param_by_json('cash_limit_up'),
                "cash_limit_down": get_param_by_json('cash_limit_down'),
                "bad_review_score": get_param_by_json('bad_review_score'),
                "default_review_score": get_param_by_json('default_review_score'),
                "default_review_delay": get_param_by_json('default_review_delay'),
                "odrder_max_seconds": get_param_by_json('odrder_max_seconds'), # 抢单大厅订单拉取时间范围，多少分钟内的订单
                "order_phone_verify": get_param_by_json('order_phone_verify'), # 接乘客时，手机尾号验证
                "order_region_verify": get_param_by_json('order_region_verify'), # 是否开启电子围栏
                "play_voice": get_param_by_json('play_voice'), # 司机端语音播报                
            }
            data_json = json.dumps(data)
            if row:
                self.db.update_data_by_id('ls_sys_config',{'driver_config': data_json},row['id'])
                return echo_json(0,'success')
            else:
                self.db.insert_data_by_dict('ls_sys_config',{'driver_config': data_json})
        elif _type == 'system':
            # 系统设置
            data = {
                # 客服电话
                "service_phone": get_param_by_json('service_phone'),
                # 首页弹窗,1时才会打开，0时不会打开
                "index_popup_flag": get_param_by_json('index_popup_flag'),
                # 弹窗背景
                "ad_img": get_param_by_json("ad_img"),
                # 弹窗链接
                "ad_url": get_param_by_json("ad_url"),
                # 登录 背景
                "login_img": get_param_by_json("login_img"),
                # logo
                "logo": get_param_by_json("logo"),
                # 用户中心背景user_banner
                "user_banner": get_param_by_json("user_banner"),
            }
            data_json = json.dumps(data)
            if row:
                self.db.update_data_by_id('ls_sys_config',{'site_config': data_json},row['id'])
                return echo_json(0,'success')
            else:
                self.db.insert_data_by_dict('ls_sys_config',{'site_config': data_json})
                        
        return echo_json(0,'success')
    
    def get_user_list(self):
        sql = f"select * from ls_user"
        result = self.db._query_sql(sql)
        return echo_json(0,'success',result)
    
    def reset_pwd(self):
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(1,'id is required')
        pwd = gen_md5('123456')
        sql = f"update ls_user set password = '{pwd}' where id = {id}"
        self.db._execute_sql(sql)
        return echo_json(0,'success')
    
    def update_status(self):
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(1,'id is required')
        status = get_param_by_int('status')
        
        ret = self.db.update_data_by_id('ls_user',{'status':status},id)
        if ret:
            return echo_json(0,'success')
        return echo_json(1,'failed')
    
    def get_one(self):
        id = self.get_uid()
        if id <= 0:
            return echo_json(1,'id is required')
        sql = f"select * from ls_user where id = {id}"
        result = self.db._query_sql_one(sql)
        return result
    
    def update(self):
        id = self.get_uid()
        truename = get_param_by_str('truename')
        phone = get_param_by_str('phone')
        pwd1 = get_param_by_str('pwd1')
        pwd2 = get_param_by_str('pwd2')
        data = {
            "truename": truename,
            "phone": phone,
        }
        if pwd1 != '' and pwd2 != '' and pwd1 != pwd2:
            return echo_json(1,'两次密码不一致')
        
        if pwd1 != "" and pwd2 != '':
            data['password'] = gen_md5(pwd1)
        
        ret = self.db.update_data_by_id('ls_user',data,id)
        if ret:
            return echo_json(0,'success')
        return echo_json(1,'failed')
    
    def add(self):
        truename = get_param_by_str('truename')
        phone = get_param_by_str('phone')
        pwd1 = get_param_by_str('pwd1')
        pwd2 = get_param_by_str('pwd2')
        username = get_param_by_str('username')
        data = {
            "truename": truename,
            "phone": phone,
            "username": username
        }
        if pwd1 != '' and pwd2 != '' and pwd1 != pwd2:
            return echo_json(1,'两次密码不一致')
        
        if pwd1 != "" and pwd2 != '':
            data['password'] = gen_md5(pwd1)
        else:
            data['password'] = gen_md5('123456')
        
        ret = self.db.insert_data_by_dict('ls_user',data)
        if ret:
            return echo_json(0,'success')
        
        return echo_json(1,'failed')
    
    def delete(self):
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(1,'id is required')
        row = self.db._query_sql_one(f"select * from ls_user where id = {id}")
        if row['is_admin'] == 999:
            return echo_json(-1,'管理员不能删除')
        
        sql = f"delete from ls_user where id = {id}"
        self.db._execute_sql(sql)
        return echo_json(0,'success')
    
    def user_log(self):
        pageindex,pagesize = get_page_param()
        pageindex = pageindex - 1 if pageindex > 0 else 0
        pageindex = pageindex * pagesize
        sql = f"select a.*,b.username,b.truename,b.phone,b.username from ls_user_log as a,ls_user as b where a.uid=b.id order by id desc limit {pageindex},{pagesize}"
        result = self.db._query_sql(sql,use_cache=False)
        
        sql = f"select count(a.id) as num from ls_user_log as a,ls_user as b where a.uid=b.id"
        ret = self.db._query_sql_one(sql,use_cache=False)
        total = ret['num']
        return echo_json(0,'success',result,total)
    
    def clear_user_log(self):
        sql = f"delete from ls_user_log"
        self.db._execute_sql(sql)
        return echo_json(0,'success')