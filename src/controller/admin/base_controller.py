# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

from flask import request,session
from src.helper.helper import *
from src.helper.upload_service import UploadService

class BaseController():
     def __init__(self) -> None:
          pass

     def img_post(self,tmp_path = ''):
        ''' 图片上传
            Args:
                : 多文件数组
                : 临时保存目录
            Return: 
                上传的文件列表
            @date:   2024/09/29 18:06:38
            @author: snz
        '''
        
        filer_tager=request.files
        imgs = []
        for _file in filer_tager:
            ret = UploadService.UploadByFile(filer_tager[_file],tmp_path)
            if ret["code"] != 200:
                continue
        
            imgs.append(ret['data']['file_key'])
            
        return imgs

     def get_uid(self):
            ''' 获取当前登录的用户ID
                Parameters:
                    is_stop: True=未登录时停止执行，并输出json至客户端，False=未登录时返回0值
                Returns: 
                    is_stop=True时未登录则停止并输出json提示， False=未登录时返回0值
                @date:   2024/03/22 20:11:06
                @author: snz
            '''
            
            uid = session.get('uid')
            if uid is None or uid <= 0:
                return 0
            
            return uid
    
     def IsAdmin(self):
          """是否为管理员，True是"""
          if session.get('is_admin') == 999:
               return True
          return False
     
     def IsAllowLoginManager(self):
         '''
            是否为允许后台登录
         '''
         if session.get('is_admin') in [111,999]:
              return True
         
         return False
     
     def IsLogin(self):
         """后台用户是否已经登录
         """
         if not self.IsAllowLoginManager():
             return 0
         
         uid = self.get_uid()
         if uid > 0 and session.get('status') != -1:
             return uid
         
         return 0