# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file    :   driver_find_libs.py
@date    :   2025/04/14 11:15:01
@author  :   snz
@version :   1.0
@email   :   274043505@qq.com
@copyright:   Copyright (C) kmlskj All Rights Reserved.
@desc    :   司机查找类,使用scheduler实现

'''
from apscheduler.schedulers.background import BackgroundScheduler
from src.model.driving.driver_location_db import DriverLocationDb
from src.model.order.order_db import OrderDb
from src.model.driving.driver_order_accept_db import DriverOrderAcceptDb
from src.model.driving.driver_db import DriverDb
from src.controller.web.wechat.libs.driver_location_cache import DriverLocationCache
from src.common.const_defined import *
from settings import DriverFindConfig, DatabaseConfig
from src.helper.geo_helper import *
from loguru import logger
import json
from src.helper.helper import *
import redis

# 注意helper中使用了import datetime，所以需要按如下导入，否则会报错datetime.now时
from datetime import datetime
#from src.libs.websocket_client.redis_client import publish_message

# 🟡 在类内部定义 Redis 连接信息
REDIS_HOST = DatabaseConfig.REDIS_HOST
REDIS_PORT = DatabaseConfig.REDIS_PORT
CHANNEL_NAME = 'websocket_messages'
class DriverFinder:
    def __init__(self, order_id, customer_openid,start_lat, start_lng,order_time,reject_driver_ids=None,company_ids='',start_location='',end_location='',end_lat='',end_lng=''):
        ''' 查找司机并通道司机及乘客
            Args:
                order_id: 订单ID
                customer_openid: 乘客openid标识
                start_lat: 起点纬度
                start_lng: 起点经度
                order_time: 订单下单时间
                reject_driver_ids: 拒绝司机ID列表
                company_ids: 所选打车的车辆所属于id列表, 1,2,3,4
                start_location: 起点位置
                end_location: 终点位置
                end_lat: 终点纬度
                end_lng: 终点经度
            Return: 
                None
            @date:   2025/05/04 10:59:53
            @author: snz
        '''
        
        self.order_id = order_id
        self.start_lat = round(float_ex(start_lat),6)
        self.start_lng = round(float_ex(start_lng),6)
        self.end_lat = round(float_ex(end_lat),6)
        self.end_lng = round(float_ex(end_lng),6)
        
        self.order_time = order_time
        self.target_token = customer_openid
        self.reject_driver_ids = reject_driver_ids
        self.company_ids = company_ids
        self.start_location = start_location
        self.end_location = end_location
                
        self.start_time = datetime.now()
        
        self.scheduler = BackgroundScheduler()
        self.driver_location = DriverLocationDb()
        self._db = OrderDb()
        self.driver_accept = DriverOrderAcceptDb()
        self.driver = DriverDb()
        self.job_id = f"find_driver_{order_id}"  # 为任务生成唯一 ID
        
        self.search_radius = DriverFindConfig.SEARCH_RADIUS
               
        # 乘客下单等待的超时，也是查找司机的超时时间
        self.timeout = DriverFindConfig.SEARCH_TIMEOUT
        
        # 取系统配置参数
        self.customer_config = get_current_customer_config()
        if "timeout" in self.customer_config:
            self.timeout = self.customer_config['timeout']            
        
        self.driver_config = get_current_driver_config()
        # 获取系统配置，查找范围米
        if self.driver_config and "order_dispatch_range" in self.driver_config:
            self.search_radius = self.driver_config['order_dispatch_range']
        
        self.interval = 1 #DriverFindConfig.DRIVER_FIND_INTERVAL  # 默认为1，第一次未找到时增加时间来查找，每次增加5秒
        # 多少分钟内司机的有效定位
        self.gps_expired_time = DriverFindConfig.DRIVER_GPS_EXPIRE_TIME
        self.task_running = True  # 标志位，控制任务是否继续运行
        
        # 默认关围栏功能    
        self.order_region_verify = 0
        if self.driver_config and "order_region_verify" in self.driver_config:
            self.order_region_verify = int_ex(self.driver_config['order_region_verify'])
            
        # 初始化 Redis 连接
        #self.redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        # 连接池
        pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
        self.redis_conn = redis.Redis(connection_pool=pool)
        self.channel = CHANNEL_NAME

        
        # 看订单是否为先付后乘
        row = self._db.get_order_by_id(self.order_id, 'order_type')
        # 是否为先付后乘1=是
        self.need_after_pay = row['order_type'] == ORDER_TYPE.PAY_AFTER_USE
        
        # 先删除先前抢单池中的此订单的司机抢单记录,以便于此订单重新找司机
        self.driver_accept.delete_order_by_order_id(self.order_id)
        
        # 司机缓存坐标
        self.driver_cache = DriverLocationCache()
        
    def check_point_in_region(self,company_id,lon,lat):
        """ 检查司机当前点是否在公司所在的指定区域中 """                
        sql = f"""
            SELECT id, company_id 
            FROM ls_company_map 
            WHERE ST_Contains(
                latlng, 
                ST_GeomFromText('POINT({lon} {lat})')
                AND company_id = {company_id}
            );
        """
        
        result = self.driver._query_sql(sql)

        if result:
            #return echo_json(0, '在围栏内', result)
            return True
        else:
            #return echo_json(1, '不在围栏内')
            logger.info(f"公司ID：{company_id},坐标：{lon},{lat}，不在围栏内")
            return False

    def _publish_redis_message(self, message: dict):
        """私有方法：向 Redis 发送消息"""
        try:
            msg = {'target_token': message['target_token'], 'data': message}
            self.redis_conn.publish(self.channel, json.dumps(msg))
            logger.debug(f"Published to Redis channel {self.channel}: {msg}")
        except Exception as e:
            logger.error(f"Redis publish failed: {e}")

    def find_drivers(self):
        """模拟查找司机的逻辑"""
        if not self.task_running:
            logger.info(f"任务 {self.job_id} 已被停止，退出查找逻辑")
            return
        
        # 检查订单状态，如果已经被取消或司机接单，则停止任务，接单后司机端自行处理接单消息至乘客端，服务端不作处理
        order_status = self._db.get_order_status(self.order_id)
        # 如果订单状态不是待接单或无司机且订单不是先付后乘，则停止任务
        if order_status not in [ORDER_STATUS.PENDING, ORDER_STATUS.NO_DRIVER] and not self.need_after_pay:
            self.interval = 1
            self.stop()
            return
        
        # 检查是否超时
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        if elapsed_time > self.timeout:
            # 超时处理
            self.notify_passenger_no_driver()
            self.stop()
            return

        # 查找周边司机
        drivers = self.query_nearby_drivers(self.start_lat, self.start_lng)
        if drivers:
            # 找到司机，通知乘客
            self.notify_passenger_with_driver(drivers)
            self.stop()
        else:
            # 增加查找时间，第1次为1秒，第2将增加5秒，以此类推
            if self.interval < 60:
                self.interval += 5
                self.update_job_interval(self.interval)

    def query_nearby_drivers(self, lat, lng):
        """查询周边司机"""
        
        logger.info(f"正在查找 {self.search_radius} 米范围内的司机...wxapp: {self.target_token}")
        
        # 这里调用数据库或缓存查询周边司机
        #results = self.driver_location.find_nearby_drivers(lng,lat, self.search_radius, self.gps_expired_time,self.reject_driver_ids,company_ids=self.company_ids)
        
        cids = None
        if self.company_ids != '':
            cids = self.company_ids.split(',')
            cids = [int(cid.strip()) for cid in cids]
            
        results = self.driver_cache.find_nearby_drivers(lng=lng,lat=lat,radius=self.search_radius,unit='m')
        logger.info(f"查询到的司机数量: {len(results)}")
        
        drivers = []
        if results is not None:
            for row in results:
                driver_id = int_ex(row['driver_id'])
                company_id = int_ex(row['cid'])
                
                # 开了电子围栏后，找到的司机位置是否在所在公司的电子围栏范围内，如不在，则不考虑
                if self.order_region_verify == 1:
                    is_in_region = self.check_point_in_region(company_id,row['lng'],row['lat'])
                    if is_in_region is not None:
                        # 不在电子围栏内，则不考虑
                        logger.info(f"司机ID：{driver_id},公司ID：{company_id},坐标：{row['lng']},{row['lat']}，不在电子围栏内")
                        if is_in_region is False:
                            continue
                
                                
                # 排除的司机ID
                logger.info(f"司机ID：{driver_id},公司ID：{company_id},坐标：{row['lng']},{row['lat']}，是否在排除列表中：{driver_id in self.reject_driver_ids}")
                if self.reject_driver_ids != '' and driver_id in self.reject_driver_ids:
                    continue
                
                # 符合公司ID， 司机不是用户选择的车型企业时，不考虑
                logger.info(f"司机ID：{driver_id},公司ID：{company_id},坐标：{row['lng']},{row['lat']}，是否用户所选的车辆公司ID：{company_id in cids}")
                if cids is not None:
                    if company_id not in cids:
                        continue                    
                
                info = self.driver.get_user_info_by_id(driver_id,'work_status,token,score,accept_order_status,company_id,today_online_total_time,accept_order_model,no_air,no_train,on_way_address')
                if info is None:
                    continue
                
                # 未在线或未工作的司机不考虑
                if info['work_status'] != DRIVER_WORK_STATUS.WORK_ON or info['accept_order_status'] == DRIVER_ACCEPT_ORDER_STATUS.YES_ACCEPT:                
                    continue
                # 是否为机场、火车站等特殊车型
                if "火车站" in self.start_location:
                    # 不接火车站订单的司机不考虑
                    if info['no_train'] == 1:
                        continue
                if "机场" in self.start_location:
                    # 不接机场订单的司机不考虑
                    if info['no_air'] == 1:
                        continue
                # 是否顺路单
                if info['on_way_address']:
                    _arr = info['on_way_address'].split('#')
                    if len(_arr) == 3:
                        _addr,_latlng,_ratio = _arr
                        # 计算出我设置的顺路位置与乘客目的地的距离
                        _distance,_duration = get_distance_by_amap(self.end_lng+','+self.end_lat, _latlng)
                        
                        _ratio = float_ex(_ratio) # 0.6或0.9
                        
                        # 计算顺路单的距离(1-0.6) * 2000
                        # 以2公里为基准，顺路单的距离
                        _ratio = (1 - _ratio) * 2000
                        if _distance > _ratio:
                            # 小于顺路单的距离
                            continue
                    
                score = info['score']

                drivers.append({
                    'token': info['token'],
                    'score': score,
                    'distance': row['distance'],
                    "driver_id": driver_id,
                    'accept_order_model': info['accept_order_model'], # 司机设置的接单模式
                    'today_online_total_time': info['today_online_total_time'], # 今日在线时长
                })

            dispatch_model = ''
            if drivers:
                # 按照当天在线时间降序排序，最长在线的司机排在前面
                drivers_sort = sorted(drivers, key=lambda x: x['today_online_total_time'],reverse=False)
                                
                if self.driver_config:
                    # 系统调度，取最近司机1名司机,如是自动派单，则所有司机都考虑
                    if self.driver_config['order_dispatch_flag'] == ORDER_DISPATCH.SYSTEM:
                        dispatch_model = '系统调度'
                        logger.info(f"系统调度，取最近1名开启了系统派单模式的司机")
                        # 取第1名司机,如果司机开启了系统派单模式
                        for drow in drivers_sort:
                            if drow['accept_order_model'] == ORDER_DISPATCH.SYSTEM:
                                drivers = [drow]
                                logger.info(f"系统调度，取最近1名开启了系统派单模式的司机，司机ID：{drow['driver_id']}")
                                break
                    else:
                        dispatch_model = '自动派单'
                        logger.info(f"自动派单，考虑所有司机")                        

                logger.info(f"找到司机：{drivers}, 派单模式：{dispatch_model}")
            else:
                logger.info(f"未能到司机：{self.target_token}")
                        
        msg = {'flag': 'search_driver', "target_token":self.target_token, 'order_id': self.order_id, 'msg': f"正在查找 {self.search_radius} 米范围内的司机...token: {self.target_token}"}
        #send_message_to_target_client(self.target_token, {'flag': 'search_driver', "target_token":self.target_token, 'order_id': self.order_id, 'msg': f"正在查找 {self.search_radius} 米范围内的司机...token: {self.target_token}"})
        #send_message_to_target_client('all',msg)
        #publish_message(message=msg)

        self._publish_redis_message(msg)
        return drivers  # 返回司机列表（如果找到）
        
    def notify_passenger_with_driver(self, drivers):
        """通知乘客找到司机"""
        logger.info(f"找到司机: {len(drivers)} 位,查询时间：{self.timeout}秒,查询半径：{self.search_radius}米")
        
        order_type_txt = '先乘后付'
        if self.need_after_pay:
            order_type_txt = '先付后乘，乘客已付款'
            
        # 发送消息给司机
        for driver in drivers:
            # 通过 WebSocket 通知司机接单
            # 插入司机接单记录
            _insert_id = self.driver_accept.insert_data({
                'order_id': self.order_id,
                'driver_id': driver['driver_id'],
                'send_time': self.order_time,
                'order_type_text': order_type_txt,
                'status': DRIVER_ACCEPT_STATUS.PENDING
            })
            msg = '实时订单'
            if self.driver_config['order_dispatch_flag'] == ORDER_DISPATCH.SYSTEM:
                msg = f"系统派单,请接单"
            # 司机token
            driver_token = driver['token']           
            ac_row = self._db._query_sql_one(f"select * from v_accept_order where accept_id={_insert_id}")
                            
            msg = {'flag':'find_driver','msg': msg,'accept_id':_insert_id,'order_id': self.order_id,'target_token': driver_token,'order': ac_row}            
            
            # 只有系统派单时才发接单信息，也只有一位司机能接单
            if self.driver_config:                
                if self.driver_config['order_dispatch_flag'] == ORDER_DISPATCH.SYSTEM:
                    self.build_order_to_driver(driver_token,_insert_id)
                    # 更新订单为系统派单订单，0=自动派单(默认)
                    self._db.update_order(self.order_id, {'is_dispatch': 1})
                else:
                    # 自动派单时都要发出去,各自到抢单中心看
                    self._publish_redis_message(msg)
            else:
                # 未设置时也发抢单数据
                #send_message_to_target_client(driver_token, msg)
                self._publish_redis_message(msg)
        
        num = len(drivers)
        # 发给乘客
        msg = {'flag': 'find_driver', "target_token":self.target_token,'order_id': self.order_id, 'num': num, 'msg': f"找到司机,待司机接单...token: {self.target_token}"}
        #send_message_to_target_client(self.target_token, msg)
        self._publish_redis_message(msg)

    def build_order_to_driver(self,driver_token,accept_id):
        """ 系统派单，发订单给司机，司机弹出来接单
        Args:
            : 
        Return:
            None
        @date:   2025/05/12 11:27:17
        @author: snz
            
        """
        result = self._db._query_sql_one(f"select * from v_accept_order where accept_id={accept_id}")
        if result is None: return
        
        total_fee = float_ex(result['total_fee'])
        cost = float_ex(result['cost'])
        # 系统派单时，还没有订单金额，因为不同公司接单的计费不同，所以这里使用预估的金额
        if total_fee == 0:
            total_fee = cost
            
        order_type = int_ex(result['order_type'])
        if order_type == 1:
            order_type = '先付后乘'
        else:
            order_type = '先乘后付'
                                            
        result_json = {
            'flag': 'find_driver',
            'target_token': driver_token,
            'msg': f"实时单,{result['start_location']}到{result['end_location']}",  # 语音播报
            'accept_id': result['accept_id'],
            'customer_id': result['customer_id'],
            'start_latlng': result['start_latlng'],
            'end_latlng': result['end_latlng'],
            'start_location': result['start_location'],
            'end_location': result['end_location'],
            'order_id': result['order_id'],
            'customer_token': result['openid'], # 乘客token现更换为openid
            'customer_phone': result['customer_phone'],
            'openid': result['openid'],
            'ev_price': result['ev_price'],
            'cost': cost,
            'total_fee': total_fee,
            'order_type': result['order_type'],
            'add_price': float_ex(result['add_price']),
            'distance': str(round(float_ex(result['distance']) / 1000, 2)) + "km",  # 转换为公里
            'duration': str(round(float_ex(result['duration']) / 60, 2)) + "分钟",  # 转换为分钟
        }
        
        #msg = json.dumps(result_json)
        #send_message_to_target_client(driver_token, msg)
        self._publish_redis_message(result_json)
    def notify_passenger_no_driver(self):
        """寻找已经超时通知乘客未找到司机"""
        
        logger.info(f"未找到司机，请重新尝试,查询时间：{self.timeout}秒,查询半径：{self.search_radius}米")
        
        # 当前无接单司机，此时反馈给乘客，让乘客重新发起请求（加价）
        self._db.update_order_status(self.order_id, ORDER_STATUS.NO_DRIVER)
        
        # 删除接单表中的订单记录，因为未找到司机
        self.driver_accept.delete_order_by_order_id(self.order_id)
        
        msg = {'flag': 'no_driver', "target_token":self.target_token, 'order_id': self.order_id, 'msg': f"未找到司机，请重新尝试..."}
        logger.info(f"target_token: {self.target_token},msg: {msg}")
        #send_message_to_target_client(self.target_token, {'flag': 'no_driver', "target_token":self.target_token, 'order_id': self.order_id, 'msg': f"未找到司机，请重新尝试..."})        
        self._publish_redis_message(msg)
    
    def update_job_interval(self, new_seconds):
        job = self.scheduler.get_job(self.job_id)
        if not job:
            logger.warning(f"任务 {self.job_id} 不存在，无法修改间隔")
            return

        try:
            self.scheduler.reschedule_job(
                job_id=self.job_id,
                trigger='interval',
                seconds=new_seconds
            )
            self.interval = new_seconds
            logger.info(f"任务 {self.job_id} 的执行间隔已修改为 {new_seconds} 秒")
        except Exception as e:
            logger.error(f"修改任务间隔失败: {e}")
        
    def stop(self):
        """停止任务"""
        self.task_running = False
        self.scheduler.remove_job(self.job_id)
        logger.info(f"任务 {self.job_id} 已停止,对应订单ID: {self.order_id}")
        
    def start(self):
        """启动定时任务"""
        if self.scheduler.get_job(self.job_id):
            logger.info(f"任务 {self.job_id} 已存在，跳过启动")
            return
        
        self.task_running = True
        logger.info(f"任务 {self.job_id} 已启动,对应订单ID: {self.order_id}")
        self.scheduler.add_job(
            self.find_drivers,
            'interval',
            seconds=self.interval,
            id=self.job_id
        )
        self.scheduler.start()
'''
# 示例调用
finder = DriverFinder(order_id=123, start_lat=24.013375, start_lng=102.162364, search_radius=5000)
finder.start()
'''