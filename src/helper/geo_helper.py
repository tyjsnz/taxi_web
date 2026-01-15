# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file    :   geo_helper.py
@date    :   2025/05/23 14:10:33
@author  :   snz
@version :   1.0
@email   :   274043505@qq.com
@copyright:   Copyright (C) kmlskj All Rights Reserved.
@desc    :   地理位置计算工具类

'''
import math
import requests

def calculate_cartesian(x1, y1, x2, y2):
    """计算平面坐标系中中的两点之间的距离，基于笛卡尔坐标系的几何距离计算方法
    Args:
        x1, y1: 第一个点的横坐标和纵坐标
        x2, y2: 第二个点的横坐标和纵坐标
    Returns:
        distance: 两点之间的距离（单位：米）
    """
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


def calculate_distance(
    lat1=102.731467, lon1=25.080998, lat2=102.732214, lon2=25.081639
):
    """计算两点之间的距离（单位：米）
    使用Haversine公式计算地球表面两点之间的距离
        Args:
            lat1, lon1: 第一个点的纬度、经度（度）
            lat2, lon2: 第二个点的纬度、经度（度）
        Returns:
            distance: 两点之间的距离（单位：米）
    """
    # 地球半径，单位：米
    R = 6371000

    # 将经纬度转换为弧度
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # 计算纬度差和经度差
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine公式
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    # print(f"两点间的距离约为 {distance:.2f} 米")
    return distance


def calculate_distance_time(distance, speed=30):
    """计算距离对应的时间（单位：秒）
    Args:
        distance: 距离（单位：米）
        speed: 速度（单位：公里/小时）
    Returns:
        time: 时间（单位：秒）
    """
    # 使用传入的速度计算时间
    time = distance / (speed * 1000 / 60)  # 转换为秒
    return time


def get_geocode_info(latlng):
    """调用高德地图反地理编码接口获取详细地址"""
    try:
        # 注意：高德API要求坐标格式是 "经度,纬度"
        lat, lng = str(latlng).split(",")
        location = f"{lng.strip()},{lat.strip()}"  # 转换为 lng,lat 格式
        API_KEY = '高德API key'
        url = f"https://restapi.amap.com/v3/geocode/regeo?key={API_KEY}&location={location}"
        response = requests.get(url, timeout=10)
        result = response.json()

        if result.get("status") == "1":
            regeocode = result.get("regeocode", {})
            address = regeocode.get("formatted_address")
            province = regeocode.get("addressComponent", {}).get("province")
            city = regeocode.get("addressComponent", {}).get("city")
            district = regeocode.get("addressComponent", {}).get("district")
            township = regeocode.get("addressComponent", {}).get("township")

            return {
                "address": address,
                "province": province,
                "city": city,
                "district": district,
                "township": township,
            }
    except Exception as e:
        print(f"[Error] 获取地理信息失败: {str(e)}")
        return None
    return None

def get_distance_by_amap(origin, destination, key='', mode=1):
    """
    调用高德地图API获取两点之间的实际距离
    
    Args:
        origin (str): 起点经纬度，格式为 "经度,纬度",6位小数点
        destination (str): 终点经纬度，格式为 "经度,纬度"
        key (str): 高德地图的 Web Service Key
        mode (int): 路径规划方式，默认为 1（驾车），可选 0直线距离，3（步行）

    Returns:
        array: [返回的距离（单位：米），返回的时间（单位：秒）]，如果失败则返回 None
    """
            
    url = f"https://restapi.amap.com/v3/distance?origin={origin}&destination={destination}&key={key}&type={mode}"

    response = requests.get(url)
    data = response.json()

    if data.get("status") == "1" and data.get("count") > 0:
        route = data["results"][0]
        distance = float(route["distance"])  # 返回单位是米
        duration = float(route["duration"])  # 返回单位是秒
        return [distance,duration]
    else:
        print("高德地图API调用失败:", data.get("info"))
        return None