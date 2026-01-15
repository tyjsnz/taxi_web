# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   driver_location_db.py
@date     :   2025/03/21 19:45:52
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   司机位置数据库操作，注意只维护司机的最后一个位置，应该在登录上班后记录，下班后清空此司机记录，
            防止数据库记录过多情况
'''
from src.model.base_db import PublicDbConnection
from src.helper.helper import *
class DriverLocationDb(PublicDbConnection):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self) -> None:
        super().__init__()
        self._tbname = "ls_driver_location"

    def clear_driver_location(self, driver_id):
        """ 清空司机位置
            Args:
                driver_id: 司机id
            Return: 
                None
            @date:   2025/03/21 19:47:21
            @author: snz
        """
        sql = f"delete from {self._tbname} where driver_id={driver_id}"
        return self._execute_sql(sql)
    
    def insert_driver_location(self, driver_id, lng,lat, address):
        """ 插入司机位置，如存在则更新最后的位置
            Args:
                driver_id: 司机id
                lng: 位置
                lat: 位置
            Return: 
                插入的数据ID
            @date:   2025/03/21 19:47:21
            @author: snz
        """

        row = self._query_sql_one(f"select id from {self._tbname} where driver_id={driver_id}")
        if row:
            sql = f"update {self._tbname} set location=POINT({lng},{lat}),address='{address}',updated_at='{get_current_time()}',latlng='{lat},{lng}' where driver_id={driver_id}"
            return self._execute_sql(sql)
        else:
            sql = f"insert into {self._tbname} (driver_id,location,address,latlng,updated_at) values({driver_id},POINT({lng},{lat}),'{address}','{lat},{lng}','{get_current_time()}')"
            return self._execute_sql(sql)
        
    def find_nearby_drivers(self, start_longitude, start_latitude, distance, minute=5,reject_driver_ids=None,company_ids=''):
        """ 查询附近的司机
            Args:
                start_longitude: 打车用户所在目标经度
                start_latitude: 打车用户所在目标纬度
                distance: 查询范围多少米（半径）
                minute: 查询多少分钟内有定位的记录
                reject_driver_ids: 不需要查询的司机id列表，如：[1,2,3]
                company_ids: 查询指定公司下的司机,id列表 1,2,3
            Return: 
                None
            @date:   2025/03/21 19:47:21
            @author: snz
        """
        company_where = ''
        if company_ids != '':
            company_where = f"AND company_id IN ({company_ids})"

        if reject_driver_ids:
            query = f"""
                SELECT 
                    driver_id,
                    ST_X(location) AS longitude,
                    ST_Y(location) AS latitude,
                    updated_at,
                    ST_DISTANCE_SPHERE(
                        location,
                        POINT({start_longitude}, {start_latitude})
                    ) AS distance
                FROM 
                    {self._tbname}
                WHERE 
                    driver_id NOT IN ({','.join(map(str, reject_driver_ids))})
                    {company_where}
                    AND ST_DISTANCE_SPHERE(
                        location,
                        POINT({start_longitude}, {start_latitude})
                    ) <= {distance}
                    AND updated_at >= NOW() - INTERVAL {minute} MINUTE AND status = 1;
            """
        else:
            query = f"""
                SELECT 
                    driver_id,
                    ST_X(location) AS longitude,
                    ST_Y(location) AS latitude,
                    updated_at,
                    ST_DISTANCE_SPHERE(
                        location,
                        POINT({start_longitude}, {start_latitude})
                    ) AS distance
                FROM 
                    {self._tbname}
                WHERE 
                    ST_DISTANCE_SPHERE(
                        location,
                        POINT({start_longitude}, {start_latitude})
                    ) <= {distance}
                    {company_where}
                    AND updated_at >= NOW() - INTERVAL {minute} MINUTE AND status = 1;
            """

        # 测试使用
        #query = f"SELECT driver_id, X(location) AS longitude, Y(location) AS latitude, updated_at, ST_DISTANCE_SPHERE( location, POINT({start_longitude}, {start_latitude}) ) AS distance FROM ls_driver_location WHERE status=1 ORDER BY RAND() limit 10;"
        # status 状态为：0=下班状态，1=上班状态，2=休息状态，3=接送乘客状态，故司机在每次上传位置时，要更新当前状态，以便于查找
        return self._query_sql(query)