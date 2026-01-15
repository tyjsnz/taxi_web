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
'''登录控制器
'''
class LoginController(BaseController):
    def __init__(self) -> None:
        super().__init__()
        self.__tbname = "ls_user"
        self.db = PublicDbConnection()
    
    def is_login(self):
        '''检查是否已经登录
            Params:
                True: 登录, 反之
        '''
        if session.get('uid') is None:
            return False
        
        if session.get('uid') > 0 and session.get("username") != None:
            return True
        
        return False
    
    def __updateLoginLog(self,id,ip):
        '''更新登录日志'''

        sql = f"insert into ls_user_log(uid,content,ip,created_at) values({id},'登录', '{ip}','{get_current_time()}')"
        return self.db._execute_sql(sql)
    
    def login(self):
        if request.method == 'POST':
            username = request.values.get('username')
            password = request.values.get('password')
                        
            if not all([username,password]):
                return echo_json(-1,"登录信息错误")
            
            ip = request.remote_addr
            password = gen_md5(password)
            sql = f"select * from {self.__tbname} where username='{username}' and password='{password}'"
            row = self.db._query_sql_one(sql)
            
            if row is None or row is False:
                return echo_json(-1, "帐号密码错误")
            if row['is_admin'] not in [111,999]:
                return echo_json(-1,"帐号无权限")
            
            if row['status'] == -1:
                return echo_json(-1,"帐号已停用")
            
            session["username"] = row['username']
            session['uid'] = row['id']
            session['is_admin'] = row['is_admin']
            session['truename'] = row['truename']
            session['phone'] = row['phone']
            session['status'] = row['status']

            self.__updateLoginLog(row['id'],ip)
            
            return echo_json(0, "登录成功")
        
    def logout(self):
        session.clear()
        session['username'] = None
        session['uid'] = None
        session.pop('username',None)
        session.pop('uid',None)
        session['is_admin'] = None
        session['truename'] = None
        session['phone'] = None
        session['status'] = None

        return redirect(url_for('admin_route.login'))
