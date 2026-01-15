# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file    :   db_service.py
@date    :   2025/02/21 17:41:37
@author  :   snz
@version :   1.0
@email   :   274043505@qq.com
@copyright:   Copyright (C) kmlskj All Rights Reserved.
@desc    :   数据库服务（统计数据）

'''
import pymysql
from datetime import datetime
from loguru import logger
from settings import DatabaseConfig

class DBService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        super().__init__()
        
        # Initialize the database connection
        self.connection = pymysql.connect(
            host = DatabaseConfig.HOST,
            user = DatabaseConfig.USER,
            password = DatabaseConfig.PASSWORD,
            database = DatabaseConfig.DB,
            port = DatabaseConfig.PORT,
            charset='utf8mb4'
        )
        
    def _query(self, query, params=None):
        with self.connection.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            try:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
            except Exception as e:
                print(f"An error occurred: {e}")
                return None
            finally:
                cursor.close()
            
    def _query_one(self, query, params=None):
        with self.connection.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            try:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result
            except Exception as e:
                print(f"An error occurred: {e}")
                return None
            finally:
                cursor.close()
            
    def _execute_sql(self, sql, params=None):
        with self.connection.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
            try:
                cursor.execute(sql, params)
                if sql.upper().find("INSERT") != -1:
                    result = cursor.lastrowid
                else:
                    # 删除语句时候返回影响行数            
                    result = cursor.rowcount
                self.connection.commit()
            except Exception as e:
                print(e)
                self.connection.rollback()
                return None            
            finally:
                cursor.close()
        
        return result
    
    def total_hours_order_data(self):
        """统计每小时的订单数据
        """
        delete_sql = """
        DELETE FROM ls_order_hours_total WHERE DATE(created_at) = CURDATE();
        """
        self._execute_sql(delete_sql)
        
        # 只统计有数据的小时
        select_sql = """
        SELECT
            DATE_FORMAT(created_at, '%H') AS HOUR, #时间
            COUNT(*) AS total_num, # 总数
            SUM(total_fee) AS total_fee, # 总金额
            COUNT(CASE WHEN STATUS = 5 THEN 1 END) AS completed_num, # 已完成数
            SUM(CASE WHEN STATUS = 5 THEN total_fee ELSE 0 END) AS completed_fee,
            COUNT(CASE WHEN STATUS = - 1 THEN 1 END) AS cancel_num, # 取消数
            SUM(CASE WHEN STATUS = - 1 THEN total_fee ELSE 0 END) AS cancel_fee,
            COUNT(CASE WHEN STATUS = - 2 THEN 1 END) AS no_driver_num, # 无司机接单数
            SUM(CASE WHEN STATUS = - 2 THEN total_fee ELSE 0 END) AS no_driver_fee
            FROM
            ls_order
            WHERE
            DATE(created_at) = CURDATE()
            GROUP BY
            HOUR
            ORDER BY
            HOUR;
        """
        
        # 步骤二：查询订单统计数据，当前时段没有记录也返回0
        select_sql = """
         SELECT
            h.hour AS HOUR,
            COALESCE(o.total_num, 0) AS total_num,
            COALESCE(o.total_fee, 0) AS total_fee,
            COALESCE(o.completed_num, 0) AS completed_num,
            COALESCE(o.completed_fee, 0) AS completed_fee,
            COALESCE(o.cancel_num, 0) AS cancel_num,
            COALESCE(o.cancel_fee, 0) AS cancel_fee,
            COALESCE(o.no_driver_num, 0) AS no_driver_num,
            COALESCE(o.no_driver_fee, 0) AS no_driver_fee
            FROM
            (
                SELECT '00' AS hour UNION SELECT '01' UNION SELECT '02' UNION SELECT '03' UNION
                SELECT '04' UNION SELECT '05' UNION SELECT '06' UNION SELECT '07' UNION
                SELECT '08' UNION SELECT '09' UNION SELECT '10' UNION SELECT '11' UNION
                SELECT '12' UNION SELECT '13' UNION SELECT '14' UNION SELECT '15' UNION
                SELECT '16' UNION SELECT '17' UNION SELECT '18' UNION SELECT '19' UNION
                SELECT '20' UNION SELECT '21' UNION SELECT '22' UNION SELECT '23'
            ) h
            LEFT JOIN (
            SELECT
                DATE_FORMAT(created_at, '%H') AS HOUR,
                COUNT(*) AS total_num,
                SUM(total_fee) AS total_fee,
                COUNT(CASE WHEN STATUS = 5 THEN 1 END) AS completed_num,
                SUM(CASE WHEN STATUS = 5 THEN total_fee ELSE 0 END) AS completed_fee,
                COUNT(CASE WHEN STATUS = -1 THEN 1 END) AS cancel_num,
                SUM(CASE WHEN STATUS = -1 THEN total_fee ELSE 0 END) AS cancel_fee,
                COUNT(CASE WHEN STATUS = -2 THEN 1 END) AS no_driver_num,
                SUM(CASE WHEN STATUS = -2 THEN total_fee ELSE 0 END) AS no_driver_fee
            FROM
                ls_order
            WHERE
                DATE(created_at) = CURDATE()
            GROUP BY
                HOUR
            ) o ON h.hour = o.HOUR
            ORDER BY
            h.hour;
        """
        
        result = self._query(select_sql)
        if not result:
            return None
        
        # 步骤三：插入到目标表
        insert_sql = """
        INSERT INTO ls_order_hours_total (order_num, order_fee, hour, completed_num,completed_fee,cancel_num,cancel_fee,no_driver_num,no_driver_fee,created_at)
        VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s,%s)
        """
        
        now = datetime.now()
        for row in result:
            order_num = row['total_num']
            order_fee = row['total_fee']
            hour = row['HOUR']
            completed_num = row['completed_num']
            completed_fee = row['completed_fee']
            cancel_num = row['cancel_num']
            cancel_fee = row['cancel_fee']
            no_driver_num = row['no_driver_num']
            no_driver_fee = row['no_driver_fee']
            created_at = now.strftime('%Y-%m-%d %H:%M:%S')
            
            self._execute_sql(insert_sql, (order_num, order_fee, hour, completed_num, completed_fee, cancel_num, cancel_fee, no_driver_num, no_driver_fee, created_at))
            
        logger.info("订单统计数据已完成")
        
if __name__ == "__main__":
    db_service = DBService()
    db_service.total_hours_order_data()