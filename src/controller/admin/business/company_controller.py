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
from src.common.const_defined import ORDER_STATUS,USER_STATUS
from src.model.base_db import PublicDbConnection

class CompanyController(BaseController):
    def __init__(self):
        super().__init__()
        self.db = PublicDbConnection()

    def get_one(self):
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(-1,"id为空")
        
        row = self.db._query_sql_one(f"select * from ls_company where id={id}")
        return row

    def add(self):
        # 添加商家
        imgs = self.img_post()
        pic = ''
        if len(imgs) > 0:
            pic = imgs[0]

        if pic != '':
            pic = resize_and_crop_image(pic, (800,600))

        data = {
            'name': get_param_by_str('name'),
            'short_name': get_param_by_str('short_name'),
            'contact': get_param_by_str('contact'),
            'phone': get_param_by_str('phone'),
            'service_phone': get_param_by_str('service_phone'),
            'email': get_param_by_str('email'),
            'region': get_param_by_str('region'),
            'address': get_param_by_str('address'),
            'license_no': get_param_by_str('license_no'),
            'status': get_param_by_str('status'),
            'bz': get_param_by_str('remark'),
            'license_img': pic,
            'created_at': get_current_time(),
            'uid': self.get_uid()
        }
        _id = self.db.insert_data_by_dict('ls_company',data)
        if _id:
            return echo_json(0)
        return echo_json(-1,'添加失败')
    
    def update_status(self):
        # 更新
        id = int(get_param_by_json('id'))
        if id <= 0:
            return echo_json(-1,"id为空")
        status = get_param_by_json('status')
        ret = self.db.update_data_by_id('ls_company',{'status': status},id)
        if ret:
            return echo_json(0,'更新成功')
        
        return echo_json(-1,'更新失败')

    def update(self):
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(-1,"id为空")
        
        imgs = self.img_post()
        pic = ''
        if len(imgs) > 0:
            pic = imgs[0]

        if pic != '':
            pic = resize_and_crop_image(pic, (800,600))

        data = {
            'name': get_param_by_str('name'),
            'short_name': get_param_by_str('short_name'),
            'contact': get_param_by_str('contact'),
            'phone': get_param_by_str('phone'),
            'service_phone': get_param_by_str('service_phone'),
            'email': get_param_by_str('email'),
            'region': get_param_by_str('region'),
            'address': get_param_by_str('address'),
            'license_no': get_param_by_str('license_no'),
            'status': get_param_by_str('status'),
            'bz': get_param_by_str('remark'),
            'created_at': get_current_time(),
            'uid': self.get_uid()
        }
        if pic != '':
            data['license_img'] = pic

        ret = self.db.update_data_by_id('ls_company',data,id)
        if ret:
            return echo_json(0,'更新成功')
        
        return echo_json(-1,'更新失败')
    
    def delete(self):
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(-1,"id为空")
        
        sql = f"select * from ls_company where id={id}"
        row = self.db._query_sql_one(sql)
        if row:
            delete_file(row['license_img'])

        sql = f"delete from ls_company where id={id}"
        ret = self.db._execute_sql(sql)
        if ret:
            return echo_json(0,'删除成功')
        
        return echo_json(-1,'删除失败')
    
    def delete_img(self):
        # 删除图片
        id = get_param_by_int('id')
        if id <= 0:
            return echo_json(-1,"id为空")
        
        row = self.db._query_sql_one(f"select license_img from ls_company where id={id}")
        if row:
            delete_file(row['license_img'])
            self.db.update_data_by_id("ls_company",{'license_img': ''},id)

        return echo_json(0)
    
    def get_list(self):
        pageindex,pagesize = get_page_param()
        pageindex = pageindex - 1 if pageindex > 1 else 0
        pageindex = pageindex * pagesize

        name = get_param_by_str('name')
        phone = get_param_by_str('phone')
        contact = get_param_by_str('contact')
        status = get_param_by_str('status')

        where = 'id > 0'
        if name != '':
            where += f" and name like '%{name}%'"
        if phone != '':
            where += f" and phone='{phone}'"
        if contact != '':
            where += f" and contact='{contact}'"
        if status != '':
            where += f" and status={status}"

        sql = f"select count(id) as num from ls_company where {where}"
        ret = self.db._query_sql_one(sql)
        num = ret['num']

        sql = f"select * from ls_company where {where} limit {pageindex},{pagesize}"
        result = self.db._query_sql(sql)

        for row in result:
            # 司机数量
            sql = f"select count(id) as num from ls_driver where company_id={row['id']}"
            ret = self.db._query_sql_one(sql)
            row['driver_num'] = ret['num']

        return echo_json(0,'success',result,num)
    
    # 佣金
    def get_commission_list(self):
        pageindex,pagesize = get_page_param()
        pageindex = pageindex - 1 if pageindex > 1 else 0
        pageindex = pageindex * pagesize
        
        name = get_param_by_str('name')
        where = 'id > 0'
        if name != '':
            where += f" and name like '%{name}%'"
            
        ret = self.db._query_sql_one(f"select count(id) as num from ls_company where {where}")
        num = ret['num']
        sql = f"select id,name,commission_rate,driver_rate from ls_company where {where} limit {pageindex},{pagesize}"
        result = self.db._query_sql(sql)
        for row in result:
            # 司机数量
            sql = f"select count(id) as num from ls_driver where company_id={row['id']}"
            ret = self.db._query_sql_one(sql)
            row['driver_num'] = ret['num']
           
        
        return echo_json(0,'success',result,num)
    
    def get_commission_driver_list(self):
        # 列机列表
        company_id = get_param_by_int('company_id')
        if company_id <= 0:
            return echo_json(-1,'参数错误')
        
        pageindex,pagesize = get_page_param()
        pageindex = pageindex - 1 if pageindex > 1 else 0
        pageindex = pageindex * pagesize
        
        ret = self.db._query_sql_one(f"select count(id) as num from ls_driver where company_id={company_id}")
        num = 0
        if ret:
            num = ret['num']
        
        sql = f"select id,truename,phone,commission_rate,created_at from ls_driver where company_id={company_id}"
        ret = self.db._query_sql(sql)
        return echo_json(0,'success',ret,num)
    
    def commission_setup(self):
        # 设置加盟商佣金
        id = int(get_param_by_json('id'))
        if id <= 0:
            return echo_json(-1,"id为空")
        
        data = {
            'commission_rate': get_param_by_json('rate'),
            'updated_at': get_current_time(),
            'uid': self.get_uid()
        }
        sync = get_param_by_json('apply_to_drivers')
        if sync == 1:
            data['driver_rate'] = data['commission_rate']
            
        ret = self.db.update_data_by_id("ls_company",data,id)
        if ret:
            sql = f"update ls_driver set commission_rate={data['commission_rate']} where company_id={id}"
            ret = self.db._execute_sql(sql)
            
        return echo_json(0,'更新成功')
    
    def commission_driver_setup(self):
        # 设置司机佣金
        company_id = int(get_param_by_json('company_id'))
        if company_id <= 0:
            return echo_json(-1,"company id为空")
        
        data = {
            'commission_rate': get_param_by_json('rate'),
            'uid': self.get_uid()
        }
        sql = f"update ls_driver set commission_rate={data['commission_rate']},uid={self.get_uid()} where company_id={company_id}"
        ret = self.db._execute_sql(sql)
        if ret:
            return echo_json(0,'更新成功')
        
        return echo_json(-1,'更新失败')