# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

'''
@file     :   websocket_client.py
@date     :   2025/05/24 11:32:19
@author   :   snz 
@version  :   1.0
@email    :   274043505@qq.com
@copyright:   kmlskj Co.,Ltd.
@desc     :   websocket客户端
'''

import json
import time
import threading
from typing import Optional
from websockets.sync.client import connect as sync_connect
import websockets


class WebSocketClient:
    def __init__(self, uri="ws://127.0.0.1:8080?client_id=flask_backend&token=your_secret_token"):
        self.uri = uri
        self.conn = None
        self.running = True
        self.heartbeat_interval = 30
        self.conn_lock = threading.RLock()  # 可重入锁
        self._start_monitor()
        self._connect()
        self._start_heartbeat()
        #self._start_message_receiver()  # 新增：启动下行消息监听线程
        #self.message_handlers = []

    def _start_monitor(self):
        """启动连接监控线程"""
        self.running = True
        threading.Thread(target=self.monitor_connection, daemon=True).start()

    def monitor_connection(self):
        """连接状态监控"""
        time.sleep(5)  # 每5秒检查一次
        while self.running:
            with self.conn_lock:
                if self._is_closed(self.conn):
                    print("监控检测到连接断开")
                    self._connect()
            time.sleep(5)  # 每5秒检查一次
    def _connect(self):
        """带详细错误处理的连接方法"""
        with self.conn_lock:
            try:
                if not self.running:
                    return False
                
                print(f"尝试连接到 {self.uri}...")
                
                # 添加连接超时和协议头
                self.conn = sync_connect(
                    self.uri,
                    open_timeout=5,       # 缩短超时时间
                    close_timeout=5,
                    ping_interval=60,
                    ping_timeout=60
                )
                
                print("连接成功且验证通过")
                self.running = True
                return True

            except websockets.exceptions.InvalidURI:
                print("错误：URI格式无效")
            except websockets.exceptions.InvalidHandshake:
                print("错误：握手失败（检查token/协议）")
            except ConnectionRefusedError:
                print("错误：连接被拒绝（服务未运行或端口错误）")
            except Exception as e:
                print(f"未知连接错误: {type(e).__name__}: {str(e)}")
            
            self.conn = None
            return False
    def _is_closed(self, conn):
        """精确可靠的连接状态检查"""
        if conn is None:
            return True
            
        # 优先检查已知的关闭状态属性
        if getattr(conn, 'closed', False):  # websockets库的标准属性
            return True
            
        # 检查底层传输状态（兼容不同版本）
        try:
            transport = getattr(conn, 'transport', None)
            if transport and getattr(transport, 'is_closing', lambda: False)():
                return True
        except Exception:
            pass  # 忽略检查过程中的异常

    def _heartbeat_loop(self):
        """安全的心跳线程"""
        while self.running:
            try:
                # 先快速检查连接状态（不加锁）
                if self.conn is None:
                    print("心跳检测到连接问题，准备重连...")
                    if not self._connect():  # 这个方法内部有锁
                        time.sleep(1)
                        continue

                # 实际心跳发送（加锁时间尽量短）
                with self.conn_lock:
                    if self._is_closed(self.conn):
                        continue
                    
                    try:
                        self.send({"flag": "ping"}, silent=True)
                        #print("心跳发送成功", time.strftime("%H:%M:%S"))
                    except:
                        pass

                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                print(f"心跳线程异常: {type(e).__name__}")
                time.sleep(1)

    def _start_heartbeat(self):
        """启动后台心跳线程"""
        self.running = True
        thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        thread.start()

    def send(self, data: dict, target: Optional[str] = None, silent=False):
        """线程安全的消息发送"""
        if not self.running:
            raise RuntimeError("客户端已关闭")

        message = data
        if target:
            message["target_token"] = target

        max_retries = 2
        for attempt in range(max_retries):
            try:
                # 加锁时间尽量短
                with self.conn_lock:
                    if self._is_closed(self.conn):
                        if not silent:
                            print("连接已断开，准备重连...")
                        if not self._connect():
                            continue
                    
                    self.conn.send(json.dumps(message))
                    if not silent:
                        print(f"发送成功: {message}")
                    return True

            except websockets.exceptions.ConnectionClosed as e:
                print(f"连接关闭 (代码: {e.code})")
                self.conn = None
            except Exception as e:
                print(f"发送异常: {type(e).__name__}")
                if attempt == max_retries - 1:
                    raise

        return False
    def send_msg(self, target_token: Optional[str], data: dict):
        """对外发送接口"""
        self.send(data, target_token)

    def close(self):
        """安全的关闭方法"""
        if not self.running:
            return

        self.running = False
        
        # 使用超时锁避免死锁
        lock_acquired = self.conn_lock.acquire(timeout=2)
        try:
            if self.conn and not self._quick_check_closed():
                try:
                    self.conn.close(code=1000)  # 正常关闭
                except:
                    pass
            self.conn = None
            print("客户端已安全关闭")
        finally:
            if lock_acquired:
                self.conn_lock.release()

    def _start_message_receiver(self):
        """启动下行消息监听线程"""
        thread = threading.Thread(target=self._message_receiver, daemon=True)
        thread.start()

    def _message_receiver(self):
        """下行消息监听线程"""
        while self.running:
            try:
                with self.conn_lock:
                    if self._is_closed(self.conn):
                        print("连接断开，等待重连后继续接收下行消息")
                        time.sleep(5)
                        continue
                    
                    try:
                        message = self.conn.recv(timeout=5)  # 设置超时避免阻塞
                        if message:
                            print(f"收到下行消息: {message}")
                            self._handle_received_message(message)
                    except websockets.exceptions.ConnectionClosed:
                        print("连接已关闭，准备重连...")
                        self._connect()
                    except TimeoutError as e:
                        print(f"接收下行消息超时: {type(e).__name__}: {e}")
            except Exception as e:
                print(f"下行消息线程异常: {type(e).__name__}: {e}")
                time.sleep(1)

    # def _handle_received_message(self, message: str):
    #     """处理接收到的消息"""
    #     try:
    #         if message == "pong":
    #             print("收到心跳响应")
    #             return
    #         data = json.loads(message)
    #         print("解析后的下行消息:", data)
            
    #         # 示例：转发回 Redis（可选）
    #         from redis_client import publish_message
    #         publish_message(channel="websocket_downstream", message={"type": "downstream", "data": data})
            
    #     except json.JSONDecodeError:
    #         print("无法解析下行消息为 JSON:", message)

    def register_handler(self, handler_func):
        """注册下行消息处理器"""
        pass
        #self.message_handlers.append(handler_func)

    def _handle_received_message(self, message: str):
        return
        """支持多个处理器的消息分发"""
        for handler in self.message_handlers:
            try:
                if message == "pong":
                    #print("收到心跳响应")
                    return
                handler(message)
            except Exception as e:
                print(f"下行消息处理器错误: {e}")