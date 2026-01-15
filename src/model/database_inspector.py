# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   database_inspector.py
@date     :   2025/03/08 21:36:59
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   数据库表结构检查
'''

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import DatabaseConfig
import pymysql

class DatabaseInspector:
    def __init__(self):
        self.connection = pymysql.connect(
            host=DatabaseConfig.HOST,
            user=DatabaseConfig.USER,
            password=DatabaseConfig.PASSWORD,
            db=DatabaseConfig.DB,
            charset=DatabaseConfig.CHARSET,
            port=DatabaseConfig.PORT,
            cursorclass=pymysql.cursors.DictCursor
        )

    def list_tables(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            return [table['Tables_in_' + DatabaseConfig.DB] for table in tables]

    def describe_table(self, table_name):
        with self.connection.cursor() as cursor:
            cursor.execute(f"DESCRIBE {table_name}")
            return cursor.fetchall()

    def close_connection(self):
        self.connection.close()

if __name__ == "__main__":
    inspector = DatabaseInspector()
    print(inspector.list_tables())
    print(inspector.describe_table('ls_drive'))
    inspector.close_connection()