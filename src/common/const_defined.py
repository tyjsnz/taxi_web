# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   const_defined.py
@date     :   2025/03/09 15:01:42
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   公共常量定义
'''

class USER_TYPE:
    # 超级管理员
    ADMIN = 999 
    # 调度员
    DISPATCHER = 2
    # 代理商
    AGENT = 1
    # 普通用户
    NORMAL = 0 

class USER_STATUS:
    # 正常
    NORMAL = 0
    # -1:禁用
    DISABLE = -1
    # -9: 待审核（司机使用）
    NO_VERIFY = -9

class COMMISSION_SETTLE_STATUS:
    # 未结算
    NO_SETTLEMENT = 0
    # 已结算
    YES_SETTLEMENT = 1
    
class ORDER_STATUS:
    # 待接单
    PENDING = 0
    # 已接单
    ACCEPTED = 1
    # 乘客已上车
    PICKED_UP = 2
    # 行程进行中
    IN_PROGRESS = 3
    # 到达目的地，待支付
    ARRIVED_NO_PAY = 4
    # 已支付，订单结束
    COMPLETED = 5
    # 用户取消订单
    CANCELED = -1
    # 当前无司机接单
    NO_DRIVER = -2
    # 司机拒绝接单
    REJECTED = -3
    # 正在接乘客途中
    TO_PICKED_UP = 6

class ORDER_DISPATCH:
    # 系统派单（根据距离），司机必须接单，但可以拒绝，每日有拒绝限额
    SYSTEM = 0
    # 自动派单
    AUTO = 1
    
class ORDER_TYPE:
    # 0=先乘后付
    USE_AFTER_PAY = 0
    # 1=先付后乘
    PAY_AFTER_USE = 1
    
class DRIVER_WORK_STATUS:
    # 下班状态(不可接单)
    WORK_OFF = 0
    # 上班状态(可接单)
    WORK_ON = 1
    # 休息状态(不可接单)
    REST = 2
    
class DRIVER_ACCEPT_ORDER_STATUS:
    # 未在服务乘客状态
    NO_ACCEPT = 0
    # 已在服务乘客状态不可(接单状态)
    YES_ACCEPT = 1

class DRIVER_ACCEPT_STATUS:
    # 下发后当前未接单
    PENDING = 0
    # 拒绝接单
    REJECT_ACCEPT = -1
    # 订单超时无人接单
    TIMEOUT = -2
    # 乘客主动取消
    CANCELED = -3
    # 司机已接单
    ACCEPT = 1
    
    
class DRIVER_CASH_VERIFY_STATUS:
    # 提现审核
    # 未审核
    NO_VERIFY = 0
    # 审核中
    VERIFYING = 1
    # 已通过
    VERIFY_SUCCESS = 2
    # 已拒绝
    VERIFY_REJECT = 3
    # 已打款
    PAID = 4
   
class COUPON_TYPE:
    # 代金券
    CASH = 1
    # 满减
    DISCOUNT = 2
    # 拉新
    REFERRAL = 3
    
class COUPON_STATUS:
    # 未使用
    UNUSED = 0
    # 已使用
    USED = 1
    # 已过期
    EXPIRED = -1
    
class WECHAT_TEMPLATE_ID:
    # 司机接单提醒
    DRIVER_ACCEPT_ORDER = 'UcERJiF-4ifrFHFxuptqQKiK4K0MmXUYi-A5uPN3a5I',
    # 订单支付成功通知
    ORDER_PAY = 'Fs4vSXVa-3W2da_fim93QrfbUtH-WholPeYmO_JPTm0'