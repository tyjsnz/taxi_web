# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

from src.helper.helper import *
from src.model.order.order_db import OrderDb
from src.model.common.taxi_fee_settings_db import TaxiFeeSettingsDb
from src.common.const_defined import *
from datetime import datetime

class PriceCalculateLibs:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        self._db = OrderDb()
        self._fee_setting = TaxiFeeSettingsDb()
    def calculate_order_fee(self, taxi_time, distance, duration_minutes, temporary_surcharge_coefficent=0, tolls=0, insurance_fee=0,is_wechat_calculate=True):
        """ 计算订单费用
            Args:
                tax_time: 打车时间
                distance: 距离
                duration_minutes: 预计用时(分钟)
                temporary_surcharge_coefficent: 临时加价系数百分比(1-100)
                tolls: 收费站收费情况
                insurance_fee: 保险费
                is_wechat_calculate: 是否微信端计算
            Return:
                None
            @date:   2025/03/21 17:00:00
            @author: snz
        """

        price_list = []
        #将字符串转换为datetime对象
        date_time_obj = datetime.strptime(taxi_time, '%Y-%m-%d %H:%M:%S')
        # 提取时间部分
        time_part = date_time_obj.time()

        distance = float(distance) / 1000
        result_list = self._fee_setting.get_taxi_fee_settings_by_starttime(time_part)

        for result in result_list:
            start_fee = float(result['start_fee'])
            start_mileage = float(result['start_mileage'])
            mileage_fee_per_km = float(result['mileage_fee_per_km'])
            long_distance_trigger_mileage = float(result['long_distance_trigger_mileage'])
            long_distance_fee_per_km = float(result['long_distance_fee_per_km'])
            duration_fee_per_minute = float(result['duration_fee_per_minute'])

            # 计算超出起步里程的里程数
            if distance > start_mileage:
                extra_mileage = distance - start_mileage
            else:
                extra_mileage = 0

            extra_mileage = float(extra_mileage)

            # 计算远途费
            if distance > long_distance_trigger_mileage:
                long_distance_fee = (distance - long_distance_trigger_mileage) * long_distance_fee_per_km
            else:
                long_distance_fee = 0
            long_distance_fee = float(long_distance_fee)

            # 假设时长为 0
            extra_duration_minutes = duration_minutes

            # 计算总费用
            total_fee = float(start_fee + (extra_mileage * mileage_fee_per_km) + (extra_duration_minutes * duration_fee_per_minute) + long_distance_fee)
            # 加价系数
            temporary_fee = total_fee + (total_fee * (temporary_surcharge_coefficent / 100))

            # 如有过路费情况，则加上代付的过路费
            total_fee = round(float(total_fee) + float(temporary_fee) + float(tolls) + float(insurance_fee),1)

            # 基础费用(超步价)
            base_fee = start_fee
            #里程费用 (起步里程费用 + 超出起步里程费用)
            km_fee = start_fee + (extra_mileage * mileage_fee_per_km)
            # 时长费用
            time_fee = (extra_duration_minutes * duration_fee_per_minute) + long_distance_fee

            details = {
                'start_fee': start_fee,
                'start_mileage': start_mileage,
                'mileage_fee_per_km': mileage_fee_per_km,
                'extra_mileage': extra_mileage,
                'duration_fee_per_minute': duration_fee_per_minute,
                'extra_duration_minutes': extra_duration_minutes,
                'long_distance_fee': long_distance_fee,
                'long_distance_trigger_mileage': long_distance_trigger_mileage,
                'temporary_surcharge': temporary_fee,
                'temporary_coefficent': temporary_surcharge_coefficent,
                'tolls': tolls,
                'insurance_fee': insurance_fee,
                'total_fee': total_fee,
                'created_at': get_current_time()
            }

            # 小程序计算，则只返回以下数据
            if is_wechat_calculate:
                # 只专计算好的费用回去，多了客户端用不到
                details = {
                    'company_id': result['company_id'],
                    'short_name': result['short_name'],
                    'base_fee': base_fee, # 基础费用(超步价)
                    'km_fee': km_fee, # 里程费用 (起步里程费用 + 超出起步里程费用)
                    'time_fee': time_fee, # 时长费用
                    'total_fee': total_fee, # 总费用
                    'created_at': get_current_time() # 创建时间
                }

            price_list.append(details)

        return price_list if len(price_list) > 0 else None
        
    def calculate_order_fee_by_companyid(self, company_id, taxi_time, distance, duration_minutes, temporary_surcharge_coefficent=0, tolls=0, insurance_fee=0,is_wechat_calculate=True):
        """ 计算订单费用，获取单条记录，用于订单被接单的所属公司的费用计算
            Args:
                company_id: 公司id
                tax_time: 打车时间
                distance: 距离
                duration_minutes: 预计用时(分钟)
                temporary_surcharge_coefficent: 临时加价系数百分比(1-100)
                tolls: 收费站收费情况
                insurance_fee: 保险费
                is_wechat_calculate: 是否微信端计算
            Return:
                None
            @date:   2025/03/21 17:00:00
            @author: snz
        """
        #将字符串转换为datetime对象
        date_time_obj = datetime.strptime(taxi_time, '%Y-%m-%d %H:%M:%S')
        # 提取时间部分
        time_part = date_time_obj.time()

        distance = float(distance) / 1000
        result = self._fee_setting.get_taxi_fee_settings_by_starttime_and_company_id(company_id,time_part)
        if result is None:
            return [None,None]
        if result:
            start_fee = float(result['start_fee'])
            start_mileage = float(result['start_mileage'])
            mileage_fee_per_km = float(result['mileage_fee_per_km'])
            long_distance_trigger_mileage = float(result['long_distance_trigger_mileage'])
            long_distance_fee_per_km = float(result['long_distance_fee_per_km'])
            duration_fee_per_minute = float(result['duration_fee_per_minute'])

            # 计算超出起步里程的里程数
            if distance > start_mileage:
                extra_mileage = distance - start_mileage
            else:
                extra_mileage = 0

            extra_mileage = float(extra_mileage)

            # 计算远途费
            if distance > long_distance_trigger_mileage:
                long_distance_fee = (distance - long_distance_trigger_mileage) * long_distance_fee_per_km
            else:
                long_distance_fee = 0
            long_distance_fee = float(long_distance_fee)

            # 假设时长为 0
            extra_duration_minutes = duration_minutes

            # 计算总费用
            total_fee = float(start_fee + (extra_mileage * mileage_fee_per_km) + (extra_duration_minutes * duration_fee_per_minute) + long_distance_fee)
            # 加价系数
            temporary_fee = total_fee + (total_fee * (temporary_surcharge_coefficent / 100))

            # 如有过路费情况，则加上代付的过路费
            total_fee = round(float(total_fee) + float(temporary_fee) + float(tolls) + float(insurance_fee),1)

            # 基础费用(超步价)
            base_fee = start_fee
            #里程费用 (起步里程费用 + 超出起步里程费用)
            km_fee = start_fee + (extra_mileage * mileage_fee_per_km)
            # 时长费用
            time_fee = (extra_duration_minutes * duration_fee_per_minute) + long_distance_fee
            
            details = {
                'start_fee': start_fee,
                'start_mileage': start_mileage,
                'mileage_fee_per_km': mileage_fee_per_km,
                'extra_mileage': extra_mileage,
                'duration_fee_per_minute': duration_fee_per_minute,
                'extra_duration_minutes': extra_duration_minutes,
                'long_distance_fee': long_distance_fee,
                'long_distance_trigger_mileage': long_distance_trigger_mileage,
                'temporary_surcharge': temporary_fee,
                'temporary_coefficent': temporary_surcharge_coefficent,
                'tolls': tolls,
                'insurance_fee': insurance_fee,
                'total_fee': total_fee,
                'created_at': get_current_time()
            }
            
            # 小程序计算，则只返回以下数据
            if is_wechat_calculate:
                # 只专计算好的费用回去，多了客户端用不到
                details = {
                    'company_id': result['company_id'],
                    'short_name': result['short_name'],
                    'base_fee': base_fee, # 基础费用(超步价)
                    'km_fee': km_fee, # 里程费用 (起步里程费用 + 超出起步里程费用)
                    'time_fee': time_fee, # 时长费用
                    'total_fee': total_fee, # 总费用
                    'created_at': get_current_time() # 创建时间
                }

            return [total_fee,details]