# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

"""
@file    :   heatmap_service.py
@date    :   2025/02/21 18:18:24
@author  :   snz
@version :   1.0
@email   :   274043505@qq.com
@copyright:   Copyright (C) kmlskj All Rights Reserved.
@desc    :   热力图服务，每5分钟更新一次订单数据

"""

# import sys
# import os
# # 获取当前脚本所在目录
# current_dir = os.path.dirname(os.path.abspath(__file__))
# # 获取项目根目录（假设 src 是子目录）
# project_root = os.path.dirname(os.path.dirname(current_dir))

# # 将项目根目录添加到 PYTHONPATH
# if project_root not in sys.path:
#     sys.path.append(project_root)

from src.model.base_db import PublicDbConnection
from datetime import datetime
from src.helper.geo_helper import get_geocode_info
class HeatmapService:
    def __init__(self):
        self.db = PublicDbConnection()

    def get_heatmap_data(self):
        """ 获取热力图数据,统计今天的订单数据
        
        """        
        delete_sql = """
            DELETE FROM ls_order_heatmap WHERE DATE(created_at) = CURDATE();
        """
        self.db._execute_sql(delete_sql)
        
        query = """
            SELECT 
                'start' AS location_type,
                start_latlng AS latlng,
                COUNT(*) AS order_count,
                SUM(total_fee) AS total_fee
            FROM ls_order
            WHERE DATE(created_at) = CURDATE()
            GROUP BY start_latlng

            UNION ALL

            SELECT 
                'end' AS location_type,
                end_latlng AS latlng,
                COUNT(*) AS order_count,
                SUM(total_fee) AS total_fee
            FROM ls_order
            WHERE DATE(created_at) = CURDATE()
            GROUP BY end_latlng;
        """        
        result = self.db._query_sql(query)
        for row in result:
            # 处理数据
            latlng = row['latlng']
            order_count = row['order_count']
            total_fee = row['total_fee']
            location_type = row['location_type']
            
            # 获取地理信息
            geocode_info = get_geocode_info(latlng)
            if geocode_info:
                address = geocode_info.get('address')
                province = geocode_info.get('province')
                city = geocode_info.get('city')
                district = geocode_info.get('district')
                township = geocode_info.get('township')
            else:
                address = province = city = district = township = None
            
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')            
             # 插入到热力图表中
            insert_sql = f"""
                INSERT INTO ls_order_heatmap (
                    latlng, order_count, total_fee, location_type, 
                    address, province, city, district, township, created_at
                ) VALUES ('{latlng}', {order_count}, {total_fee}, '{location_type}','{address}', '{province}', '{city}', '{district}', '{township}', '{created_at}');
            """
            
            self.db._execute_sql(insert_sql)
            
        print("热力图数据已更新")
        return result
