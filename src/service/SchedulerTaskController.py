# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file    :   SchedulerTaskController.py
@date    :   2025/05/21 17:48:15
@author  :   snz
@version :   1.0
@email   :   274043505@qq.com
@copyright:   Copyright (C) kmlskj All Rights Reserved.
@desc    :   定时任务调度器,定期任务要独立于flask应用运行

运行方式
nohup python SchedulerTaskController.py > scheduler.log 2>&1 &

'''
import sys
import os
# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（假设 src 是子目录）
project_root = os.path.dirname(os.path.dirname(current_dir))

# 将项目根目录添加到 PYTHONPATH
if project_root not in sys.path:
    sys.path.append(project_root)
    
from apscheduler.schedulers.background import BackgroundScheduler
from src.model.base_db import PublicDbConnection
from datetime import datetime as dt, timedelta
import time,json
from loguru import logger
from src.common.const_defined import COUPON_STATUS,ORDER_STATUS,DRIVER_WORK_STATUS
from src.helper.helper import *
from src.controller.web.wechat.libs.driver_location_cache import DriverLocationCache

def check_coupons_status():
    """ 检查优惠券状态
    Args:
        : 
    Return:
        None
    @date:   2025/04/18 20:28:05
    @author: snz
        
    """
    db = PublicDbConnection()
    sql = f"select id from ls_coupons where status = 0 and end_date < '{dt.now()}'"
    result = db._query_sql(sql,use_cache=False)
    if result is None:
        return
    
    for row in result:
        sql = f"update ls_coupons set status = -1 where id = {row['id']}"
        db._execute_sql(sql)
        # 更新用户领用表，设为过期
        sql = f"update ls_coupons_list set status = -1 where coupon_id = {row['id']}"
        db._execute_sql(sql)

def check_order_comment():
    """ 检测订单评价状态，如果评价时间超过7天，则默认好评
    Args:
        : 
    Return:
        None
    @date:   2025/04/18 20:36:13
    @author: snz
        
    """
    delay_time = 7
    default_review_score = 0
    db = PublicDbConnection()
    row = db._query_sql_one(f"select * from ls_sys_config limit 1")
    if row:
        if row['driver_config']:
            row['driver_config'] = json.loads(row['driver_config'])
            # 超时天数
            delay_time = row['driver_config']['default_review_delay']
            # 默认评价给多少分
            default_review_score = row['driver_config']['default_review_score']

    # 大于设定的天数，订单结束了，但未评价，这时默认好评            
    sql = f"""
    SELECT o.id,o.driver_id,o.customer_id,o.openid,o.score
        FROM ls_order o
        LEFT JOIN ls_order_rating r ON o.id = r.order_id
        WHERE o.status = {ORDER_STATUS.COMPLETED}
        AND o.updated_at < DATE_SUB(NOW(), INTERVAL {delay_time} DAY)
        AND r.id IS NULL;
    """
    result = db._query_sql(sql)
    if result is None:
        return
    # 查询给默认给好评价
    for row in result:
        data = {
            "order_id": row['id'],
            "driver_id": row['driver_id'],
            "score": default_review_score,
            "score": '系统默认好评',
            "remark":f'超时：{delay_time}天未评价，系统默认好评',
            "openid": row['openid'],
            "user_id": row['customer_id'],
            "created_at": get_current_time()
        }
        db.insert_data_by_dict("ls_order_rating",data)
        # 更新评价记录
        logs = {
            "order_id": row['id'],
            "driver_id": row['driver_id'],
            "score": default_review_score,
            "remark":f'超时：{delay_time}天未评价，系统默认好评',            
            "created_at": get_current_time()
        }
        db.insert_data_by_dict("ls_driver_score_log",logs)
        # 更新司机评价分数
        db.update_data_by_id("ls_driver",{"score": row['score'] + default_review_score},row['driver_id'])
        
def clean_expired_drivers():
    cache = DriverLocationCache()  # 初始化你的缓存类
    now =  dt.now().timestamp()
    five_minutes_ago = now - 300  # 5分钟前的时间戳

    # 获取所有超过5分钟未更新的司机
    expired_drivers = cache.redis_client.zrangebyscore(
        f"{cache.key}:last_update", 0, five_minutes_ago
    )
    if not expired_drivers or len(expired_drivers) == 0:
        logger.info("没有超时未更新的司机")
        return

    driver_db = PublicDbConnection()
    for driver_id in expired_drivers:
        driver_id = driver_id.decode('utf-8') if isinstance(driver_id, bytes) else driver_id
        # 从 GEO 和 ZSET 中删除司机
        cache.redis_client.zrem(cache.key, driver_id)
        cache.redis_client.zrem(f"{cache.key}:last_update", driver_id)
        logger.info(f"司机 {driver_id} 已被移除（超时未更新）")
        
        # 更新司机状态为离线
        driver_db.update_data_by_id("ls_driver",{"work_status": DRIVER_WORK_STATUS.WORK_OFF},driver_id)
        
def update_driver_work_status():
    """ 更新司机工作状态，5分钟内未更新位置的司机，工作状态改为下班状态
    Args:
        : 
    Return:
        None
    @date:   2025/04/18 20:36:13
    """
    db = PublicDbConnection()
    five_minutes_ago = datetime.datetime.now() - timedelta(minutes=5)
    sql = "SELECT driver_id FROM ls_driver_location WHERE updated_at < %s"
    result = db._query_sql(sql, (five_minutes_ago,))
    if result is None:
        return

    for row in result:
        driver_id = row['driver_id']
        db.update_data_by_id("ls_driver", {"work_status": DRIVER_WORK_STATUS.WORK_OFF}, driver_id)    
def total_hours_order_data():
    # 统计每小时订单数据，第小时统计一次
    from src.service.db.db_service import DBService
    db_service = DBService()
    db_service.total_hours_order_data()
    
def total_heatmap_data():
    # 每5分钟统计一次热力图数据
    from src.service.db.heatmap_service import HeatmapService
    heatmap_service = HeatmapService()
    result = heatmap_service.get_heatmap_data()
    
def start_scheduler():
    # 初始化 APScheduler
    scheduler = BackgroundScheduler()
    # minutes=10 , minute='*/3'
    # 5分钟检查一次优惠券过期状态
    scheduler.add_job(func=check_coupons_status, trigger="interval", minutes=5)
    
    # 每天午夜（00:00）运行一次 check_order_comment 任务
    scheduler.add_job(func=check_order_comment, trigger="cron", hour=0, minute=0)
    
    # 每分钟运行一次清理任务
    scheduler.add_job(clean_expired_drivers, 'interval', minutes=1)
        
    # 每5分钟统计一次热力图数据
    scheduler.add_job(func=total_heatmap_data, trigger="interval", minutes=5)
    
    # 每小时统计一次订单数据
    scheduler.add_job(func=total_hours_order_data, trigger="interval", hours=1)
    
    # 每5分钟更新司机工作状态
    scheduler.add_job(func=update_driver_work_status, trigger="interval", minutes=5)
    
    #scheduler.add_job(func=check_order_status, trigger="cron", minute='*/3')
    scheduler.start()
    
    # 启动后立即执行一次（可选）
    total_heatmap_data()
    total_hours_order_data()
    clean_expired_drivers()
    update_driver_work_status()
    
'''
# 每天上午 10:30 运行：
scheduler.add_job(func=check_order_comment, trigger="cron", hour=10, minute=30)
# 每天下午 3:45 运行：
scheduler.add_job(func=check_order_comment, trigger="cron", hour=15, minute=45)
'''

if __name__ == "__main__":
    try:
        start_scheduler()
        logger.info("定时任务已启动")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到退出信号，正在关闭定时任务...")
    except Exception as e:
        logger.error(f"发生致命错误：{e}")