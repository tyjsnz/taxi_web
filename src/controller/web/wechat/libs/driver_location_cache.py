# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file    :   driver_location_cache.py
@date    :   2025/05/19 00:00:48
@author  :   snz
@version :   1.0
@email   :   274043505@qq.com
@copyright:   Copyright (C) kmlskj All Rights Reserved.
@desc    :   Redis 缓存司机位置
注意： redis必须在3.2以上版本，windows下可使用7.4、8.0

'''
from loguru import logger
import redis
from datetime import datetime
import math

class DriverLocationCache:
    def __init__(self, city_id=0):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.key = f"driver_locations:{city_id}"
        self.redis_client.expire(self.key, 86400)  # 设置一天过期时间

    def update_driver_location(self, driver_id: int, lng: float, lat: float,company_id=0):
        """
        更新司机在 Redis 中的位置（默认行为：新增或更新）
        :param driver_id: 司机唯一标识
        :param lng: 经度
        :param lat: 纬度
        """
        try:
            # 默认允许新增或更新
            self.redis_client.geoadd(self.key, (lng, lat, str(driver_id)))
            
            self.redis_client.hset(f"driver_info:{driver_id}",mapping={
                "company_id": company_id,
                'lng': lng,
                'lat': lat
            })
            
            # 同时记录司机最后更新时间（用于过期判断）
            timestamp = datetime.now().timestamp()
            self.redis_client.zadd(f"{self.key}:last_update", {str(driver_id): timestamp})
        
            logger.info(f"司机 {driver_id} 位置已更新至 Redis")
        except Exception as e:
            logger.error(f"Redis 更新司机位置失败: {e}")

    def get_all_drivers(self):
        """
        获取所有司机的位置信息
        :return: 包含司机 ID 和位置的列表 [{'driver_id': 1, 'lng': xx.xxxx, 'lat': xx.xxxx}, ...]
        """
        try:
            driver_ids = []
            scan_cursor = 0
            while True:
                scan_cursor, members_with_scores = self.redis_client.zscan(f"{self.key}:last_update", cursor=scan_cursor)
                for member, _ in members_with_scores:
                    if isinstance(member, bytes):
                        driver_id = member.decode('utf-8')
                    else:
                        driver_id = member
                    driver_ids.append(driver_id)
                if scan_cursor == 0:
                    break

            drivers = []
            for driver_id in driver_ids:
                result = self.redis_client.geopos(self.key, driver_id)
                if result and result[0]:
                    lng, lat = result[0]
                    drivers.append({
                        'driver_id': driver_id,
                        'lng': float(lng),
                        'lat': float(lat)
                    })
            return drivers
        except Exception as e:
            logger.error(f"获取所有司机位置失败: {e}")
            return []
    def get_driver_position(self, driver_id: int):
        """
        获取司机当前的坐标
        :param driver_id: 司机ID
        :return: {'lat': xx.xxxx, 'lng': xx.xxxx}
        """
        try:
            result = self.redis_client.geopos(self.key, str(driver_id))
            if result and result[0]:
                return {
                    'lng': float(result[0][0]),
                    'lat': float(result[0][1])
                }
            return None
        except Exception as e:
            logger.error(f"获取司机位置失败: {e}")
            return None

    def int_ex(self,v):        
        try:
            v = int(v)
            if math.isnan(v) or math.isinf(v):
                return 0
            return v
        except:
            return 0

    def float_ex(self,v):
        try:
            v = float(v)
            if math.isnan(v) or math.isinf(v):
                return 0
            return v
        except:
            return 0
    def find_nearby_drivers(self, lng: float, lat: float, radius: float, unit='m'):
        """
        查找指定经纬度周围一定范围内的司机
        :param lng: 中心经度
        :param lat: 中心纬度
        :param radius: 搜索半径
        :param unit: 单位 m(米), km(千米), mi(英里), ft(英尺)
        :return: 包含司机 ID 和距离的列表 [{'driver_id': 1, 'distance': 500}, ...]
        """
        try:
            results = self.redis_client.georadius(
                self.key,
                lng, lat,
                radius,
                unit=unit,
                withdist=True,
                sort='ASC'
            )

            drivers = []
            for driver_id, distance in results:
                driver_id = driver_id.decode('utf-8') if isinstance(driver_id, bytes) else driver_id                
                #self.redis_client.hgetall(f"driver_info:{driver_id}")
                if driver_id == '':
                    continue
                
                cid = self.redis_client.hget(f"driver_info:{driver_id}","company_id")
                cid = cid.decode('utf-8') if cid else 0
                lat = self.redis_client.hget(f"driver_info:{driver_id}","lat")
                lat = lat.decode('utf-8') if lat else 0
                lat = round(self.float_ex(lat),6)
                lng = self.redis_client.hget(f"driver_info:{driver_id}","lng")
                lng = lng.decode('utf-8') if lng else 0
                lng = round(self.float_ex(lng),6)
                
                drivers.append({
                    'driver_id': (driver_id),
                    'distance': round(float(distance), 2),
                    'cid':  cid,
                    'lng': lng,
                    'lat': lat
                })

            return drivers

        except Exception as e:
            logger.error(f"Redis 查询附近司机失败: {e}")
            return []

    def remove_driver_location(self, driver_id: int):
        """
        移除司机位置信息（如司机下线）
        :param driver_id: 司机ID
        """
        try:
            self.redis_client.zrem(self.key, str(driver_id))
            logger.info(f"司机 {driver_id} 已从 Redis 删除")
        except Exception as e:
            logger.error(f"删除司机位置失败: {e}")


if __name__ == '__main__':
    cache = DriverLocationCache()

    print("查询司机位置:", cache.get_driver_position(2))
    # 第一次插入司机位置
    cache.update_driver_location(3, 102.730425, 25.079124)
    print("插入司机位置成功")

    # 再次更新司机位置（应该成功）
    cache.update_driver_location(2, 102.731425, 25.079224)
    print("司机位置更新成功")

    print("查询司机位置:", cache.get_driver_position(2))
    # 查询附近司机
    nearby = cache.find_nearby_drivers(116.4074, 39.9042, 5000)
    print("附近司机:", nearby)
    for row in nearby:
        print(row)
        print(f"ID={row['driver_id']}司机位置:", cache.get_driver_position(row["driver_id"]))

    # 删除司机位置
    #cache.remove_driver_location(1001)
    #cache.remove_driver_location(1002)
    print("司机位置已删除")